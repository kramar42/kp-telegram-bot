#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os

from telegram.ext import Updater, CommandHandler

from module import load_modules


def error(bot, update, error):
    logging.getLogger().error(error)


def main():
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s][%(module)s][%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    bot_token = os.environ['BOT_TOKEN']
    updater = Updater(bot_token)

    updater.dispatcher.add_error_handler(error)
    load_modules(updater.dispatcher)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
