from . import bomb_word
from . import chat
from . import infometr
from . import sasai
from . import say
from . import timer
from . import moskaliki


def get_handlers():
    modules = [bomb_word, chat, infometr, sasai, say, timer, moskaliki]
    return [handler for m in modules for handler in getattr(m, 'handlers', [])]
