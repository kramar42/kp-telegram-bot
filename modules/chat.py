# -*- coding: utf-8 -*-

import logging
import re

from telegram.ext import MessageHandler, Filters

from . import bomb_word
from .infometr import check_info


def chat(bot, update, chat_data, job_queue):
    if check_info(update.message.text) == 100:
        update.message.reply_text('Инфа 100%')

    if 'bombs' in chat_data:
        text = bomb_word.normalize_text(update.message.text)
        bombers = set()
        for bomber, bombinfo in chat_data['bombs'].items():
            logging.getLogger().debug('word: ' + bombinfo['word'])
            if bombinfo['word'] in text: bombers.add(bomber)
        bombers and bomb_word.trigger_bombers(bot, job_queue, update, chat_data, bombers)

    if 'pidor_active' in chat_data:
        if 'bomb_pidors' not in chat_data or update.message.from_user.id not in chat_data['bomb_pidors']:
            text = update.message.text.lower()
            for pidor_str in ['пидор', 'пидар', 'пидр', 'пидорас', 'підор', 'підар', 'підр', 'підорас', 'підерас']:
                if 'не ' + pidor_str in text:
                    # FIX
                    chat_data['not_pidors'].add(str(update.message.from_user.id))
                    return


handlers = [MessageHandler(Filters.text, chat, pass_chat_data=True, pass_job_queue=True)]
