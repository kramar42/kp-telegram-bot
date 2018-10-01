#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import subprocess

from telegram import ChatMember
from telegram.ext import Updater, CommandHandler

from module import load_modules


_BOT_TOKEN = os.environ['BOT_TOKEN']

updater = Updater(_BOT_TOKEN)
dispatcher = updater.dispatcher


def error(bot, update, error):
    logging.getLogger().error(error)


def reload(bot, update):
    chat_member = bot.get_chat_member(update.message.chat_id, update.message.from_user.id)
    logging.getLogger().warning("reload request received from '%s'", chat_member.user.username)

    if chat_member.status in [ChatMember.ADMINISTRATOR, ChatMember.CREATOR]:
        logging.getLogger().info('reloading modules')
        subprocess.call(["git", "pull"])
        load_modules()
        update.message.reply_text('done')
    else:
        logging.getLogger().warning("user doesn't have permissions")
        update.message.reply_sticker('CAADAgADLwEAAnEVJwABIQFxj4o5xLkC', reply_to_message_id=False)


def start():
    dispatcher.add_error_handler(error)
    updater.start_polling()
    return [CommandHandler('reload', reload)]
