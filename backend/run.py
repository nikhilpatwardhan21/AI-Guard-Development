#!/usr/bin/env python3
"""
🛡️ AI Guard — FastAPI Backend Server Launcher
"""

import sys
import uvicorn
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app.config import settings

if __name__ == "__main__":
    banner = f"""
============================================================
  🛡️  AI GUARD — REAL-TIME ZONE INTRUSION DETECTION SYSTEM
============================================================
  - API Server    : http://{settings.backend_host}:{settings.backend_port}
  - API Docs      : http://localhost:{settings.backend_port}/docs
  - MJPEG Stream  : http://localhost:{settings.backend_port}/api/stream
  - WebSocket     : ws://localhost:{settings.backend_port}/ws/alerts
  - Model         : {settings.yolo_model}
  - Camera Source : {settings.camera_source}
============================================================
"""
    print(banner)
    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=False,
        log_level="info"
    )
