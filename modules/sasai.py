#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random

from telegram.ext import CommandHandler


def sasai(bot, update, args):
    who = ' '.join(args)
    if random.randint(0, 1) == 0:
        bot.send_message(chat_id=update.message.chat_id, text='%s наклоняется и делает нежный сасай %s' %
                (who, update.message.from_user.name))
    else:
        bot.send_message(chat_id=update.message.chat_id, text='%s делает первоклассный сасай %s' %
                (update.message.from_user.name, who))


handlers = [CommandHandler('sasai', sasai, pass_args=True)]
