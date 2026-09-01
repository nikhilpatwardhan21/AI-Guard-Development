import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

# Find project root and backend dir
BACKEND_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BACKEND_DIR.parent

# Load .env
env_path = BACKEND_DIR / ".env"
if not env_path.exists():
    env_path = ROOT_DIR / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseModel):
    # Camera
    camera_source: str = os.getenv("CAMERA_SOURCE", "0")
    camera_width: int = int(os.getenv("CAMERA_WIDTH", "1280"))
    camera_height: int = int(os.getenv("CAMERA_HEIGHT", "720"))
    camera_fps: int = int(os.getenv("CAMERA_FPS", "30"))

    # YOLO
    yolo_model: str = os.getenv("YOLO_MODEL", "yolov8n.pt")
    confidence_threshold: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.45"))
    iou_threshold: float = float(os.getenv("IOU_THRESHOLD", "0.5"))
    device: str = os.getenv("DEVICE", "cpu")

    # Paths
    zone_config_path: str = str(BACKEND_DIR / os.getenv("ZONE_CONFIG_PATH", "data/zones/default_zone.json"))
    screenshot_dir: str = str(BACKEND_DIR / os.getenv("SCREENSHOT_DIR", "data/alerts"))
    log_dir: str = str(BACKEND_DIR / "data/logs")
    save_screenshots: bool = os.getenv("SAVE_ALERT_SCREENSHOTS", "true").lower() in ("true", "1", "yes")

    # Alerts
    alert_cooldown_seconds: int = int(os.getenv("ALERT_COOLDOWN_SECONDS", "30"))

    # Email
    email_enabled: bool = os.getenv("EMAIL_ENABLED", "false").lower() in ("true", "1", "yes")
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    alert_recipient: str = os.getenv("ALERT_RECIPIENT", "")

    # Server
    backend_host: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    backend_port: int = int(os.getenv("BACKEND_PORT", "8000"))

    # Ensure required data directories exist
    def setup_directories(self):
        Path(self.screenshot_dir).mkdir(parents=True, exist_ok=True)
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)
        Path(self.zone_config_path).parent.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.setup_directories()
