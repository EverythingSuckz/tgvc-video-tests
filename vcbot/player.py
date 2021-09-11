import os
import re
import time
import math
import asyncio
from vcbot.config import Var
from pytgcalls import StreamType
from pyrogram.types import Message
from pyrogram.errors import MessageNotModified
from pytgcalls.types import Update
from pytgcalls.pytgcalls import PyTgCalls
from vcbot import UB, queues, group_calls, LOG
from vcbot.helpers.utils import generate_hash, get_duration, ms_format, tg_download
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
    LOG.info(f"called ended stream")
    cms = time.time()
    if k:= ms.get(update.chat_id):
        if cms-k < 10:
            LOG.info(cms-k)
            return
    ms[update.chat_id] = cms
    anything = queues.get(update.chat_id, False)
    player = Player(update.chat_id)
    if player.is_live:
        return
    if player.current_process:
        pass
    if anything:
        player.clear_played()
        next = queues.get(update.chat_id)
        video , is_path, user = next
        mess = await UB.send_message(update.chat_id, "Processing Next Song..")
        suc, err = await player.play_file(video, mess, is_path=is_path, change=True)
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
        self._progress_file = open(f'progress{chat_id}.log', 'w')
        self._rprogress_file = open(f'progress{chat_id}.log', 'r')
        if not meta.get(chat_id):
            meta[chat_id] = {}
        if meta[chat_id] == {}:
            self.is_live = False
            self.current_process = None
            self.is_playing = False
            self.to_delete = dict()
        else:
            self.is_live = meta[chat_id].get('is_live')
            self.current_process = meta[chat_id].get('current_process')
            self.is_playing = meta[chat_id].get('is_playing')
            self.to_delete = meta[chat_id].get('to_delete', {})
        self.meta = meta[chat_id]

    def __eq__(self, o: object) -> bool:
        return self._current_chat == o._current_chat

    async def play_file(self, file, m: Message, is_path=False, change=False):
        self.meta["is_playing"] = True
        if not is_path:
            file = await self.yt_download(file, m)
        else:
            file = await tg_download(file)
        audio, video = await self.convert(file, m, delete=True)
        self.add_to_trash(audio)
        self.add_to_trash(video)
        if change:
            await self.change_source(video, audio)
        else:
            await self.join_play(video, audio)
        return True, None

    async def yt_download(self, ytlink, m: Message):
        # file_name = await get_filename(ytlink)
        cmd = ["youtube-dl",
            "-c",
            "--geo-bypass",
            "--no-playlist",
            "--hls-prefer-ffmpeg",
            "--no-check-certificate",
            "--embed-subs",
            "-f",
            f"bestvideo[height<={Var.HEIGHT},ext=mp4]+bestaudio[ext=m4a]",
            ytlink,
            "-o",
            "%(title)s.%(ext)s"
        ]
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=self._progress_file, stderr=asyncio.subprocess.PIPE)
        self.meta["current_process"] = proc
        last_percentage = None
        file_name = None
        while True:
            latest = self._rprogress_file.readlines()
            if not latest:
                continue
            else:
                if match := re.search(r'\[ffmpeg\] Merging formats into "(.+\.\w+)"', " ".join(latest)):
                    file_name = match.group(1)
                if file_name:
                    break
                latest = latest[-1]
                match = re.search(r'\[\w+\]\s+(?P<percentage>\d+\.?\d?%)(?:\sof\s+)(?P<total>\d+\.\d+\w+)\s(?:at\s+(\d+\.\d+\w+\/s)\s(?P<eta>.+))$', latest)
                if match:
                    percent = match.group('percentage')
                    total = match.group('total')
                    eta = match.group('eta')
                    if last_percentage != percent:
                        await m.edit(f"Downloading {percent} of {total}\n{eta}")
                        last_percentage = percent
                        await asyncio.sleep(2)
                else:
                    continue
        await proc.communicate()
        self._progress_file.close()
        self.meta["current_process"] = None
        if os.path.exists(file_name):
            return file_name

    async def convert(self,
                      file_path: str,
                      m: Message,
                      delete=True,
                      daemon=False,
                      audio_file=None,
                      video_file=None):
        if not audio_file:
            audio_file = generate_hash(5) + 'audio' + ".raw"
        if not video_file:
            video_file = generate_hash(5) + 'video' + ".raw"
        cmd = ["ffmpeg", "-progress", f'progress{self._current_chat}.log', "-y", "-i", file_path, "-f", "s16le", "-ac", "1", "-ar", str(Var.BITRATE), audio_file, "-f", "rawvideo", '-r', str(Var.FPS), '-pix_fmt', 'yuv420p', '-vf', f'scale={Var.WIDTH}:-1', "-preset", "ultrafast", video_file]
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        if daemon:
            self.meta['current_process'] = proc
        else:
            last_percentage = None
            duration = await get_duration(file_path)
            while True:
                text = open(f'progress{self._current_chat}.log', 'r').read()
                frame = re.findall("frame=(\d+)", text)
                fps = re.findall("fps=(\d+)", text)
                time_in_us=re.findall("out_time_ms=(\d+)", text)
                progress=re.findall("progress=(\w+)", text)
                speed=re.findall("speed=(\d+\.?\d*)", text)
                frame = int(frame[-1]) if frame else 0
                speed = speed[-1] if speed else 1
                fps = int(fps[-1]) if fps else 0
                time_in_us = time_in_us[-1] if time_in_us else 0
                if progress:
                    if progress[-1] == "end":
                        break
                elapsed_time = int(time_in_us)/1000000
                difference = math.floor( (duration - elapsed_time) / float(speed) )
                eta = "N\A" if difference < 0 else ms_format(difference*1000)
                percentage = math.floor(elapsed_time * 100 / duration)
                if last_percentage != percentage:
                    try:
                        await m.edit(f"Converting {percentage}%\nETA: {eta}\nSpeed: {speed}\nFPS: {fps}")
                    except MessageNotModified:
                        pass
                    await asyncio.sleep(3)
            await proc.communicate()
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
            suc, err = await self.play_file(vid, m, is_path, change)
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
        if x:= self.current_process:
            try:
                self.meta["current_process"] = None
                x.terminate()
                return x.pid
            except (RuntimeError or RuntimeWarning):
                self.meta["current_process"] = None
                await x.terminate()
                return await x.pid
    
    def clear_played(self):
        LOG.info("Deleting additional files")
        files = self.to_delete.get(self._current_chat, [])
        print(files)
        for i in files:
            print(i)
            try:
                os.remove(i)
                LOG.info("Removed {}".format(i))
            except BaseException:
                LOG.info("Couldn't remove {}".format(i))
            self.meta["to_delete"][self._current_chat].remove(i)
    
    def add_to_trash(self, file):
        try:
            self.meta["to_delete"]
        except KeyError:
            self.meta["to_delete"] = {}
        if not self.meta["to_delete"].get(self._current_chat):
            self.meta["to_delete"][self._current_chat] = [file]
        else:
            self.meta["to_delete"][self._current_chat].append(file)