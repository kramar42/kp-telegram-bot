import logging

from yaml import safe_load

log = logging.getLogger(__name__)

_aliases = {}


def parse_aliases(filename):
    if not filename:
        log.info("skipped import aliases")
        return

    with open(filename) as f:
        aliases = safe_load(f)
        num_aliases = sum(len(x) for x in aliases.values())
        log.info(f"imported {num_aliases} aliases from {filename}")

        global _aliases
        _aliases.update(aliases)


def get_chat_aliases(chat_id):
    global _aliases
    return _aliases.get(chat_id, {})


def get_alias(chat_id, user_id):
    return get_chat_aliases(chat_id).get(user_id)
