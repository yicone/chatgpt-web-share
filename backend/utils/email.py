from fastapi_mail import ConnectionConfig
from fastapi_mail import MessageSchema, FastMail

import api.globals as g

config = g.config

conf = ConnectionConfig(
    MAIL_USERNAME=config.get("mail_username"),
    MAIL_PASSWORD=config.get("mail_password"),
    MAIL_FROM=config.get("mail_from"),
    MAIL_FROM_NAME=config.get("mail_from_name"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    MAIL_DEBUG=1,
)


async def send_activation_email(email: str, token: str):
    message = MessageSchema(
        subject="Account activation",
        subtype="plain",
        recipients=[email],
        body=f"Please click the following link to activate your account: {config.get('base_url')}/auth/verify/{token}",
    )
    fm = FastMail(conf)
    await fm.send_message(message)
