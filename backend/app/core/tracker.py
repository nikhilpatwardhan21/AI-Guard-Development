import logging
import supervision as sv

logger = logging.getLogger("ai_guard.tracker")


class PersonTracker:
    """ByteTrack wrapper for multi-person tracking across video frames."""

    def __init__(self, track_activation_threshold: float = 0.25, lost_track_buffer: int = 30):
        self.tracker = sv.ByteTrack(
            track_activation_threshold=track_activation_threshold,
            lost_track_buffer=lost_track_buffer
        )
        logger.info("ByteTrack initialized.")

    def update(self, detections: sv.Detections) -> sv.Detections:
        """Updates detections with persistent tracker_ids."""
        if len(detections) == 0:
            return detections

        try:
            tracked_detections = self.tracker.update_with_detections(detections)
            return tracked_detections
        except Exception as e:
            logger.error(f"Tracker update error: {e}")
            return detections

    def reset(self):
        """Resets tracker state."""
        self.tracker.reset()
        logger.info("Tracker reset.")
