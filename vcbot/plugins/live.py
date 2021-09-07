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
from vcbot.helpers.utils import convert_to_stream, raw_converter, is_ytlive, transcode
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
    player = Player(m.chat.id)
    audio, video, proc = await transcode(stream_url, daemon=True)
    ff_sempai[m.chat.id] = proc
    await group_calls.join_group_call(
        m.chat.id,
        InputAudioStream(
            audio,
            AudioParameters(
                bitrate=48000,
            ),
        ),
        InputVideoStream(
            video,
            VideoParameters(
                width=1280,
                height=720,
                frame_rate=20,
            ),
        ),
        stream_type=StreamType().local_stream,
    )



@UB.on_message(filters.user(Var.SUDO) & filters.command('stop', '!'))
async def stop_stream_msg_handler(_, m: Message):
    player = Player(m.chat.id)
    try:
        instance = group_calls.get_active_call(m.chat.id)
    except GroupCallNotFound:
        instance = None
    if instance:
        await player.leave_vc()
    else:
        await m.reply("No streams going on vc")