import logging

from telegram.ext import ApplicationBuilder

from . import db
from .alias import parse_aliases
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
    if db_uri:
        db.client.connect(db_uri, "chat_history")
        application.add_handlers(db.client.get_handlers(), -1)

    return application


async def reply(reply):
    message = await reply
    await db.client.archive(message)
