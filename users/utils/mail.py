import os

from fastapi import BackgroundTasks
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from pydantic import EmailStr

from .auth import create_access_token

conf = ConnectionConfig(
    MAIL_USERNAME=os.environ.get("EMAIL_HOST"),
    MAIL_PASSWORD=os.environ.get("EMAIL_PASSWORD"),
    MAIL_FROM=os.environ.get("EMAIL_HOST"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_SSL_TLS=False,
    MAIL_STARTTLS=True
)

async def send_mail(
        email: EmailStr,
        email_template: str,
        subject: str,
        backgroundtasks: BackgroundTasks
    ) -> None:
    """
    Function to send mail with verification or reset link.
    Args:
        email: string with email address
        email_template: HTML file with a template for email which will be sent to user.
        subject: subject of the email which will be sent to user.
        backgroundtasks: instance of BackgroundTasks class.
    """
    token = await create_access_token({"sub": email})
    with open(f"users/email_templates/{email_template}.html", "r") as file:
        template = file.read().format(token=token)

    message = MessageSchema(
        subject=subject,
        recipients=[email],
        body=template,
        subtype="html"
    )

    fm = FastMail(conf)
    backgroundtasks.add_task(fm.send_message, message)
