# -*- coding: utf-8 -*-

from . import bomb_word
from . import chat
from . import infometr
from . import sasai
from . import say
from . import timer


def get_handlers():
    modules = [bomb_word, chat, infometr, sasai, say, timer]
    return [handler for m in modules for handler in getattr(m, 'handlers', [])]
