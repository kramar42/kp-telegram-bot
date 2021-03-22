# -*- coding: utf-8 -*-

import random

from telegram.ext import CommandHandler


def sasai(update, context):
    who = ' '.join(context.args)
    if random.randint(0, 1) == 0:
        update.effective_chat.send_message(f'{who} наклоняется и делает нежный сасай {update.message.from_user.name}')
    else:
        update.effective_chat.send_message(f'{update.message.from_user.name} делает первоклассный сасай {who}')


handlers = [CommandHandler('sasai', sasai)]
