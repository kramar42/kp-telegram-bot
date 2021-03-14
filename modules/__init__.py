# -*- coding: utf-8 -*-

from . import bomb_word
from . import chat
from . import db
from . import infometr
from . import sasai
from . import say
from . import timer


def _get_handlers():
    modules = [bomb_word, chat, infometr, sasai, say, timer]
    return [handler for m in modules for handler in getattr(m, 'handlers', [])]


def register_handlers(dispatcher):
    for handler in db.handlers:
        dispatcher.add_handler(handler)

    for handler in _get_handlers():
        dispatcher.add_handler(handler, 1)
