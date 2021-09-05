import os
import json
import asyncio
import subprocess
from youtube_dl import YoutubeDL
from pyrogram.types import Message

def get_readable_time(seconds: int) -> str:
    count = 0
    readable_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", " days"]
    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        readable_time += time_list.pop() + ", "
    time_list.reverse()
    readable_time += ": ".join(time_list)
    return readable_time

def raw_converter(source, vid, audio, log_file='ffmpeg.log'):
    # log_file = open(log_file, 'w')
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", source, "-f", "s16le", "-ac", "1", "-ar", "48000", audio, "-f", "rawvideo", '-r', '25', '-pix_fmt', 'yuv420p', '-vf', 'scale=640:-1', vid]
    return subprocess.Popen(
        cmd,
        stdin=None,
        stdout=None,
        stderr=None,
        cwd=None,
    )

async def is_ytlive(url):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'outtmpl': '%(title)s - %(extractor)s-%(id)s.%(ext)s',
        'writethumbnail': False
    }
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        return info_dict.get('is_live')

async def convert_to_stream(url: str):
    cmd = ["youtube-dl", "-g", url]
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, _ = await proc.communicate()
    if stdout:
        return stdout.decode().strip()

async def transcode(file_path: str, delete=True):
    audio_f = file_path.split(".")[0] + 'audio' + ".raw"
    video_f = file_path.split(".")[0] + 'video' + ".raw"
    if (os.path.isfile(audio_f) and (os.path.isfile(video_f))):
        return audio_f, video_f
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", file_path, "-f", "s16le", "-ac", "1", "-ar", "48000", audio_f, "-f", "rawvideo", '-r', '25', '-pix_fmt', 'yuv420p', '-vf', 'scale=640:-1', video_f]
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    await proc.communicate()
    if proc.returncode != 0:
        print(f"Transcode failed for {file_path}")
        return None
    if delete:
        try:
            os.remove(file_path)
        except BaseException:
            ...
    return audio_f, video_f

async def get_video_info(filename):
    proc = await asyncio.create_subprocess_exec('ffprobe', '-hide_banner', '-print_format', 'json', '-show_format', '-show_streams', filename, stdout=asyncio.subprocess.PIPE)
    stdout, _ = await proc.communicate()
    return json.loads(stdout)

async def get_backdrop_res(url):
    info = await get_video_info(url)
    width = None
    height = None
    for each in info['streams']:
        try:
            width = int(each['width'])
            height = int(each['height'])
            break
        except (KeyError or AttributeError):
            continue
    if height:
        if not width:
            width, height = get_resolution({'height': height})
        return (width, height)

# got this from somewhere
def get_resolution(info_dict):
    if {"width", "height"} <= info_dict.keys():
        width = int(info_dict['width'])
        height = int(info_dict['height'])
    # https://support.google.com/youtube/answer/6375112
    elif info_dict.get("height") == 1080:
        width = 1920
        height = 1080
    elif info_dict.get("height") == 720:
        width = 1280
        height = 720
    elif info_dict.get("height") == 480:
        width = 854
        height = 480
    elif info_dict.get("height") == 360:
        width = 640
        height = 360
    elif info_dict.get("height") == 240:
        width = 426
        height = 240
    else:
        return None
    return (width, height)

async def yt_download(ytlink):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'outtmpl': '%(title)s - %(extractor)s-%(id)s.%(ext)s',
        'writethumbnail': False
    }
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(ytlink, download=False)
        res = get_resolution(info_dict)
        if not res:
            res = await get_backdrop_res(ytlink)
        ydl.process_info(info_dict)
        _file = ydl.prepare_filename(info_dict)
        return _file, res

async def tg_download(m: Message):
    path = await m.download()
    return path

# # ignore
# async def _transcode(file_path: str):
#     file_name = file_path.split(".")[0] + ".raw"
#     if os.path.isfile(file_name):
#         return file_name
#     proc = await asyncio.create_subprocess_shell(
#         f"ffmpeg -y -i {file_path} -f s16le -ac 2 -ar 48000 -acodec pcm_s16le {file_name}",
#         asyncio.subprocess.PIPE,
#         stderr=asyncio.subprocess.PIPE
#     )
#     await proc.communicate()
#     if proc.returncode != 0:
#         print(f"Transcode failed for {file_path}")
#         return None
#     return file_name

# # ignore
# async def __transcode(filename: str):
#     file_name = filename.split(".")[0] + ".raw"
#     ffmpeg.input(filename).output(
#         file_name,
#         format="s16le",
#         acodec="pcm_s16le",
#         ac=2,
#         ar="48k",
        
#         loglevel="error",
#     ).overwrite_output().run_async()
#     if os.path.exists(file_name):
#         return file_name