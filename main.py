# -*- coding: utf-8 -*-

import logging
import os
import sys

from telegram.ext import Updater, CommandHandler

import modules


def error(update, context):
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

    updater = Updater(bot_token)
    updater.dispatcher.add_error_handler(error)

    db_uri = os.environ.get('DB_URI')
    if db_uri:
        modules.db.client.connect(db_uri)

    modules.register_handlers(updater.dispatcher)
    log.info('registered all handlers')

    updater.start_polling()
    log.info('bot started')
    updater.idle()


if __name__ == '__main__':
    main()
