import cv2
import time
import threading
import numpy as np
import logging
from typing import Optional, Tuple, Union
from app.utils.drawing import generate_test_pattern

logger = logging.getLogger("ai_guard.camera")


class CameraStream:
    """Threaded Video Stream capture for zero-latency real-time video processing."""

    def __init__(self, source: Union[str, int] = "0", width: int = 1280, height: int = 720, fps: int = 30):
        self.source_str = str(source)
        self.source = int(source) if str(source).isdigit() else source
        self.width = width
        self.height = height
        self.fps = fps

        self.cap: Optional[cv2.VideoCapture] = None
        self.current_frame: Optional[np.ndarray] = None
        self.is_running = False
        self.is_connected = False
        self.thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
        self.last_frame_time = 0.0
        self.actual_fps = 0.0

    def start(self) -> "CameraStream":
        """Starts the background acquisition thread."""
        if self.is_running:
            return self

        self.is_running = True
        self._init_capture()
        self.thread = threading.Thread(target=self._capture_loop, daemon=True, name="CameraCaptureThread")
        self.thread.start()
        logger.info(f"Camera stream thread started with source: {self.source}")
        return self

    def _init_capture(self):
        """Initializes cv2.VideoCapture with optimal buffer settings."""
        try:
            if self.cap is not None:
                self.cap.release()

            # On Windows, cv2.CAP_DSHOW or cv2.CAP_MSMF works well for webcams
            if isinstance(self.source, int):
                self.cap = cv2.VideoCapture(self.source, cv2.CAP_DSHOW)
                if not self.cap.isOpened():
                    self.cap = cv2.VideoCapture(self.source)
            else:
                self.cap = cv2.VideoCapture(self.source)

            if self.cap.isOpened():
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                self.cap.set(cv2.CAP_PROP_FPS, self.fps)
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimal buffer for zero latency
                self.is_connected = True
                logger.info(f"Camera opened successfully: {self.width}x{self.height} @ {self.fps}fps")
            else:
                self.is_connected = False
                logger.warning(f"Could not open camera source: {self.source}. Fallback test stream active.")
        except Exception as e:
            self.is_connected = False
            logger.error(f"Error initializing camera: {e}")

    def _capture_loop(self):
        """Continuous frame grabber thread."""
        reconnect_timer = 0
        frame_counter = 0
        fps_timer = time.time()

        while self.is_running:
            if self.is_connected and self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    now = time.time()
                    with self.lock:
                        self.current_frame = frame
                        self.last_frame_time = now

                    frame_counter += 1
                    if now - fps_timer >= 1.0:
                        self.actual_fps = frame_counter / (now - fps_timer)
                        frame_counter = 0
                        fps_timer = now
                else:
                    logger.warning("Camera read returned empty frame. Attempting reconnect...")
                    self.is_connected = False
                    time.sleep(0.5)
            else:
                # Fallback: create dynamic test pattern so downstream processing never starves
                test_card = generate_test_pattern(
                    self.width,
                    self.height,
                    message=f"STANDBY: Source '{self.source}' searching..."
                )
                with self.lock:
                    self.current_frame = test_card
                    self.last_frame_time = time.time()

                # Reconnect attempt every 3 seconds
                if time.time() - reconnect_timer > 3.0:
                    reconnect_timer = time.time()
                    self._init_capture()

                time.sleep(0.033)  # ~30 fps fallback

    def get_frame(self) -> Optional[np.ndarray]:
        """Returns a copy of the latest captured frame."""
        with self.lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
            return None

    def get_resolution(self) -> Tuple[int, int]:
        with self.lock:
            if self.current_frame is not None:
                h, w = self.current_frame.shape[:2]
                return (w, h)
            return (self.width, self.height)

    def reconfigure(self, new_source: Union[str, int]):
        """Switches the camera source dynamically."""
        self.source_str = str(new_source)
        self.source = int(new_source) if str(new_source).isdigit() else new_source
        self._init_capture()

    def stop(self):
        """Stops the capture thread and releases camera."""
        self.is_running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        if self.cap:
            self.cap.release()
        self.cap = None
        self.is_connected = False
        logger.info("Camera stream stopped.")
