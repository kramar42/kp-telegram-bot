# -*- coding: utf-8 -*-

import hashlib
from telegram.ext import CommandHandler

from .db import client as db_client

DIGITS = 3


def check_info(text):
    return int(hashlib.sha512(text.encode('utf8')).hexdigest()[0:DIGITS], 16) % 101


def infometr(update, context):
    args = context.args
    if len(args) == 0:
        reply = update.message.reply_text('/infa <text>')
        db_client.save_message(reply)
        return

    text = ' '.join(args)
    infa = check_info(text)
    reply = update.message.reply_text(f'Инфа {infa}%')
    db_client.save_message(reply)


handlers = [CommandHandler('infa', infometr)]
