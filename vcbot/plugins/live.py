import re
import os
import signal
import asyncio
import traceback
from asyncio import sleep
from vcbot.config import Var
from pyrogram import filters
from vcbot.player import Player
from pyrogram.types import Message
from vcbot import UB, to_delete, ff_sempai
from vcbot.helpers.utils import convert_to_stream, raw_converter, is_ytlive



@UB.on_message(filters.user(Var.SUDO) & filters.command('stream', '!'))
async def stream_msg_handler(_, m: Message):
    global ff_sempai
    status = "Processing.."
    msg = await m.reply(status)
    stream_url = "https://feed.play.mv/live/10005200/7EsSDh7aX6/master.m3u8"
    try:
        stream_url = m.text.split(' ', 1)[1]
        link = re.search(r'((https?:\/\/)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)\/(watch\?v=|embed\/|v\/|.+\?v=)?([^&=%\?]{11}))', stream_url)
        if link:
            link = link.group(1)
            is_live = await is_ytlive(link)
            if not is_live:
                status += "\nError: This Youtube url is not a live video"
                return await msg.edit(status)
            stream_url = await convert_to_stream(link)
    except IndexError:
        ...
    file = f"stream{m.chat.id}.raw"
    player = Player(m.chat.id)
    if ff_sempai.get(m.chat.id) and player.group_call.is_connected:
        status += "\nFound another stream going on this chat..\nTerminated!"
        if os.path.exists(file):
            try:
                os.remove(file)
            except Exception as err:
                print(traceback.format_exc())
                status += f"\nError: {err}"
        proc = ff_sempai[m.chat.id]
        await msg.edit(status)
        proc.send_signal(signal.SIGQUIT)
    process = raw_converter(stream_url, file)
    ff_sempai[m.chat.id] = process
    await player.join_vc()
    player.group_call.input_filename = file
    await player.group_call.set_video_capture(stream_url)
    await asyncio.sleep(7)
    if not os.path.exists(file):
        status += "\nError: Stream not found!"
        await msg.edit(status)
    else:
        await msg.delete()



@UB.on_message(filters.user(Var.SUDO) & filters.command('stop', '!'))
async def stop_stream_msg_handler(_, m: Message):
    global ff_sempai
    player = Player(m.chat.id)
    if player.group_call.is_connected:
        await player.leave_vc()
    if ff_sempai.get(m.chat.id):
        file = f"stream{m.chat.id}.raw"
        proc = ff_sempai[m.chat.id]
        await m.reply(f"FFMPEG process `{proc.pid}` is being terminated")
        proc.send_signal(signal.SIGQUIT)
        if os.path.exists(file):
            try:
                os.remove(file)
            except BaseException:
                ...
    else:
        await m.reply("No streams going on vc")