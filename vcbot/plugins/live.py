import os
import asyncio
from vcbot.config import Var
from pyrogram import filters
from vcbot import UB, to_delete, ff_sempai
from vcbot.player import Player
from pyrogram.types import Message
from asyncio import sleep
from vcbot.helpers.utils import raw_converter



@UB.on_message(filters.user(Var.SUDO) & filters.command('stream', '!'))
async def join_handler(_, m: Message):
    global ff_sempai
    stream_url = "https://feed.play.mv/live/10005200/7EsSDh7aX6/master.m3u8"
    try:
        stream_url = m.text.split(' ', 1)[1]
    except IndexError:
        ...
    file = f"stream{m.chat.id}.raw"
    player = Player(m.chat.id)
    if not ff_sempai.get(m.chat.id) and player.group_call.is_connected:
        proc = ff_sempai[m.chat.id]
        proc.terminate()
    process = raw_converter(stream_url, file)
    ff_sempai[m.chat.id] = process
    await asyncio.sleep(4)
    # if not os.path.exists(file):
    #     return await m.reply("FFMPEG died!")
    await player.join_vc()
    player.group_call.input_filename = file
    await player.group_call.set_video_capture(stream_url, fps=30, width=1280, height=720)

@UB.on_message(filters.user(Var.SUDO) & filters.command('stop', '!'))
async def join_handler(_, m: Message):
    global ff_sempai
    player = Player(m.chat.id)
    if not ff_sempai.get(m.chat.id) and player.group_call.is_connected:
        proc = ff_sempai[m.chat.id]
        await m.reply(f"FFMPEG process `{proc.pid}` is being terminated")
        proc.terminate()
    else:
        await m.reply("No streams going on vc")