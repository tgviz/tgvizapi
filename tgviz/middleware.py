import logging
import asyncio
from typing import Callable, Any, Awaitable, Dict, List

from .client import TGVizClient

logger = logging.getLogger(__name__)

def detect_event_type(update: Dict[str, Any]) -> str:
    """
    Detects the event type from the update dictionary.
    
    Checks for known keys in a specific order and returns the first key 
    whose value is truthy. If no key is found, returns "undefined".
    
    :param update: The update as a dictionary.
    :return: A string representing the event type (e.g., 'message', 'inline_query', etc.)
             or "undefined" if none of the known types is found.
    """
    event_keys = [
        "message",
        "edited_message",
        "channel_post",
        "edited_channel_post",
        "inline_query",
        "chosen_inline_result",
        "callback_query",
        "shipping_query",
        "pre_checkout_query",
        "poll",
        "poll_answer",
        "my_chat_member",
        "chat_member",
        "chat_join_request",
        "message_reaction",
        "message_reaction_count",
        "chat_boost",
        "removed_chat_boost",
        "deleted_business_messages",
        "business_connection",
        "edited_business_message",
        "business_message",
        "purchased_paid_media"
    ]
    for key in event_keys:
        if key in update and update.get(key):
            return key
    return "undefined"

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
        is_async: bool = True,
        exclude_updates: List[str] = ['inline_query']
    ) -> None:
        """
        Initializes the TGVizUpdateProcessor.

        :param tgviz_bot_token: The token used for authentication with the TGViz API.
        :param api_url: The URL of the TGViz API endpoint.
        :param timeout: Timeout (in seconds) for the API request.
        :param is_async: If True, sends the update asynchronously (fire-and-forget) - the fastest option.
                         If False, waits for the API response and may halt processing if
                         skip_update=True is returned - required if "mandatory subscription" is on.
        :param exclude_updates: A list of Update types (as strings) that should be excluded from API logging.
                                Updates with these types will be processed directly by the handler.
        """
        self.client = TGVizClient(
            tgviz_bot_token=tgviz_bot_token,
            api_url=api_url,
            timeout=timeout
        )
        self.is_async = is_async
        self.exclude_updates = exclude_updates

    async def process_update(
        self,
        update: Dict[str, Any],
        handler: Callable[[Dict[str, Any]], Awaitable[Any]]
    ) -> Any:
        """
        Sends the update to the API and then calls the provided handler.
        If the event type is "undefined" or is in the `exclude_updates` list, the update is passed 
        directly to the handler without sending it to the API.
        If the API returns an action with skip_update=True, processing is halted.

        :param update: Update as a dictionary.
        :param handler: Asynchronous update handler function.
        :return: The result of the handler or None if the update is skipped.
        """
        event_type = detect_event_type(update)
        if event_type == "undefined":
            logger.warning("Undefined update type received; skipping API processing.")
            return await handler(update)
        if event_type in self.exclude_updates:
            return await handler(update)

        try:
            if self.is_async:
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
