import logging
import os
import sys

from telegram.ext import ApplicationBuilder

import modules


async def error(update, context):
    logging.getLogger().error("exception while handling an update:", exc_info=context.error)


def main():
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s][%(module)s][%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    log = logging.getLogger()

    bot_token = os.environ['BOT_TOKEN']
    if not bot_token:
        log.fatal('empty BOT_TOKEN')
        sys.exit(1)

    application = ApplicationBuilder().token(bot_token).build()
    application.add_error_handler(error)

    handlers = modules.get_handlers()
    application.add_handlers(handlers)
    log.info('registered all handlers')

    application.run_polling()


if __name__ == '__main__':
    main()
