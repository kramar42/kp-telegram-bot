# -*- coding: utf-8 -*-

import logging
import os

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
    updater = Updater(bot_token)
    updater.dispatcher.add_error_handler(error)

    for handler in modules.get_handlers():
        updater.dispatcher.add_handler(handler)
    log.info('registered all handlers')

    updater.start_polling()
    log.info('bot started')
    updater.idle()


if __name__ == '__main__':
    main()
