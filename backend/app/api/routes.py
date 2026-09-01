import cv2
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import StreamingResponse, FileResponse

from app.config import settings
from app.models.schemas import ZoneConfig, IntrusionAlert, SystemStatus, SettingsUpdate
from app.services.stream_service import pipeline_service
from app.core.alert_manager import alert_manager
from app.services.email_service import email_service

router = APIRouter(prefix="/api", tags=["AI Guard API"])


@router.get("/stream")
async def get_live_stream():
    """Live MJPEG video stream with real-time YOLO bounding boxes, zone overlay & HUD."""
    return StreamingResponse(
        pipeline_service.generate_mjpeg_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@router.get("/snapshot")
async def get_current_snapshot(annotated: bool = Query(True, description="Whether to include bounding boxes")):
    """Returns a single JPEG image frame of current camera view."""
    if annotated:
        frame_bytes = pipeline_service.get_latest_jpeg()
    else:
        frame = pipeline_service.camera.get_frame()
        if frame is not None:
            _, buffer = cv2.imencode('.jpg', frame, (int(cv2.IMWRITE_JPEG_QUALITY), 85))
            frame_bytes = buffer.tobytes()
        else:
            frame_bytes = None

    if frame_bytes is None:
        raise HTTPException(status_code=503, detail="Camera frame unavailable")

    return Response(content=frame_bytes, media_type="image/jpeg")


@router.get("/status", response_model=SystemStatus)
async def get_system_status():
    """Returns real-time system health, FPS, and detection telemetry."""
    return pipeline_service.get_system_status()


@router.get("/alerts", response_model=List[IntrusionAlert])
async def get_alert_history(limit: int = Query(50, ge=1, le=200)):
    """Returns recent intrusion alerts with screenshot links."""
    return alert_manager.get_alerts(limit=limit)


@router.get("/alerts/{alert_id}/screenshot")
async def get_alert_screenshot(alert_id: str):
    """Fetches full-resolution screenshot captured during an intrusion."""
    # Sanitize and validate input to prevent path traversal
    if not alert_id or not alert_id.replace('-', '').replace('_', '').isalnum():
        raise HTTPException(status_code=400, detail="Invalid alert ID format")

    screenshot_dir = Path(settings.screenshot_dir).resolve()
    file_path = (screenshot_dir / f"{alert_id}.jpg").resolve()

    # Ensure path stays within screenshot directory
    try:
        file_path.relative_to(screenshot_dir)
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Alert screenshot not found")
    return FileResponse(file_path, media_type="image/jpeg")


@router.delete("/alerts")
async def clear_alerts():
    """Clears all intrusion alert records from memory and disk."""
    alert_manager.clear_alerts()
    return {"status": "success", "message": "Alert history cleared"}


@router.get("/zone", response_model=ZoneConfig)
async def get_zone_config():
    """Returns current restricted polygon zone definition."""
    zm = pipeline_service.zone_monitor
    return ZoneConfig(
        name=zm.name,
        points=zm.points,
        is_normalized=zm.is_normalized,
        color=zm.color,
        active=zm.is_active
    )


@router.post("/zone")
async def update_zone_config(config: ZoneConfig):
    """Updates and activates new polygon coordinates for the restricted zone."""
    if len(config.points) < 3:
        raise HTTPException(status_code=400, detail="Zone polygon must contain at least 3 points")

    pipeline_service.zone_monitor.update_zone(
        points=config.points,
        is_normalized=config.is_normalized,
        name=config.name,
        active=config.active
    )
    return {"status": "success", "message": f"Zone '{config.name}' updated successfully"}


@router.post("/settings")
async def update_settings(update: SettingsUpdate):
    """Updates runtime parameters (confidence threshold, cooldown, camera source, email alert toggle)."""
    if update.confidence_threshold is not None:
        pipeline_service.detector.update_confidence(update.confidence_threshold)

    if update.alert_cooldown_seconds is not None:
        alert_manager.update_cooldown(update.alert_cooldown_seconds)

    if update.camera_source is not None and update.camera_source != pipeline_service.camera.source_str:
        pipeline_service.camera.reconfigure(update.camera_source)

    if update.email_enabled is not None:
        email_service.enabled = update.email_enabled
        settings.email_enabled = update.email_enabled

    if update.alert_recipient is not None:
        email_service.recipient = update.alert_recipient
        settings.alert_recipient = update.alert_recipient

    return {"status": "success", "message": "Settings updated"}


@router.post("/test-alert")
async def trigger_test_alert():
    """Manually triggers a test intrusion alert to verify dashboard notifications and email delivery."""
    frame = pipeline_service.camera.get_frame()
    if frame is None:
        raise HTTPException(status_code=503, detail="Camera unavailable for test capture")

    alert = alert_manager.process_intrusion(
        annotated_frame=frame,
        zone_name=pipeline_service.zone_monitor.name + " (TEST)",
        intruder_count=1,
        intruding_ids=[999]
    )

    if alert:
        return {"status": "success", "alert": alert.model_dump()}
    else:
        return {"status": "cooldown", "message": "Alert throttled by cooldown timer. Try again shortly."}
