import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.api.routes import router as api_router
from app.api.websocket import ws_manager
from app.services.stream_service import pipeline_service
from app.core.alert_manager import alert_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ai_guard.main")


async def telemetry_broadcast_loop():
    """Periodically broadcasts system telemetry (FPS, detected persons, intruders) to WebSocket clients."""
    while True:
        try:
            status = pipeline_service.get_system_status()
            await ws_manager.broadcast_json("SYSTEM_STATUS", status.model_dump())
        except Exception as e:
            logger.error(f"Error in telemetry loop: {e}")
        await asyncio.sleep(0.5)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing AI Guard Core Services...")
    pipeline_service.start()
    alert_manager.set_broadcast_callback(ws_manager.sync_broadcast_alert)
    telemetry_task = asyncio.create_task(telemetry_broadcast_loop())
    logger.info("AI Guard Server is LIVE and ready.")

    yield

    # Shutdown
    logger.info("Shutting down AI Guard Services...")
    telemetry_task.cancel()
    pipeline_service.stop()
    logger.info("AI Guard Server shutdown complete.")


app = FastAPI(
    title="AI Guard - Real-Time Zone Intrusion Detection",
    version="1.0.0",
    description="Intelligent computer vision surveillance system with YOLOv8, ByteTrack, PolygonZone monitoring, and real-time alerts.",
    lifespan=lifespan
)

# CORS middleware for React / Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(api_router)


# WebSocket for real-time alerts and telemetry
@app.websocket("/ws/alerts")
async def websocket_alerts_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and receive any client ping
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.warning(f"WebSocket exception: {e}")
        ws_manager.disconnect(websocket)


# Mount static screenshot directory
screenshot_dir = Path(settings.screenshot_dir)
screenshot_dir.mkdir(parents=True, exist_ok=True)
app.mount("/alerts/media", StaticFiles(directory=str(screenshot_dir)), name="alert_screenshots")


@app.get("/")
def root_status():
    return {
        "system": "AI Guard 🛡️📹",
        "status": "Online",
        "endpoints": {
            "docs": "/docs",
            "stream": "/api/stream",
            "status": "/api/status",
            "alerts": "/api/alerts",
            "zone": "/api/zone",
            "ws": "/ws/alerts"
        }
    }
