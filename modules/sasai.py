# -*- coding: utf-8 -*-

import random

from telegram.ext import CommandHandler

from .db import client as db_client


def sasai(update, context):
    who = ' '.join(context.args)
    text = ''
    if random.randint(0, 1) == 0:
        text = f'{who} наклоняется и делает нежный сасай {update.message.from_user.name}'
    else:
        text = f'{update.message.from_user.name} делает первоклассный сасай {who}'
    msg = update.effective_chat.send_message(text)
    db_client.save_message(msg)


handlers = [CommandHandler('sasai', sasai)]
