from email.message import EmailMessage

import aiosmtplib

from src.config import settings


class EmailService:
    async def send_verification_code(self, email_to: str, code: str):
        message = EmailMessage()
        message["From"] = settings.EMAILS_FROM_EMAIL
        message["To"] = email_to
        message["Subject"] = f"Your Satzwerk Verification Code: {code}"

        message.set_content(
            f"Welcome to Satzwerk! Your 6 digit verification code is {code}\n"
            f"This code will expire in 15 minutes."
        )

        message.add_alternative(
            f"""
            <html>
                <body style="font-family: sans-serif; padding: 20px">
                    <h2>Welcome to Satzwerk</h2>
                    <p>Enter the code below to confirm your email address:</p>
                    <div style="font-size: 28px; font-weight: bold; letter-spacing: 4px; padding: 12px; background: #f4f4f4; display: inline-block;">
                        {code}
                    </div>
                    <p style="color: #666; font-size: 12px; margin-top: 16px;">This code expires in 15 minutes.</p>
                </body>
            </html>
            """,
            subtype="html",
        )

        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            use_tls=False,
        )

    async def send_password_reset_email(self, email_to: str, link: str):

        message = EmailMessage()

        message["Subject"] = "Reset Your Password"
        message["From"] = settings.EMAILS_FROM_EMAIL
        message["To"] = email_to

        message.set_content(
            f"Click the link to reset your password: {link}", subtype="html"
        )

        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            use_tls=False,
        )


email_service = EmailService()
