#!/usr/bin/env python3
"""
AI Guard — SMTP Email Verification Utility
Usage:
  python tools/test_email.py
"""

import sys
import numpy as np
import cv2
from datetime import datetime
from pathlib import Path

# Add backend dir to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.config import settings
from app.services.email_service import email_service


def test_email_dispatch():
    print("\n" + "=" * 60)
    print(" [AI GUARD] GMAIL SMTP EMAIL DISPATCH TEST")
    print("=" * 60)
    print(f" - Email Enabled   : {settings.email_enabled}")
    print(f" - SMTP Host       : {settings.smtp_host}:{settings.smtp_port}")
    print(f" - Sender Email    : {settings.smtp_user or '[NOT SET]'}")
    print(f" - Recipient Email : {settings.alert_recipient or '[NOT SET]'}")
    print("=" * 60)

    if not settings.smtp_user or not settings.smtp_password or not settings.alert_recipient:
        print("\n[!] SMTP credentials not configured in 'backend/.env'")
        return

    # Create synthetic test frame
    test_img = np.zeros((720, 1280, 3), dtype=np.uint8)
    cv2.rectangle(test_img, (100, 100), (1180, 620), (0, 0, 200), 3)
    cv2.putText(test_img, "AI GUARD SURVEILLANCE TEST CAPTURE", (120, 360), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

    test_screenshot = str(Path(settings.screenshot_dir) / "test_email_sample.jpg")
    Path(settings.screenshot_dir).mkdir(parents=True, exist_ok=True)
    cv2.imwrite(test_screenshot, test_img)

    print("\n[AI Guard] Connecting to smtp.gmail.com and sending test alert email...")
    email_service.enabled = True
    email_service.user = settings.smtp_user
    email_service.password = settings.smtp_password
    email_service.recipient = settings.alert_recipient

    current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    success = email_service.send_alert_email(
        alert_id="TEST-001",
        timestamp=current_time_str,
        zone_name="Restricted Zone",
        intruder_count=1,
        tracker_ids=[99],
        screenshot_path=test_screenshot
    )

    # Clean up temporary sample file
    if Path(test_screenshot).exists():
        Path(test_screenshot).unlink(missing_ok=True)

    if success:
        print(f"\n[+] SUCCESS! Alert email delivered to: {settings.alert_recipient}")
    else:
        print(f"\n[-] FAILED to authenticate or send email.")
        print("Note: Google requires a 16-character App Password rather than your primary account password.")
        print("Generate one at: https://myaccount.google.com/apppasswords\n")


if __name__ == "__main__":
    test_email_dispatch()
