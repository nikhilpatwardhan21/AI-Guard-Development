import smtplib
import ssl
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from pathlib import Path
from typing import Optional, List
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
        tracker_ids: List[int],
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
            # Professional, non-spammy subject line
            msg["Subject"] = f"Security Advisory: Person Detected in {zone_name} [{alert_id}]"
            msg["From"] = f"AI Guard Security System <{self.user}>"
            msg["To"] = self.recipient

            formatted_ids = ", ".join(f"#{tid}" for tid in tracker_ids) if tracker_ids else "N/A"
            person_text = f"{intruder_count} Person" if intruder_count == 1 else f"{intruder_count} People"

            # Enterprise Professional HTML Template
            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>AI Guard Security Notification</title>
                <style>
                    body {{
                        margin: 0;
                        padding: 0;
                        background-color: #f4f6f9;
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                        color: #1f2937;
                        -webkit-font-smoothing: antialiased;
                    }}
                    .wrapper {{
                        width: 100%;
                        table-layout: fixed;
                        background-color: #f4f6f9;
                        padding: 30px 0;
                    }}
                    .main-card {{
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: #ffffff;
                        border-radius: 12px;
                        border: 1px solid #e5e7eb;
                        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
                        overflow: hidden;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                        padding: 24px 32px;
                        color: #ffffff;
                    }}
                    .header-top {{
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                        margin-bottom: 8px;
                    }}
                    .brand-title {{
                        font-size: 18px;
                        font-weight: 700;
                        letter-spacing: -0.01em;
                        color: #ffffff;
                        margin: 0;
                    }}
                    .badge-alert {{
                        display: inline-block;
                        background-color: #ef4444;
                        color: #ffffff;
                        font-size: 11px;
                        font-weight: 700;
                        padding: 4px 10px;
                        border-radius: 20px;
                        text-transform: uppercase;
                        letter-spacing: 0.05em;
                    }}
                    .header-subtitle {{
                        font-size: 13px;
                        color: #94a3b8;
                        margin: 0;
                    }}
                    .content {{
                        padding: 28px 32px;
                    }}
                    .alert-summary {{
                        font-size: 14px;
                        line-height: 1.6;
                        color: #374151;
                        margin-bottom: 24px;
                        padding-bottom: 16px;
                        border-bottom: 1px solid #f3f4f6;
                    }}
                    .meta-table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin-bottom: 24px;
                        background-color: #f8fafc;
                        border-radius: 8px;
                        overflow: hidden;
                        border: 1px solid #edf2f7;
                    }}
                    .meta-table td {{
                        padding: 12px 16px;
                        font-size: 13px;
                        border-bottom: 1px solid #edf2f7;
                    }}
                    .meta-table tr:last-child td {{
                        border-bottom: none;
                    }}
                    .meta-label {{
                        font-weight: 600;
                        color: #64748b;
                        width: 40%;
                    }}
                    .meta-val {{
                        font-weight: 600;
                        color: #0f172a;
                    }}
                    .evidence-title {{
                        font-size: 14px;
                        font-weight: 700;
                        color: #0f172a;
                        margin: 20px 0 10px 0;
                    }}
                    .image-container {{
                        background-color: #0f172a;
                        border-radius: 8px;
                        overflow: hidden;
                        border: 1px solid #e2e8f0;
                        text-align: center;
                    }}
                    .screenshot {{
                        width: 100%;
                        height: auto;
                        display: block;
                    }}
                    .cta-section {{
                        margin-top: 28px;
                        text-align: center;
                    }}
                    .cta-button {{
                        display: inline-block;
                        background-color: #0284c7;
                        color: #ffffff;
                        text-decoration: none;
                        font-size: 13px;
                        font-weight: 600;
                        padding: 11px 24px;
                        border-radius: 6px;
                    }}
                    .footer {{
                        padding: 20px 32px;
                        background-color: #f8fafc;
                        border-top: 1px solid #e5e7eb;
                        text-align: center;
                        font-size: 12px;
                        color: #6b7280;
                        line-height: 1.5;
                    }}
                </style>
            </head>
            <body>
                <div class="wrapper">
                    <div class="main-card">
                        <!-- Header -->
                        <div class="header">
                            <table style="width: 100%;" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td>
                                        <div class="brand-title">AI GUARD SURVEILLANCE</div>
                                        <div class="header-subtitle">Computer Vision Security Advisory</div>
                                    </td>
                                    <td style="text-align: right;">
                                        <span class="badge-alert">Zone Breach</span>
                                    </td>
                                </tr>
                            </table>
                        </div>

                        <!-- Content Body -->
                        <div class="content">
                            <p class="alert-summary">
                                An unauthorized presence was detected within the defined boundary of <strong>{zone_name}</strong> at <strong>{timestamp}</strong>. Event telemetry and video evidence are recorded below.
                            </p>

                            <!-- Incident Metadata Table -->
                            <table class="meta-table" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td class="meta-label">Location / Zone</td>
                                    <td class="meta-val">{zone_name}</td>
                                </tr>
                                <tr>
                                    <td class="meta-label">Detection Timestamp</td>
                                    <td class="meta-val">{timestamp}</td>
                                </tr>
                                <tr>
                                    <td class="meta-label">Individuals Detected</td>
                                    <td class="meta-val">{person_text}</td>
                                </tr>
                                <tr>
                                    <td class="meta-label">Tracked Object IDs</td>
                                    <td class="meta-val" style="font-family: monospace;">{formatted_ids}</td>
                                </tr>
                                <tr>
                                    <td class="meta-label">Incident Reference</td>
                                    <td class="meta-val" style="font-family: monospace; color: #475569;">#{alert_id}</td>
                                </tr>
                            </table>

                            <!-- Evidence Image Capture -->
                            {"<div class='evidence-title'>Captured Video Evidence</div><div class='image-container'><img src='cid:screenshot' class='screenshot' alt='Intrusion Evidence Frame'/></div>" if screenshot_path and Path(screenshot_path).exists() else ""}

                            <!-- Dashboard Link -->
                            <div class="cta-section">
                                <a href="http://localhost:5173" class="cta-button">Open Security Dashboard</a>
                            </div>
                        </div>

                        <!-- Footer -->
                        <div class="footer">
                            <div>AI Guard Intelligent Vision Engine &bull; YOLOv8 + ByteTrack</div>
                            <div style="margin-top: 4px; font-size: 11px; color: #9ca3af;">
                                This is an automated advisory dispatched according to your monitored zone policy.
                            </div>
                        </div>
                    </div>
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
                    image.add_header("Content-Disposition", "inline", filename=f"incident_{alert_id}.jpg")
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
