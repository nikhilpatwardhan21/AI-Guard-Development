import logging
import numpy as np
from typing import Optional
from ultralytics import YOLO
import supervision as sv

logger = logging.getLogger("ai_guard.detector")


class PersonDetector:
    """YOLOv8 Person Detection Engine."""

    PERSON_CLASS_ID = 0  # COCO class 0 is 'person'

    def __init__(self, model_name: str = "yolov8n.pt", confidence: float = 0.45, device: str = "cpu"):
        self.model_name = model_name
        self.confidence = confidence
        self.device = device
        self.model: Optional[YOLO] = None
        self._load_model()

    def _load_model(self):
        try:
            logger.info(f"Loading YOLO model '{self.model_name}' on device '{self.device}'...")
            self.model = YOLO(self.model_name)
            logger.info("YOLO model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            raise

    def detect(self, frame: np.ndarray) -> sv.Detections:
        """Runs YOLO inference and filters for person detections."""
        if self.model is None or frame is None:
            return sv.Detections.empty()

        try:
            results_list = list(self.model(
                frame,
                conf=self.confidence,
                classes=[self.PERSON_CLASS_ID],
                device=self.device,
                verbose=False
            ))
            if not results_list:
                return sv.Detections.empty()

            results = results_list[0]
            detections = sv.Detections.from_ultralytics(results)
            return detections
        except Exception as e:
            logger.error(f"Error during detection inference: {e}")
            return sv.Detections.empty()

    def update_confidence(self, new_conf: float):
        self.confidence = max(0.1, min(0.99, new_conf))
        logger.info(f"Updated detection confidence threshold to {self.confidence:.2f}")
