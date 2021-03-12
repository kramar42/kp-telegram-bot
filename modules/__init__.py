from . import bomb_word
from . import chat
from . import infometr
from . import sasai
from . import say
from . import timer


def get_handlers():
    from functools import reduce
    modules = [bomb_word, chat, infometr, sasai, say, timer]
    handlers = [getattr(m, 'handlers', []) for m in modules]
    return reduce(lambda x, y: x + y, handlers)
