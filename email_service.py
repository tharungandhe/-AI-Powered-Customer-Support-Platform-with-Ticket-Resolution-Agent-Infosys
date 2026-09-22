import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv

class EmailService:
    def __init__(self):
        load_dotenv(override=True)

    def send_email(
        self,
        recipient,
        subject,
        body
    ):
        email = os.getenv("SMTP_EMAIL")
        password = os.getenv("SMTP_PASSWORD")
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))

        if not email or not password:
            return {
                "success": False,
                "message": "SMTP configuration missing"
            }

        if email == "support@example.com":
            return {
                "success": True,
                "message": "Email sent successfully (Simulated)"
            }

        message = MIMEMultipart()
        message["From"] = email
        message["To"] = recipient
        message["Subject"] = subject
        
        message.attach(
            MIMEText(body, "plain")
        )

        try:
            server = smtplib.SMTP(
                smtp_server,
                smtp_port
            )
            server.starttls()
            server.login(
                email,
                password
            )
            
            server.sendmail(
                email,
                recipient,
                message.as_string()
            )
            server.quit()
            
            return {
                "success": True,
                "message": "Email sent successfully"
            }
        except Exception as error:
            return {
                "success": False,
                "message": str(error)
            }
