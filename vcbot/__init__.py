import logging
import time
from pyrogram import Client
from vcbot.config import Var
from vcbot.queue import Queue
StartTime = time.time()

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("pytgcalls").setLevel(logging.WARNING)
logging.getLogger("youtube_dl").setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO)

instances = dict()
queues = Queue()
to_delete = []
ff_sempai = dict()

Bot = None
if Var.BOT_TOKEN:
    Bot = Client(
        "bot",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        bot_token=Var.BOT_TOKEN,
        workers=2
    )
UB = Client(
    Var.SESSION,
    api_id=Var.API_ID,
    api_hash=Var.API_HASH,
    workers=8
)