import os
import time
from pyrogram import filters
from datetime import datetime
from pyrogram.types import Message
from vcbot import UB, group_calls, StartTime
from vcbot.helpers.utils import get_readable_time

@UB.on_message(filters.command('ping', '!'))
async def ping_msg_handler(_, m: Message):
    to_be_edited = await m.reply('`Pinging..`')
    start_ms = datetime.now()
    uptime = get_readable_time((time.time() - StartTime))
    end = datetime.now()
    ms = (end - start_ms).microseconds / 1000
    calls_ping = await group_calls.ping
    await to_be_edited.edit('🏓 **Pong**\n`⟶` ms: `{}`\n`⟶` PyTgCalls ping: `{}`\n`⟶` Uptime: {}'.format(ms, round(calls_ping, 2), uptime))

@UB.on_message(filters.command('logs', '!'))
async def ping_msg_handler(_, m: Message):
    bot_log_path = 'bot.log'
    ffmpeg_log_path = 'ffmpeg.log'
    if os.path.exists(bot_log_path):
        try:
            await m.reply_document(bot_log_path, quote=True, caption='📄 **Bot Logs**')
        except:
            os.remove(bot_log_path)
    if os.path.exists(ffmpeg_log_path):
        try:
            await m.reply_document(ffmpeg_log_path, quote=True, caption='📄 **FFmpeg Logs**')
        except:
            os.remove(ffmpeg_log_path)
    if not os.path.exists(bot_log_path) and not os.path.exists(ffmpeg_log_path):
        await m.reply('📄 **No logs found!**')