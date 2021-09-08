import logging
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
from vcbot import UB, group_calls
from vcbot.helpers.utils import convert_to_stream, is_ytlive, yt_download
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
    player = Player(m.chat.id)
    stream_url = "https://feed.play.mv/live/10005200/7EsSDh7aX6/master.m3u8"
    player.meta["is_live"] = True
    try:
        stream_url = m.text.split(' ', 1)[1]
        link = re.search(r'((https?:\/\/)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)\/(watch\?v=|embed\/|v\/|.+\?v=)?([^&=%\?]{11}))', stream_url)
        if link:
            link = link.group(1)
            if (await is_ytlive(stream_url)):
                stream_url = await convert_to_stream(link)
            else:
                player.meta["is_live"] = False
                stream_url, _ = await yt_download(link)
                player.add_to_trash(stream_url)
    except IndexError:
        ...
    audio = f"audio{m.chat.id}.raw"
    video = f"video{m.chat.id}.raw"
    audio, video = await player.convert(stream_url,
                                        daemon=True,
                                        delete=False,
                                        audio_file=audio,
                                        video_file=video)
    player.meta["is_playing"] = True
    await group_calls.join_group_call(
        m.chat.id,
        InputAudioStream(
            audio,
            AudioParameters(
                bitrate=Var.BITRATE,
            ),
        ),
        InputVideoStream(
            video,
            VideoParameters(
                width=Var.WIDTH,
                height=Var.HEIGHT,
                frame_rate=Var.FPS,
            ),
        ),
        stream_type=StreamType().live_stream,
    )

