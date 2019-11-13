#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import subprocess

from telegram import ChatMember
from telegram.ext import Updater, CommandHandler

from module import manager


def error(bot, update, error):
    logging.getLogger().error(error)


def reload(bot, update):
    chat_member = bot.get_chat_member(update.message.chat_id, update.message.from_user.id)
    log = logging.getLogger()
    log.warning("reload request received from '%s'", chat_member.user.username)

    if chat_member.status in [ChatMember.ADMINISTRATOR, ChatMember.CREATOR]:
        log.info('reloading modules')
        subprocess.call(["git", "pull"])
        manager.reload_modules()
        update.message.reply_text('done')
    else:
        log.warning("user doesn't have permissions")
        update.message.reply_sticker('CAADAgADLwEAAnEVJwABIQFxj4o5xLkC', reply_to_message_id=False)


def main():
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s][%(module)s][%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    manager.import_new_modules()

    updater = Updater(os.environ['BOT_TOKEN'])
    dispatcher = updater.dispatcher
    # add core handlers
    dispatcher.add_error_handler(error)
    dispatcher.add_handler(CommandHandler('reload', reload))
    # start all modules
    manager.start_modules(dispatcher)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
