#!/usr/bin/env python3
"""
🛡️ AI Guard — Interactive Zone Drawing Tool (OpenCV CLI)

Usage:
  python tools/zone_drawer.py [--source 0] [--output data/zones/default_zone.json]

Instructions:
  - Left-Click: Add polygon vertex
  - Right-Click: Undo last point
  - Press 'C': Close polygon loop
  - Press 'S': Save zone to JSON file and exit
  - Press 'R': Reset / clear points
  - Press 'Q' or 'ESC': Quit without saving
"""

import sys
import os
import cv2
import json
import argparse
import numpy as np
from pathlib import Path

# Add backend dir to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.utils.drawing import generate_test_pattern


def run_zone_drawer():
    parser = argparse.ArgumentParser(description="AI Guard Interactive Zone Drawer")
    parser.add_argument("--source", default="0", help="Camera source (0, RTSP URL, or video path)")
    parser.add_argument("--output", default="data/zones/default_zone.json", help="Output JSON path")
    parser.add_argument("--name", default="Restricted Zone", help="Name of the zone")
    args = parser.parse_args()

    source = int(args.source) if args.source.isdigit() else args.source
    output_path = Path(backend_dir / args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Initialize video capture
    print(f"\n[AI Guard] Opening camera source: {source}...")
    if isinstance(source, int):
        cap = cv2.VideoCapture(source, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(source)
    else:
        cap = cv2.VideoCapture(source)

    has_camera = cap.isOpened()
    if not has_camera:
        print("[AI Guard] Camera could not be opened. Using synthetic test frame for zone drawing.")

    points = []
    window_name = "AI Guard - Zone Polygon Drawer"
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

    def mouse_callback(event, x, y, flags, param):
        nonlocal points
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append((x, y))
            print(f" -> Point added: ({x}, {y})")
        elif event == cv2.EVENT_RBUTTONDOWN:
            if points:
                popped = points.pop()
                print(f" <- Point removed: {popped}")

    cv2.setMouseCallback(window_name, mouse_callback)

    print("\n" + "=" * 55)
    print(" 📍 AI GUARD INTERACTIVE ZONE DRAWER")
    print("=" * 55)
    print(" [Left Click]  : Add polygon point")
    print(" [Right Click] : Undo last point")
    print(" [S]           : Save zone polygon to file")
    print(" [R]           : Reset / Clear all points")
    print(" [Q / ESC]     : Exit")
    print("=" * 55 + "\n")

    while True:
        if has_camera:
            ret, frame = cap.read()
            if not ret or frame is None:
                frame = generate_test_pattern(1280, 720, message="CAMERA OFFLINE")
        else:
            frame = generate_test_pattern(1280, 720, message="DEFINE ZONE ON TEST CANVAS")

        h, w = frame.shape[:2]
        display = frame.copy()

        # Draw semi-transparent polygon fill if >= 3 points
        if len(points) >= 3:
            overlay = display.copy()
            pts_arr = np.array(points, dtype=np.int32)
            cv2.fillPoly(overlay, [pts_arr], (200, 150, 0))
            cv2.addWeighted(overlay, 0.3, display, 0.7, 0, display)

        # Draw polygon lines
        if len(points) >= 2:
            for i in range(len(points) - 1):
                cv2.line(display, points[i], points[i + 1], (0, 255, 255), 2, cv2.LINE_AA)
            if len(points) >= 3:
                cv2.line(display, points[-1], points[0], (0, 200, 255), 1, cv2.LINE_AA)

        # Draw points
        for i, pt in enumerate(points):
            cv2.circle(display, pt, 6, (0, 255, 255), -1, lineType=cv2.LINE_AA)
            cv2.circle(display, pt, 8, (255, 255, 255), 1, lineType=cv2.LINE_AA)
            cv2.putText(display, f"P{i+1}", (pt[0] + 8, pt[1] - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1, cv2.LINE_AA)

        # Draw top instruction overlay
        hud = display.copy()
        cv2.rectangle(hud, (0, 0), (w, 40), (20, 22, 28), -1)
        cv2.addWeighted(hud, 0.8, display, 0.2, 0, display)
        help_text = f"Points: {len(points)}  |  [Click] Add  |  [R] Reset  |  [S] Save ({len(points)} pts)  |  [Q] Exit"
        cv2.putText(display, help_text, (20, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 240, 255), 1, cv2.LINE_AA)

        cv2.imshow(window_name, display)
        key = cv2.waitKey(20) & 0xFF

        if key in (ord('q'), ord('Q'), 27):  # ESC or Q
            print("\n[AI Guard] Exiting without saving.")
            break
        elif key in (ord('r'), ord('R')):
            points = []
            print("\n[AI Guard] Points cleared.")
        elif key in (ord('s'), ord('S')):
            if len(points) < 3:
                print("\n⚠️ [AI Guard] You must define at least 3 points to create a zone polygon!")
            else:
                # Convert to normalized coordinates (0.0 to 1.0)
                norm_points = [[round(p[0] / w, 4), round(p[1] / h, 4)] for p in points]
                zone_data = {
                    "name": args.name,
                    "points": norm_points,
                    "is_normalized": True,
                    "color": "#EF4444",
                    "active": True
                }
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(zone_data, f, indent=2)
                print(f"\n✅ [AI Guard] Zone successfully saved to: {output_path}")
                print(f"Points saved: {norm_points}")
                break

    if has_camera:
        cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_zone_drawer()
