import os
import re
import json
import ffmpeg
import asyncio
from os import path
from vars import Var
from random import randint
from youtube_dl import YoutubeDL
from pyrogram import Client, filters
from pytgcalls import GroupCallFactory
from pyrogram.utils import MAX_CHANNEL_ID
from pyrogram.types.messages_and_media.message import Message

app = Client(Var.SESSION, api_id=Var.API_ID, api_hash=Var.API_HASH)
group_call = GroupCallFactory(app).get_file_group_call('test.raw')

# global stuffs

to_delete = []
QUEUE = []
group = None
playing = False


# got this from somewhere
def get_resolution(info_dict):
    if {"width", "height"} <= info_dict.keys():
        width = int(info_dict['width'])
        height = int(info_dict['height'])
    # https://support.google.com/youtube/answer/6375112
    elif info_dict['height'] == 1080:
        width = 1920
        height = 1080
    elif info_dict['height'] == 720:
        width = 1280
        height = 720
    elif info_dict['height'] == 480:
        width = 854
        height = 480
    elif info_dict['height'] == 360:
        width = 640
        height = 360
    elif info_dict['height'] == 240:
        width = 426
        height = 240
    return (width, height)

# ignore
async def _transcode(file_path: str):
    file_name = file_path.split(".")[0] + ".raw"
    if path.isfile(file_name):
        return file_name
    proc = await asyncio.create_subprocess_shell(
        f"ffmpeg -y -i {file_path} -f s16le -ac 2 -ar 48000 -acodec pcm_s16le {file_name}",
        asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    await proc.communicate()
    if proc.returncode != 0:
        print(f"Transcode failed for {file_path}")
        return None
    return file_name

# ignore
async def __transcode(filename: str):
    file_name = filename.split(".")[0] + ".raw"
    ffmpeg.input(filename).output(
        file_name,
        format="s16le",
        acodec="pcm_s16le",
        ac=2,
        ar="48k",
        
        loglevel="error",
    ).overwrite_output().run_async()
    if path.exists(file_name):
        return file_name

async def transcode(file_path: str):
    file_name = file_path.split(".")[0] + ".raw"
    if path.isfile(file_name):
        return file_name
    cmd = ["ffmpeg", "-y", "-i", file_path, "-f", "s16le", "-ac", "2", '-vn', "-ar", "48000", "-acodec", "pcm_s16le", file_name]
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    await proc.communicate()
    if proc.returncode != 0:
        print(f"Transcode failed for {file_path}")
        return None
    return file_name

async def download(ytlink):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'outtmpl': '%(title)s - %(extractor)s-%(id)s.%(ext)s',
        'writethumbnail': False
    }
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(ytlink, download=False)
        print(json.dumps(info_dict, indent=3))
        res = get_resolution(info_dict)
        ydl.process_info(info_dict)
        _file = ydl.prepare_filename(info_dict)
        return _file, res

# pytgcalls example template
@group_call.on_network_status_changed
async def on_network_changed(context, is_connected):
    chat_id = MAX_CHANNEL_ID - context.full_chat.id
    if is_connected:
        await app.send_message(chat_id, 'Successfully joined!')
    else:
        await app.send_message(chat_id, 'Disconnected from voice chat..')

@app.on_message(filters.chat(Var.CHANNEL) & filters.command('join', '!'))
async def join_handler(_, m: Message):
    global group, playing, to_delete
    group = m.chat
    try:
        link = re.search(r'((https?:\/\/)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)\/(watch\?v=|embed\/|v\/|.+\?v=)?([^&=%\?]{11}))', m.text).group(1)
    except AttributeError:
        link = None
    if not link:
        try:
            query = m.text.split(' ', 1)[1]
        except IndexError:
            query = None
        except AttributeError:
            query = None
        if not query:
            await m.reply("Please provide a link or a query")
            return
        # todo
    status = await m.reply("Downloading...")
    if not group_call.is_connected:
        await group_call.start(m.chat.id)
    print(len(QUEUE))
    print(playing)
    if not QUEUE and not playing:
        vid, res = await download(link)
        width, height = res
        print(width, height)
        audio = await transcode(vid)
        to_delete.append(vid)
        to_delete.append(audio)
        if not audio:
            await status.edit("Couldn't play audio")
            return
        print(f"Playing {audio}")
        await group_call.set_video_capture(vid, fps=30, width=width, height=height)
        group_call.input_filename = audio
        playing = True
        await status.edit("Playing")
    else:
        data = {'link': link, 'from_user': m.from_user}
        QUEUE.append(data)
        await m.reply(f"Added to queue #{len(QUEUE) + 1}")
    print('done')

@group_call.on_playout_ended
async def when_the_music_fucking_stops(group_call: group_call, filename):
    global playing, to_delete
    if not QUEUE:
        await group_call.stop()
        await group_call.leave_current_group_call()
        await app.send_message(group.id, "No more videos to play!")
        playing =False
        for i in to_delete:
            print(f"Deleting {i}")
            to_delete.remove(i)
            os.remove(i)
    else:
        data = QUEUE.pop(0)
        for i in to_delete:
            to_delete.remove(i)
            os.remove(i)
        link = data['link']
        user = data['from_user']
        vid, res = await download(link)
        width, height = res
        print(width, height)
        audio = await transcode(vid)
        to_delete.append(vid)
        to_delete.append(audio)
        if not audio:
            await app.send_message(group.id, f"Couldn't play audio for {link}")
            return
        await group_call.set_video_capture(vid, fps=30, width=width, height=height)
        group_call.input_filename = audio
        await app.send_message(group.id, f"Now playing {link}\n\nRequested by: {user.mention(style='md')}")
        

@app.on_message(filters.chat(Var.CHANNEL) & filters.command('leave', '!'))
async def join_handler(_, message):
    global playing, to_delete
    for i in to_delete:
        print(f"Deleting {i}")
        to_delete.remove(i)
        os.remove(i)
    playing =  False
    await group_call.leave_current_group_call()
    await group_call.stop()

app.run()

