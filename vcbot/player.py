import os
import time
import signal
import asyncio
import subprocess
from vcbot.config import Var
from pytgcalls import StreamType
from pyrogram.types import Message
from pytgcalls.types import Update
from pytgcalls.pytgcalls import PyTgCalls
from vcbot import UB, queues, group_calls, logging
from vcbot.helpers.utils import generate_hash, tg_download, yt_download
from pytgcalls.types.input_stream import (
    VideoParameters,
    AudioParameters,
    InputAudioStream,
    InputVideoStream
)
#
# base from https://github.com/TeamUltroid/Ultroid/blob/dev/vcbot/__init__.py
# Thanks to TeamUltroid :)

ms = {}

@group_calls.on_stream_end()
async def on_stream_end(client: PyTgCalls, update: Update):
    logging.info(f"called ended stream")
    cms = time.time()
    if k:= ms.get(update.chat_id):
        if cms-k < 10:
            logging.info(cms-k)
            return
    ms[update.chat_id] = cms
    anything = queues.get(update.chat_id, False)
    player = Player(update.chat_id)
    if player.is_live:
        return
    if anything:
        next = queues.get(update.chat_id)
        video , is_path, user = next
        suc, err = await player.play_file(video, is_path, change=True)
        if not suc:
            await UB.send_message(update.chat_id, str(err))
        else:
            await UB.send_message(update.chat_id, "Now playing: {}\nRequested by: {}".format(video, user.mention(style="md")))
        return True
    else:
        await player.leave_vc()


meta = dict()
class Player:
    def __init__(self, chat_id):
        self._current_chat = chat_id
        self.ffmpeg_log = open('ffmpeg.log', 'w')
        if not meta.get(chat_id):
            meta[chat_id] = {}
        if meta[chat_id] == {}:
            self.is_live = False
            self.ffmpeg_process = None
            self.is_playing = False
            self.to_delete = []
        else:
            self.is_live = meta[chat_id].get('is_live')
            self.ffmpeg_process = meta[chat_id].get('ffmpeg_process')
            self.is_playing = meta[chat_id].get('is_playing')
            self.to_delete = meta[chat_id].get('to_delete', [])
        self.meta = meta[chat_id]

    def __eq__(self, o: object) -> bool:
        return self._current_chat == o._current_chat

    async def play_file(self, file, is_path=False, change=False):
        self.meta["is_playing"] = True
        if not is_path:
            file, _ = await yt_download(file)
        else:
            file = await tg_download(file)
        audio, video = await self.convert(file, delete=True)
        self.add_to_trash(audio)
        self.add_to_trash(video)
        if change:
            await self.change_source(video, audio)
        else:
            await self.join_play(video, audio)
        return True, None

    async def convert(self,
                      file_path: str,
                      delete=True,
                      daemon=False,
                      audio_file=None,
                      video_file=None):
        if not audio_file:
            audio_file = generate_hash(5) + 'audio' + ".raw"
        if not video_file:
            video_file = generate_hash(5) + 'video' + ".raw"
        cmd = ["ffmpeg", "-y", "-i", file_path, "-f", "s16le", "-ac", "1", "-ar", str(Var.BITRATE), audio_file, "-f", "rawvideo", '-r', str(Var.FPS), '-pix_fmt', 'yuv420p', '-vf', f'scale={Var.WIDTH}:-1', "-preset", "ultrafast", video_file]
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=self.ffmpeg_log, stderr=asyncio.subprocess.STDOUT
        )
        if daemon:
            self.meta['ffmpeg_process'] = proc
        else:
            await proc.communicate()
            self.ffmpeg_log.close()
        if delete:
            try:
                os.remove(file_path)
            except BaseException:
                ...
        while not os.path.exists(audio_file) and not os.path.exists(video_file):
            await asyncio.sleep(0.125)
        return audio_file, video_file

    async def join_play(self, video, audio, width=Var.WIDTH, height=Var.HEIGHT, fps=Var.FPS, bitrate=Var.BITRATE):
        await group_calls.join_group_call(
            self._current_chat,
            InputAudioStream(
                audio,
                AudioParameters(
                    bitrate=bitrate,
                ),
            ),
            InputVideoStream(
                video,
                VideoParameters(
                    width=width,
                    height=height,
                    frame_rate=fps,
                ),
            ),
            stream_type=StreamType().pulse_stream,
        )
        self.meta["is_playing"] = True

    async def change_source(self, video, audio, width=Var.WIDTH, height=Var.HEIGHT, fps=Var.FPS, bitrate=Var.BITRATE):
        await group_calls.change_stream(
            self._current_chat,
            InputAudioStream(
                audio,
                AudioParameters(
                    bitrate=bitrate
                ),
            ),
            InputVideoStream(
                video,
                VideoParameters(
                    width=width,
                    height=height,
                    frame_rate=fps,
                )
            )
        )
        if not self.is_playing:
            self.meta["is_playing"] = True
    
    async def play_or_queue(self, vid, m: Message, is_path=False, change=False):
        anything = queues.get(self._current_chat, False)
        print("Playing: ", self.is_playing)
        if not self.is_playing:
            suc, err = await self.play_file(vid, is_path)
            if not suc:
                await UB.send_message(self._current_chat, str(err))
            return True
        else:
            data = [vid, is_path, m.from_user]
            pos = queues.add(self._current_chat, data)
            await m.reply(f"Added to queue #{pos}")
            return False
            
    async def leave_vc(self):
        await group_calls.leave_group_call(self._current_chat)
        pid = await self.terminate_ffmpeg()
        status = f"Terminated FFmpeg with PID `{pid}`" if \
            pid else ""
        status += "\nSuccessfully left vc!"
        if self.is_playing:
            self.meta["is_playing"] = False
        self.meta["is_live"] = False
        self.clear_played()
        self.meta["is_playing"] = False
        await UB.send_message(self._current_chat, status)

    async def terminate_ffmpeg(self):
        if x:= self.ffmpeg_process:
            try:
                x.terminate()
                return x.pid
            except (RuntimeError or RuntimeWarning):
                await x.terminate()
                return await x.pid
    
    def clear_played(self):
        logging.info("Deleting additional files")
        files = self.to_delete
        for i in files:
            try:
                os.remove(i)
                logging.info("Removed {}".format(i))
            except BaseException:
                logging.info("Couldn't remove {}".format(i))
            self.meta["to_delete"].remove(i)
    
    def add_to_trash(self, file):
        if x:= self.to_delete:
            try:
                if x:
                    self.meta["to_delete"].append(file)
                else:
                    self.to_delete["to_delete"] = [file]
            except (IndexError or AttributeError):
                pass