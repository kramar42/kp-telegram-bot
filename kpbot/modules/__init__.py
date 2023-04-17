from . import bomb_word, chat, infometr, moskaliki, sasai, say, timer


def get_handlers():
    modules = [bomb_word, chat, infometr, sasai, say, timer, moskaliki]
    return [handler for m in modules for handler in getattr(m, "handlers", [])]
