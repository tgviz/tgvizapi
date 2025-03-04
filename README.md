# TGViz
![Downloads](https://img.shields.io/pypi/dm/tgviz)


**TGViz** is a universal asynchronous library for integrating with the TGViz API.  
It allows you to send Telegram bot Updates to the TGViz service for logging and processing. 

## Installation

```bash
pip install tgviz
```

Python >= 3.7

## How It Works

You can use **tgviz** in two ways:

1. **As a Processor (Recommended)**  
   The easiest way to integrate with TGViz. You wrap your existing Telegram bot update handlers,  
   and tgviz automatically logs data and decides whether to process the update or skip it based on the API response (if "mandatory subscription" is on).  
   
2. **Direct API Calls**  
   If you prefer more control, you can send updates manually using the provided `TGVizClient` class.

## Processor Modes

The `TGVizUpdateProcessor` supports two modes:  

- **Asynchronous mode (default)** – The fastest option. The bot continues processing updates without waiting for a response from the API.  
  This is suitable for any use cases (analytics, mailing and ad views) **except "mandatory subscription"** ads type.  

- **Synchronous mode** – The processor waits for the API response before passing the update to the bot's handler.  
  This is required for implementing the upcoming **"mandatory subscription"** feature.  
  In this mode, the API may return `skip_update=True`, preventing further processing if the user hasn’t subscribed yet.  
  _(Feature currently in development.)_  


## Usage Examples

### 1. Using tgviz as a Processor (Recommended)

If you want TGViz to automatically decide whether an update should be processed,  
you can use the **TGVizUpdateProcessor**.  


#### With `aiogram`

```python
import asyncio
from aiogram import Dispatcher, Bot, types
from aiogram.dispatcher.middlewares import BaseMiddleware
from tgviz.middleware import TGVizUpdateProcessor

TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TGVIZ_BOT_TOKEN = "YOUR_TGVIZ_BOT_TOKEN"

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

# Use is_async=False for synchronous mode (e.g., mandatory subscription feature)
tgviz_processor = TGVizUpdateProcessor(tgviz_bot_token=TGVIZ_BOT_TOKEN, is_async=True)

class TGVizMiddleware(BaseMiddleware):
    def __init__(self, processor: TGVizUpdateProcessor):
        self.processor = processor
    async def __call__(self, handler: callable, event: types.Update, data: dict):
        update_data = event.model_dump()
        return await self.processor.process_update(
            update=update_data,
            handler=lambda _: handler(event, data)
        )

# Register TGViz as outer middleware
dp.update.outer_middleware.register(TGVizMiddleware(tgviz_processor))

@dp.message_handler()
async def echo_handler(message: types.Message):
    await message.answer(message.text)

async def main():
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
```

#### With `python-telegram-bot`

```python
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes
from tgviz.middleware import TGVizUpdateProcessor

TGVIZ_BOT_TOKEN = "YOUR_TGVIZ_BOT_TOKEN"
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

# Use is_async=False for synchronous mode (e.g., mandatory subscription feature)
processor = TGVizUpdateProcessor(tgviz_bot_token=TGVIZ_BOT_TOKEN, is_async=True)

def tgviz_middleware(handler_func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        update_dict = update.to_dict()
        return await processor.process_update(
            update=update_dict,
            handler=lambda _: handler_func(update, context)
        )
    return wrapper

# handler with tgviz decorator:
@tgviz_middleware
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)

def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(MessageHandler(None, echo))
    application.run_polling()


if __name__ == "__main__":
    main()
```

---

### 2. Sending Updates Directly to TGViz API

If you want full control over what is sent to TGViz, you can use `TGVizClient` directly.  
This is useful if you are using a different Telegram library or need custom logic.

#### With `httpx` (Async HTTP Client)

```python
import asyncio
from tgviz.client import TGVizClient

async def main():
    client = TGVizClient(
        tgviz_bot_token="YOUR_TGVIZ_BOT_TOKEN"
    )

    update_data = {"update_id": 123456, "message": {"text": "Hello!"}}
    response = await client.send_update(update_data)
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

#### With `requests` (Sync HTTP Client)

```python
import requests

TGVIZ_BOT_TOKEN = "YOUR_TGVIZ_BOT_TOKEN"
API_URL = "https://api.tgviz.com/v1/post-update"

update_data = {"update_id": 123456, "message": {"text": "Hello!"}}
headers = {"X-TGViz-Bot-Token": TGVIZ_BOT_TOKEN, "Content-Type": "application/json"}

response = requests.post(API_URL, json=update_data, headers=headers)
print(response.json())
```

---


## Contributing

Contributions, bug reports, and suggestions are welcome! Feel free to open an issue or submit a pull request.

## License

[MIT License](LICENSE)
