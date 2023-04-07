from fastapi_mail import ConnectionConfig
from fastapi_mail import MessageSchema, FastMail

import api.globals as g
config = g.config

conf = ConnectionConfig(
    MAIL_USERNAME=config.get("email_username"),
    MAIL_PASSWORD=config.get("email_password"),
    MAIL_FROM="noreply@sharegpt.vip",
    MAIL_FROM_NAME="ShareGPT",
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
        body=f"Please click the following link to activate your account: http://localhost:8000/auth/verify/{token}",
    )
    fm = FastMail(conf)
    await fm.send_message(message)
