import re
import time
from datetime import datetime
from vcbot.helpers.utils import get_readable_time
from vcbot.config import Var
from pyrogram import filters
from vcbot import UB, to_delete, StartTime
from vcbot.player import Player
from pyrogram.types import Message

@UB.on_message(filters.command('ping', '!'))
async def ping_msg_handler(_, m: Message):
    to_be_edited = await m.reply('`Pinging..`')
    start_ms = datetime.now()
    uptime = get_readable_time((time.time() - StartTime))
    end = datetime.now()
    ms = (end - start_ms).microseconds / 1000
    await to_be_edited.edit('🏓 Pong\nms: {}\n uptime: {}'.format(ms, uptime))

@UB.on_message(filters.user(Var.SUDO) & filters.command('play', '!'))
async def play_msg_handler(_, m: Message):
    global to_delete
    chat_id = m.chat.id
    player = Player(chat_id)
    is_file = False
    try:
        query = m.text.split(' ', 1)[1]
    except IndexError:
        query = None
    if query:
        try:
            link = re.search(r'((https?:\/\/)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)\/(watch\?v=|embed\/|v\/|.+\?v=)?([^&=%\?]{11}))', m.text).group(1)
        except:
            link = query
            ...
        is_file = False
    if m.reply_to_message:
        if m.reply_to_message.video:
            is_file = True
            link = m.reply_to_message
        # todo
    status = await m.reply("Downloading...")
    await player.join_vc()
    p = await player.play_or_queue(link, m, is_file)
    await status.edit("Playing.." if p else "Queued")

@UB.on_message(filters.user(Var.SUDO) & filters.command('leave', '!'))
async def join_handler(_, m: Message):
    player = Player(m.chat.id)
    await player.leave_vc()


