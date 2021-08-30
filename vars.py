from os import getenv, environ
from dotenv import load_dotenv

load_dotenv()

class Var(object):
    API_ID = int(getenv('API_ID'))
    API_HASH = str(getenv('API_HASH'))
    SESSION = str(getenv('SESSION'))
    CHANNEL = int(getenv('BIN_CHANNEL', None))     