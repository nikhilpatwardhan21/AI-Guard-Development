import smtplib
import ssl
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from pathlib import Path
from typing import Optional
from app.config import settings

logger = logging.getLogger("ai_guard.email")


class EmailAlertService:
    """Dispatches real-time intrusion alert emails with attached camera frames."""

    def __init__(self):
        self.enabled = settings.email_enabled
        self.host = settings.smtp_host
        self.port = settings.smtp_port
        self.user = settings.smtp_user
        self.password = settings.smtp_password
        self.recipient = settings.alert_recipient

    def update_config(self, host: str, port: int, user: str, password: str, recipient: str, enabled: bool):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.recipient = recipient
        self.enabled = enabled

    def send_alert_email(
        self,
        alert_id: str,
        timestamp: str,
        zone_name: str,
        intruder_count: int,
        tracker_ids: list,
        screenshot_path: Optional[str] = None
    ) -> bool:
        """Sends an alert email synchronously (should be called in a background thread)."""
        if not self.enabled:
            logger.info(f"[Email Disabled] Alert #{alert_id} not emailed (email_enabled=False).")
            return False

        if not self.user or not self.password or not self.recipient:
            logger.warning(f"[Email Unconfigured] Missing SMTP credentials or recipient for alert #{alert_id}.")
            return False

        try:
            msg = MIMEMultipart("related")
            msg["Subject"] = f"🚨 [AI GUARD ALERT] Intruder Detected in {zone_name}!"
            msg["From"] = f"AI Guard Security <{self.user}>"
            msg["To"] = self.recipient

            # HTML Body
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #0d1117; color: #e6edf3; padding: 20px; }}
                    .card {{ background-color: #161b22; border: 1px solid #ff4444; border-radius: 8px; padding: 24px; max-width: 600px; margin: 0 auto; }}
                    .header {{ color: #ff5555; font-size: 22px; font-weight: bold; margin-bottom: 12px; }}
                    .info-row {{ margin: 8px 0; font-size: 14px; }}
                    .label {{ color: #8b949e; font-weight: 600; display: inline-block; width: 140px; }}
                    .value {{ color: #ffffff; font-weight: bold; }}
                    .screenshot {{ width: 100%; border-radius: 6px; margin-top: 16px; border: 1px solid #30363d; }}
                    .footer {{ margin-top: 20px; font-size: 12px; color: #8b949e; text-align: center; }}
                </style>
            </head>
            <body>
                <div class="card">
                    <div class="header">🚨 INTRUSION DETECTED</div>
                    <div class="info-row"><span class="label">Zone:</span> <span class="value">{zone_name}</span></div>
                    <div class="info-row"><span class="label">Time:</span> <span class="value">{timestamp}</span></div>
                    <div class="info-row"><span class="label">Intruders Count:</span> <span class="value">{intruder_count}</span></div>
                    <div class="info-row"><span class="label">Tracked Person IDs:</span> <span class="value">{tracker_ids}</span></div>
                    <div class="info-row"><span class="label">Alert ID:</span> <span class="value">#{alert_id}</span></div>
                    
                    {"<p><strong>Intrusion Frame Capture:</strong></p><img src='cid:screenshot' class='screenshot'/>" if screenshot_path and Path(screenshot_path).exists() else ""}
                    
                    <div class="footer">AI Guard Intelligent Surveillance System &bull; Real-time Computer Vision</div>
                </div>
            </body>
            </html>
            """

            msg_body = MIMEText(html_content, "html")
            msg.attach(msg_body)

            # Attach Screenshot as inline CID image
            if screenshot_path and Path(screenshot_path).exists():
                with open(screenshot_path, "rb") as img_file:
                    img_data = img_file.read()
                    image = MIMEImage(img_data)
                    image.add_header("Content-ID", "<screenshot>")
                    image.add_header("Content-Disposition", "inline", filename=f"intrusion_{alert_id}.jpg")
                    msg.attach(image)

            # SMTP Transport
            context = ssl.create_default_context()
            with smtplib.SMTP(self.host, self.port) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(self.user, self.password)
                server.sendmail(self.user, [self.recipient], msg.as_string())

            logger.info(f"Alert email successfully dispatched to {self.recipient} for alert #{alert_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False


email_service = EmailAlertService()
