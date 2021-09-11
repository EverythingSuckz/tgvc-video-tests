from os import getenv, environ
from dotenv import load_dotenv

load_dotenv()

class Var(object):
    API_ID = int(getenv('API_ID'))
    API_HASH = str(getenv('API_HASH'))
    BOT_TOKEN = getenv('BOT_TOKEN')
    SESSION = str(getenv('SESSION'))
    SUDO =  list(int(x) for x in getenv('SUDO', '').split())
    FPS = int(getenv('FPS', 20))
    WIDTH = int(getenv('WIDTH', 854))
    HEIGHT = int(getenv('HEIGHT', 480))
    BITRATE = int(getenv('BITRATE', 48000))