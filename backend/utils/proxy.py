import os.path
import subprocess

import requests

import api.globals as g
from api.models import ChatGPTUser
from utils.logger import get_logger

config = g.config
logger = get_logger(__name__)


def run_reverse_proxy(chatgpt_users: list[ChatGPTUser]):
    if not config.get("chatgpt_paid", False):
        logger.error("You need a ChatGPT Plus account to use the reverse proxy!")
        logger.error(
            "Please set chatgpt_paid to true in config.yaml and restart the server."
        )
        exit(1)

    proxy_path = config.get("reverse_proxy_binary_path", None)
    if not proxy_path:
        logger.error("You need to set the reverse proxy binary path in config.yaml!")
        exit(1)

    # extract puids and access_tokens from chatgpt_users
    puids = []
    access_tokens = []
    for chatgpt_user in chatgpt_users:
        if chatgpt_user.is_active and chatgpt_user.is_plus:
            puids.append(chatgpt_user.puid)
            access_tokens.append(chatgpt_user.access_token)

    env_vars = {
        "PORT": str(config.get("reverse_proxy_port", 6060)),
        "ENABLE_PUID_AUTO_REFRESH": str(
            config.get("auto_refresh_reverse_proxy_puid", False)
        ).lower(),
    }
    if puids:
        env_vars["PUIDS"] = ",".join(puids)
    if access_tokens:
        env_vars["ACCESS_TOKENS"] = ",".join(access_tokens)

    g.reverse_proxy_log_file = open(
        os.path.join(config.get("log_dir", "logs"), "reverse_proxy.log"),
        "w",
        encoding="utf-8",
    )
    logger.debug(f"Reverse proxy binary path: {proxy_path}")
    g.reverse_proxy_process = subprocess.Popen(
        [proxy_path],
        env=env_vars,
        stdout=g.reverse_proxy_log_file,
        stderr=g.reverse_proxy_log_file,
    )
    logger.info("Reverse proxy started!")


def refresh_puid(email: str, access_token: str, puid: str):
    if not g.reverse_proxy_process:
        return

    logger.info(f"Refreshing puid for {email}.")
    response = requests.post(
        f"http://localhost:{config.get('reverse_proxy_port', 6060)}/refresh_puid",
        json={"access_token": access_token, "puid": puid},
    )
    if response.status_code != 200:
        logger.error(
            f"Error refreshing puid for {email} to {puid}: {response.text}"
        )
        return None
    else:
        response_json = response.json()
        puid = response_json["puid"]
        logger.info(f"Successfully refreshed puid for {email}.")
        return puid


def close_reverse_proxy():
    if g.reverse_proxy_process:
        g.reverse_proxy_process.kill()
        g.reverse_proxy_process = None
        g.reverse_proxy_log_file.close()
        g.reverse_proxy_log_file = None
        logger.info("Reverse proxy stopped.")
