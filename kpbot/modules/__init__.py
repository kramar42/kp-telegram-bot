from . import ai, bomb_word, chat, infometr, sasai, say, timer


def get_handlers():
    modules = [ai, bomb_word, chat, infometr, sasai, say, timer]
    return [handler for m in modules for handler in getattr(m, "handlers", [])]
