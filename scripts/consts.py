from enum import Enum


class MessageTypes(str, Enum):
    PUBLIC_KEY = 'PUBLIC_KEY'
    SYM_KEY = 'SYM_KEY'
    USERNAME = 'USERNAME'
    PASSWORD = 'PASSWORD'
    CONNECTED = 'CONNECTED'
    MESSAGE = 'MESSAGE'
    SERVER_CLOSED = 'SERVER_CLOSED'
    KICK = 'KICK'
    BAN = 'BAN'
