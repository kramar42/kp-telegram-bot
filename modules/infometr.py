#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
from telegram.ext import CommandHandler

DIGITS = 3


def check_info(text):
    return int(hashlib.sha512(text.encode('utf8')).hexdigest()[0:DIGITS], 16) % 101


def infometr(bot, update, args):
    if len(args) == 0:
        update.message.reply_text('/infa <text>')
        return

    text = ' '.join(args)
    update.message.reply_text('Инфа %d%%' % check_info(text))


handlers = [CommandHandler('infa', infometr, pass_args=True)]
