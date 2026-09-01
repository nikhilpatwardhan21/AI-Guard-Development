import cv2
import time
import logging
import asyncio
import numpy as np
from datetime import datetime
from typing import Optional, AsyncGenerator

from app.config import settings
from app.core.camera import CameraStream
from app.core.detector import PersonDetector
from app.core.tracker import PersonTracker
from app.core.zone_monitor import ZoneMonitor
from app.core.alert_manager import alert_manager
from app.utils.drawing import draw_zone, draw_detections, draw_hud
from app.models.schemas import SystemStatus

logger = logging.getLogger("ai_guard.stream_service")


class VideoPipelineService:
    """End-to-End Vision Pipeline: Frame Capture -> YOLO Detection -> ByteTrack -> Zone Check -> MJPEG Stream."""

    def __init__(self):
        self.camera = CameraStream(
            source=settings.camera_source,
            width=settings.camera_width,
            height=settings.camera_height,
            fps=settings.camera_fps
        )
        self.detector = PersonDetector(
            model_name=settings.yolo_model,
            confidence=settings.confidence_threshold,
            device=settings.device
        )
        self.tracker = PersonTracker()
        self.zone_monitor = ZoneMonitor(config_path=settings.zone_config_path)

        # Performance & HUD tracking
        self.fps: float = 0.0
        self.frame_count: int = 0
        self.last_fps_time: float = time.time()
        self.total_persons: int = 0
        self.intruders_count: int = 0
        self.active_tracker_ids: list = []
        self.latest_annotated_jpeg: Optional[bytes] = None

    def start(self):
        """Starts background camera capture."""
        self.camera.start()
        logger.info("Video Pipeline service started.")

    def stop(self):
        """Stops camera stream."""
        self.camera.stop()
        logger.info("Video Pipeline service stopped.")

    def process_next_frame(self) -> Optional[np.ndarray]:
        """Runs single frame through the detection & annotation pipeline."""
        frame = self.camera.get_frame()
        if frame is None:
            return None

        h, w = frame.shape[:2]

        # 1. YOLOv8 Person Detection
        raw_detections = self.detector.detect(frame)

        # 2. Multi-object tracking (ByteTrack)
        tracked_detections = self.tracker.update(raw_detections)

        # 3. Zone intrusion checking
        is_intruded, intruder_mask, intruding_ids = self.zone_monitor.check_intrusion(
            tracked_detections,
            (h, w)
        )

        # 4. Extract active tracker IDs & counts
        self.total_persons = len(tracked_detections)
        self.intruders_count = len(intruding_ids)
        if tracked_detections.tracker_id is not None:
            self.active_tracker_ids = [
                int(tid) for tid in tracked_detections.tracker_id
                if tid is not None
            ]
        else:
            self.active_tracker_ids = []

        # 5. Visual Annotations
        annotated = frame.copy()

        # Draw Restricted Zone
        if self.zone_monitor.is_active and len(self.zone_monitor.points) >= 3:
            zone_pts = self.zone_monitor.get_display_polygon(w, h)
            annotated = draw_zone(
                annotated,
                zone_pts,
                is_intruded=is_intruded,
                zone_name=self.zone_monitor.name
            )

        # Draw Person Bounding Boxes & Tags
        if len(tracked_detections) > 0:
            annotated = draw_detections(
                annotated,
                boxes=tracked_detections.xyxy,
                tracker_ids=tracked_detections.tracker_id,
                confidences=tracked_detections.confidence,
                intruder_mask=intruder_mask
            )

        # Draw Top HUD and Bottom Intrusion Alert Banner
        annotated = draw_hud(
            annotated,
            fps=self.fps,
            person_count=self.total_persons,
            intruder_count=self.intruders_count,
            camera_label=f"SRC: {self.camera.source_str}"
        )

        # 6. Check & Trigger Alert (Screenshot, Log, Notification)
        if is_intruded and self.intruders_count > 0:
            alert_manager.process_intrusion(
                annotated_frame=annotated,
                zone_name=self.zone_monitor.name,
                intruder_count=self.intruders_count,
                intruding_ids=intruding_ids
            )

        # 7. Update FPS calculation
        self.frame_count += 1
        now = time.time()
        if now - self.last_fps_time >= 1.0:
            self.fps = self.frame_count / (now - self.last_fps_time)
            self.frame_count = 0
            self.last_fps_time = now

        return annotated

    def get_latest_jpeg(self) -> Optional[bytes]:
        frame = self.process_next_frame()
        if frame is not None:
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if ret:
                return buffer.tobytes()
        return None

    async def generate_mjpeg_stream(self) -> AsyncGenerator[bytes, None]:
        """Yields MJPEG stream chunks for direct browser viewing."""
        while True:
            # Process in thread to avoid blocking FastAPI async event loop
            frame = await asyncio.to_thread(self.process_next_frame)
            if frame is not None:
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                if ret:
                    jpeg_bytes = buffer.tobytes()
                    yield (
                        b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + jpeg_bytes + b'\r\n'
                    )
            await asyncio.sleep(0.02)  # Cap loop to ~45 FPS max

    def get_system_status(self) -> SystemStatus:
        return SystemStatus(
            camera_active=self.camera.is_connected,
            detector_active=self.detector.model is not None,
            current_fps=round(self.fps, 1),
            total_persons_detected=self.total_persons,
            zone_intruders_count=self.intruders_count,
            active_tracker_ids=self.active_tracker_ids,
            zone_active=self.zone_monitor.is_active,
            email_alerts_enabled=settings.email_enabled,
            system_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )


pipeline_service = VideoPipelineService()
