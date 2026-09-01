import cv2
import numpy as np
import time
import math
from typing import Tuple, Optional


def hex_to_bgr(hex_str: str) -> Tuple[int, int, int]:
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 6:
        r = int(hex_str[0:2], 16)
        g = int(hex_str[2:4], 16)
        b = int(hex_str[4:6], 16)
        return (b, g, r)
    return (0, 0, 255)


def draw_zone(
    frame: np.ndarray,
    polygon_pts: np.ndarray,
    is_intruded: bool = False,
    zone_name: str = "RESTRICTED ZONE",
    alpha: float = 0.25
) -> np.ndarray:
    """Draws a stylish semi-transparent polygon zone with glowing border and status tag."""
    if len(polygon_pts) < 3:
        return frame

    overlay = frame.copy()
    h, w = frame.shape[:2]

    # Color selection: Neon Red/Amber when intruded, Neon Cyan/Green when secure
    if is_intruded:
        fill_color = (20, 20, 220)       # Red BGR
        border_color = (0, 50, 255)      # Bright Red BGR
        status_text = f"🚨 {zone_name} - INTRUDER DETECTED"
    else:
        fill_color = (200, 150, 0)       # Cyan/Blue tint BGR
        border_color = (255, 200, 0)     # Neon Cyan BGR
        status_text = f"🛡️ {zone_name} - ARMED"

    # Fill polygon
    cv2.fillPoly(overlay, [polygon_pts], fill_color)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    # Draw polygon perimeter line
    cv2.polylines(frame, [polygon_pts], isClosed=True, color=border_color, thickness=2, lineType=cv2.LINE_AA)

    # Draw small circle at vertices
    for pt in polygon_pts:
        cv2.circle(frame, tuple(pt), 4, border_color, -1, lineType=cv2.LINE_AA)
        cv2.circle(frame, tuple(pt), 6, (255, 255, 255), 1, lineType=cv2.LINE_AA)

    # Place badge near topmost point
    top_pt = min(polygon_pts, key=lambda p: p[1])
    badge_x = max(10, min(top_pt[0] - 20, w - 240))
    badge_y = max(30, top_pt[1] - 10)

    # Draw badge background
    (tw, th), _ = cv2.getTextSize(status_text, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
    cv2.rectangle(
        frame,
        (badge_x - 6, badge_y - th - 6),
        (badge_x + tw + 6, badge_y + 4),
        (15, 15, 18),
        -1
    )
    cv2.rectangle(
        frame,
        (badge_x - 6, badge_y - th - 6),
        (badge_x + tw + 6, badge_y + 4),
        border_color,
        1
    )
    cv2.putText(
        frame,
        status_text,
        (badge_x, badge_y - 2),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (255, 255, 255),
        1,
        cv2.LINE_AA
    )

    return frame


def draw_detections(
    frame: np.ndarray,
    boxes: np.ndarray,
    tracker_ids: Optional[np.ndarray] = None,
    confidences: Optional[np.ndarray] = None,
    intruder_mask: Optional[np.ndarray] = None
) -> np.ndarray:
    """Draws sleek bounding boxes, tracker ID tags, confidence, and bottom anchor point."""
    if boxes is None or len(boxes) == 0:
        return frame

    for i, box in enumerate(boxes):
        x1, y1, x2, y2 = map(int, box)
        is_intruder = bool(intruder_mask[i]) if intruder_mask is not None and i < len(intruder_mask) else False

        # Color: Alert Red if in zone, Electric Green/Cyan if outside zone
        if is_intruder:
            color = (0, 0, 240)       # Red
            tag_color = (0, 0, 180)
            status_label = "INTRUDER"
        else:
            color = (0, 220, 100)     # Emerald Green
            tag_color = (0, 160, 70)
            status_label = "PERSON"

        # Bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2, lineType=cv2.LINE_AA)

        # Corner accents for tactical security look
        corner_len = min(20, (x2 - x1) // 4, (y2 - y1) // 4)
        thickness = 3
        # Top-left
        cv2.line(frame, (x1, y1), (x1 + corner_len, y1), (255, 255, 255), thickness)
        cv2.line(frame, (x1, y1), (x1, y1 + corner_len), (255, 255, 255), thickness)
        # Top-right
        cv2.line(frame, (x2, y1), (x2 - corner_len, y1), (255, 255, 255), thickness)
        cv2.line(frame, (x2, y1), (x2, y1 + corner_len), (255, 255, 255), thickness)
        # Bottom-left
        cv2.line(frame, (x1, y2), (x1 + corner_len, y2), (255, 255, 255), thickness)
        cv2.line(frame, (x1, y2), (x1, y2 - corner_len), (255, 255, 255), thickness)
        # Bottom-right
        cv2.line(frame, (x2, y2), (x2 - corner_len, y2), (255, 255, 255), thickness)
        cv2.line(frame, (x2, y2), (x2, y2 - corner_len), (255, 255, 255), thickness)

        # Feet anchor point (bottom center - what triggers the zone)
        anchor_x = int((x1 + x2) / 2)
        anchor_y = y2
        cv2.circle(frame, (anchor_x, anchor_y), 5, color, -1, lineType=cv2.LINE_AA)
        cv2.circle(frame, (anchor_x, anchor_y), 7, (255, 255, 255), 1, lineType=cv2.LINE_AA)

        # Label construction
        trk_id_str = f"ID:#{tracker_ids[i]} " if tracker_ids is not None and i < len(tracker_ids) and tracker_ids[i] is not None else ""
        conf_str = f" {int(confidences[i] * 100)}%" if confidences is not None and i < len(confidences) and confidences[i] is not None else ""
        label = f"{trk_id_str}{status_label}{conf_str}"

        # Draw tag above box
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
        tag_y = max(y1 - 6, th + 6)
        cv2.rectangle(frame, (x1, tag_y - th - 6), (x1 + tw + 10, tag_y + 4), tag_color, -1)
        cv2.rectangle(frame, (x1, tag_y - th - 6), (x1 + tw + 10, tag_y + 4), color, 1)
        cv2.putText(frame, label, (x1 + 5, tag_y - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

    return frame


def draw_hud(
    frame: np.ndarray,
    fps: float,
    person_count: int,
    intruder_count: int,
    camera_label: str = "LIVE FEED"
) -> np.ndarray:
    """Draws top HUD overlay with FPS, status, and intruder count banner."""
    h, w = frame.shape[:2]

    # Top overlay banner
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 36), (15, 17, 23), -1)
    cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)
    cv2.line(frame, (0, 36), (w, 36), (50, 60, 75), 1)

    # Live indicator (pulsing red dot)
    pulse = (int(time.time() * 3) % 2) == 0
    dot_color = (0, 0, 255) if pulse else (0, 0, 160)
    cv2.circle(frame, (18, 18), 6, dot_color, -1, lineType=cv2.LINE_AA)
    cv2.putText(frame, f"GUARD AI  |  {camera_label}", (32, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (240, 240, 240), 1, cv2.LINE_AA)

    # Right side HUD stats
    hud_text = f"FPS: {fps:.1f}  |  TRACKED: {person_count}"
    (tw, th), _ = cv2.getTextSize(hud_text, cv2.FONT_HERSHEY_SIMPLEX, 0.42, 1)
    cv2.putText(frame, hud_text, (w - tw - 15, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (200, 220, 240), 1, cv2.LINE_AA)

    # Bottom Alert Banner if intruder detected
    if intruder_count > 0:
        alert_h = 44
        alert_overlay = frame.copy()
        cv2.rectangle(alert_overlay, (0, h - alert_h), (w, h), (0, 0, 180), -1)
        cv2.addWeighted(alert_overlay, 0.85, frame, 0.15, 0, frame)
        cv2.line(frame, (0, h - alert_h), (w, h - alert_h), (0, 0, 255), 2)

        alert_msg = f"⚠️ INTRUSION ALERT: {intruder_count} PERSON(S) IN RESTRICTED ZONE"
        (atw, ath), _ = cv2.getTextSize(alert_msg, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
        cv2.putText(frame, alert_msg, ((w - atw) // 2, h - 14), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2, cv2.LINE_AA)

        # Flashing red perimeter border
        if pulse:
            cv2.rectangle(frame, (0, 0), (w - 1, h - 1), (0, 0, 255), 4)

    return frame


def generate_test_pattern(width: int = 1280, height: int = 720, message: str = "CAMERA CONNECTING...") -> np.ndarray:
    """Generates a high-tech synthetic CCTV test card when camera is offline or initializing."""
    frame = np.zeros((height, width, 3), dtype=np.uint8)

    # Grid background
    grid_size = 40
    for x in range(0, width, grid_size):
        cv2.line(frame, (x, 0), (x, height), (25, 28, 36), 1)
    for y in range(0, height, grid_size):
        cv2.line(frame, (0, y), (width, y), (25, 28, 36), 1)

    # Center circle radar animation
    cx, cy = width // 2, height // 2
    angle = (time.time() * 2) % (2 * math.pi)
    cv2.circle(frame, (cx, cy), 120, (40, 50, 65), 1, cv2.LINE_AA)
    cv2.circle(frame, (cx, cy), 80, (40, 50, 65), 1, cv2.LINE_AA)
    cv2.circle(frame, (cx, cy), 40, (40, 50, 65), 1, cv2.LINE_AA)

    # Sweeping radar line
    rx = int(cx + 120 * math.cos(angle))
    ry = int(cy + 120 * math.sin(angle))
    cv2.line(frame, (cx, cy), (rx, ry), (0, 200, 255), 2, cv2.LINE_AA)

    # Title & Status
    title = "AI GUARD SURVEILLANCE FEED"
    (tw, _), _ = cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
    cv2.putText(frame, title, ((width - tw) // 2, cy - 150), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 220, 255), 2, cv2.LINE_AA)

    (mw, _), _ = cv2.getTextSize(message, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
    cv2.putText(frame, message, ((width - mw) // 2, cy + 160), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 190, 210), 1, cv2.LINE_AA)

    time_str = time.strftime("%Y-%m-%d %H:%M:%S UTC")
    cv2.putText(frame, time_str, (30, height - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 120, 140), 1, cv2.LINE_AA)

    return frame
