#!/usr/bin/env python3
"""
AI Guard — Camera Device Scanner
Tests and lists all connected webcam indices (0, 1, 2, 3...) on your system.
"""

import cv2


def scan_cameras(max_tested: int = 5):
    print("\n" + "=" * 55)
    print(" [AI GUARD] CONNECTED CAMERA SCANNER")
    print("=" * 55)
    available_cameras = []

    for idx in range(max_tested):
        cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(idx)

        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                h, w = frame.shape[:2]
                available_cameras.append((idx, w, h))
                print(f" [+] Found Camera Index [{idx}]: Resolution {w}x{h}")
            cap.release()

    print("=" * 55)
    if available_cameras:
        print(f"\nAvailable Camera Indices: {[c[0] for c in available_cameras]}")
        print("  - Index 0: Built-in Webcam")
        print("  - Index 1 (or higher): External USB Webcam\n")
    else:
        print("\n[-] No physical webcams detected. (Fallback test card will be active)\n")


if __name__ == "__main__":
    scan_cameras()
