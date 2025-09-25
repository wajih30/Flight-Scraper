import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")

if not all([SMTP_USER, SMTP_PASS]):
    raise ValueError("SMTP_USER and SMTP_PASS must be set in the .env file")

def send_alert(subject: str, body: str, recipient: str):
    """Send an email alert with the given subject and body."""
    msg = EmailMessage()
    msg["From"] = SMTP_USER
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body)

    # Connect securely to SMTP server
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.ehlo()              # identify ourselves
        server.starttls()          # secure the connection
        server.ehlo()              # re-identify after STARTTLS
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        print(f"✅ Email sent to {recipient}")


if __name__ == "__main__":
    subject = "✈️ Flight Alert Test"
    body = "This is a test email to confirm that your emailer.py is working."
    recipient = SMTP_USER  # send to yourself
    send_alert(subject, body, recipient)