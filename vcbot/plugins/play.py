import re
from vcbot import UB
from vcbot.config import Var
from pyrogram import filters
from vcbot.player import Player
from pyrogram.types import Message
from vcbot.helpers.utils import is_ytlive


@UB.on_message(filters.user(Var.SUDO) & filters.command('play', '!'))
async def play_msg_handler(_, m: Message):
    chat_id = m.chat.id
    player = Player(chat_id)
    is_file = False
    is_live = False
    try:
        query = m.text.split(' ', 1)[1]
    except IndexError:
        query = None
    if query:
        try:
            link = re.search(r'((https?:\/\/)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)\/(watch\?v=|embed\/|v\/|.+\?v=)?([^&=%\?]{11}))', m.text).group(1)
            is_live = await is_ytlive(link)
        except:
            link = query
            ...
        is_file = False
    if m.reply_to_message:
        if m.reply_to_message.video:
            is_file = True
            link = m.reply_to_message
        # todo
    if is_live:
        return await m.reply("**Error**: This is a live link.\nTip: use !stream command.")
    if player.is_live:
        return await m.reply("**Error**: A Live stream is already going on this chat.\nPlease `!leave` and play the file again.")
    status = await m.reply("Downloading...")
    p = await player.play_or_queue(link, m, is_file)
    await status.edit("Playing.." if p else "Queued")

@UB.on_message(filters.user(Var.SUDO) & filters.command('leave', '!'))
async def leave_handler(_, m: Message):
    player = Player(m.chat.id)
    await player.leave_vc()


