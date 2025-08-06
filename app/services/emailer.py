import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from ..config import Config

def send_email(to_email: str, subject: str, html_body: str):
    if not (Config.SMTP_USERNAME and Config.SMTP_APP_PASSWORD and Config.SMTP_FROM):
        raise RuntimeError("SMTP config missing. Set SMTP_* env vars.")
    
    # Replace non-breaking spaces and ensure UTF-8 friendly content
    html_body = html_body.replace("\xa0", " ")

    # Create UTF-8 MIME email
    msg = MIMEText(html_body, "html", "utf-8")
    msg["Subject"] = subject
    msg["From"] = formataddr((Config.SMTP_SENDER_NAME, Config.SMTP_FROM))
    msg["To"] = to_email

    with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT) as server:
        server.starttls()
        server.login(Config.SMTP_USERNAME, Config.SMTP_APP_PASSWORD)
        server.send_message(msg)
