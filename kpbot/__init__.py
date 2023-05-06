import logging

from telegram.ext import ApplicationBuilder

from .alias import parse_aliases
from .db import connect, handlers as db_handlers
from .modules import get_handlers

log = logging.getLogger(__name__)


async def _error(update, context):
    log.error("exception while handling an update:", exc_info=context.error)


def create_app(token: str, aliases: str | None = None, db_uri: str | None = None):
    application = ApplicationBuilder().token(token).build()
    application.add_error_handler(_error)

    handlers = get_handlers()
    application.add_handlers(handlers)
    log.info("registered all handlers")

    parse_aliases(aliases)
    if connect(db_uri):
        application.add_handlers(db_handlers, -1)

    return application
