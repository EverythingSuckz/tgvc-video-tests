import re
import os
import signal
import asyncio
import traceback
from asyncio import sleep
from pytgcalls.exceptions import GroupCallNotFound
from vcbot.config import Var
from pyrogram import filters
from vcbot.player import Player
from pyrogram.types import Message
from vcbot import UB, to_delete, ff_sempai, group_calls
from vcbot.helpers.utils import convert_to_stream, raw_converter, is_ytlive
from pytgcalls import StreamType
from pytgcalls.types.input_stream import (
    VideoParameters,
    AudioParameters,
    InputAudioStream,
    InputVideoStream
)



@UB.on_message(filters.user(Var.SUDO) & filters.command('stream', '!'))
async def stream_msg_handler(_, m: Message):
    status = "Processing.."
    msg = await m.reply(status)
    stream_url = "https://feed.play.mv/live/10005200/7EsSDh7aX6/master.m3u8"
    try:
        stream_url = m.text.split(' ', 1)[1]
        link = re.search(r'((https?:\/\/)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)\/(watch\?v=|embed\/|v\/|.+\?v=)?([^&=%\?]{11}))', stream_url)
        if link:
            link = link.group(1)
            stream_url = await convert_to_stream(link)
    except IndexError:
        ...
    vid = f"vid{m.chat.id}.raw"
    audio = f"audio{m.chat.id}.raw"
    player = Player(m.chat.id)
    player.add_to_trash(vid)
    player.add_to_trash(audio)
    proc = raw_converter(stream_url, vid, audio)
    ff_sempai[m.chat.id] = proc
    while not os.path.exists(vid) and not os.path.exists(audio):
        await asyncio.sleep(0.1)
    await group_calls.join_group_call(
        m.chat.id,
        InputAudioStream(
            audio,
            AudioParameters(
                bitrate=48000,
            ),
        ),
        InputVideoStream(
            vid,
            VideoParameters(
                width=640,
                height=360,
                frame_rate=30,
            ),
        ),
        stream_type=StreamType().pulse_stream,
    )



@UB.on_message(filters.user(Var.SUDO) & filters.command('stop', '!'))
async def stop_stream_msg_handler(_, m: Message):
    player = Player(m.chat.id)
    try:
        instance = group_calls.get_active_call(m.chat.id)
    except GroupCallNotFound:
        instance = None
    print(instance)
    if instance:
        await player.leave_vc()
    else:
        await m.reply("No streams going on vc")