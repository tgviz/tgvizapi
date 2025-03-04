import logging
import asyncio
from typing import Callable, Any, Awaitable, Dict

from .client import TGVizClient

logger = logging.getLogger(__name__)

class TGVizUpdateProcessor:
    """
    Universal Update processor: sends the update to the TGViz API and
    based on the received response, determines whether to continue processing.
    """
    def __init__(
        self,
        tgviz_bot_token: str,
        api_url: str = "https://api.tgviz.com/v1/post-update",
        timeout: float = 5.0,
        is_async: bool = True
    ):
        self.client = TGVizClient(
            tgviz_bot_token=tgviz_bot_token,
            api_url=api_url,
            timeout=timeout
        )
        self.is_async = is_async

    async def process_update(
        self,
        update: Dict[str, Any],
        handler: Callable[[Dict[str, Any]], Awaitable[Any]]
    ) -> Any:
        """
        Sends the update to the API and then calls the provided handler.
        If the API returns an action with skip_update=True, processing is halted.

        :param update: Update as a dictionary.
        :param handler: Asynchronous update handler function.
        :return: The result of the handler or None if the update is skipped.
        """
        try:
            if self.is_async:
                # Асинхронный fire-and-forget вызов API
                asyncio.create_task(self._fire_and_forget(update))
            else:
                response = await self.client.send_update(update)
                if response.action and response.action.skip_update:
                    logger.debug("Update skipped based on TGVIZ API decision.")
                    return None
        except Exception as e:
            logger.error(f"Error processing update: {e!r}")

        return await handler(update)

    async def _fire_and_forget(self, update: Dict[str, Any]) -> None:
        """
        Asynchronous call to send the update without waiting for the result.
        """
        try:
            await self.client.send_update(update)
        except Exception as e:
            logger.error(f"Error in fire-and-forget sending update: {e!r}")
