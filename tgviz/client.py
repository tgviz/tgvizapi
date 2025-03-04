import httpx
import sys
import platform
from pydantic import BaseModel
from typing import Dict, Any, Optional

class TGVizBotAction(BaseModel):
    """
    Model describing the action returned by the API.
    """
    skip_update: Optional[bool] = None
    send_ads: Optional[int] = None

class TGVizApiResponse(BaseModel):
    """
    API response model containing the update_id and possibly an action.
    """
    update_id: int
    action: Optional[TGVizBotAction] = None

def detect_library() -> str:
    """
    Detects the Telegram Bot API library in use and returns its name with version.
    Checks the following libraries:
      - aiogram
      - python-telegram-bot (imported as telegram)
      - pyrogram
      - telethon
      - pyTelegramBotAPI (imported as telebot)
    If none is found, returns "unknown".
    """
    try:
        if "aiogram" in sys.modules:
            import aiogram
            return f"aiogram/{getattr(aiogram, '__version__', 'unknown')}"
    except Exception:
        pass

    try:
        if "telegram" in sys.modules:
            import telegram
            return f"python-telegram-bot/{getattr(telegram, '__version__', 'unknown')}"
    except Exception:
        pass

    try:
        if "pyrogram" in sys.modules:
            import pyrogram
            return f"pyrogram/{getattr(pyrogram, '__version__', 'unknown')}"
    except Exception:
        pass

    try:
        if "telethon" in sys.modules:
            import telethon
            return f"telethon/{getattr(telethon, '__version__', 'unknown')}"
    except Exception:
        pass

    try:
        if "telebot" in sys.modules:
            import telebot
            return f"pyTelegramBotAPI/{getattr(telebot, '__version__', 'unknown')}"
    except Exception:
        pass

    return "unknown"


class TGVizClient:
    """
    Client for sending Update data to the TGViz API.
    """
    def __init__(
        self,
        tgviz_bot_token: str,
        api_url: str = "https://api.tgviz.com/v1/post-update",
        timeout: float = 5.0
    ):
        self.api_url = api_url
        self.tgviz_bot_token = tgviz_bot_token
        self.timeout = timeout
        self.library = detect_library()
        self.python_version = platform.python_version()

    async def send_update(self, update: Dict[str, Any]) -> TGVizApiResponse:
        """
        Sends the update to the TGViz API and returns the parsed response.

        :param update: Update as a dictionary.
        :return: An instance of TGVizApiResponse.
        :raises httpx.RequestError: In case of a request error.
        :raises httpx.HTTPStatusError: For response status codes 4xx/5xx.
        """
        headers = {
            "X-TGViz-Bot-Token": self.tgviz_bot_token,
            "Content-Type": "application/json",
            "X-TGViz-Client-Library": self.library,
            "X-TGViz-Python-Version": self.python_version,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(self.api_url, json=update, headers=headers)
            response.raise_for_status()
            response_json = response.json()
            return TGVizApiResponse.parse_obj(response_json)
