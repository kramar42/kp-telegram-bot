# -*- coding: utf-8 -*-

import logging
import re

from telegram.ext import MessageHandler, Filters

from . import bomb_word
from .db import client as db_client
from .infometr import check_info


def chat(update, context):
    if check_info(update.message.text) == 100:
        reply = update.message.reply_text('Инфа 100%')
        db_client.save_message(reply)


    chat_data = context.chat_data
    if 'bombs' in chat_data:
        text = bomb_word.normalize_text(update.message.text)
        bombers = set()
        for bomber, bombinfo in chat_data['bombs'].items():
            logging.getLogger().debug('word: ' + bombinfo['word'])
            if bombinfo['word'] in text: bombers.add(bomber)
        bombers and bomb_word.trigger_bombers(update, context, bombers)

    if 'pidor_active' in chat_data:
        if 'bomb_pidors' not in chat_data or update.message.from_user.id not in chat_data['bomb_pidors']:
            text = update.message.text.lower()
            for pidor_str in ['пидор', 'пидар', 'пидр', 'пидорас', 'підор', 'підар', 'підр', 'підорас', 'підерас']:
                if 'не ' + pidor_str in text:
                    # FIX
                    chat_data['not_pidors'].add(str(update.message.from_user.id))
                    return


handlers = [MessageHandler(Filters.text & ~Filters.command, chat)]
