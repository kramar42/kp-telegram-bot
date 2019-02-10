#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import time

from telegram.ext import CommandHandler

# Bomb feature:
# once in 24h you can plant word-bomb. If someone in the chat uses this word - he becomes a pidor for 24h

BOMB_TIMEOUT = 60 * 60 * 24
BOMB_PIDOR_TIMEOUT = 60 * 60 * 24
MIN_LENGTH = 4
log = logging.getLogger()


def remove_bomb(bot, job):
    bomber = job.context['bomber']
    chat_data = job.context['chat_data']
    if bomber in chat_data['bombs']:
        word = chat_data['bombs'].pop(bomber)
        log.debug("Bomb %s removed!" % word)


def bomb_triggered(bot, job_queue, update, chat_data, word):
    user_id = update.message.from_user.id

    chat_data['bomb_pidors'][user_id] = time.time()

    if 'not_pidors' in chat_data and str(user_id) in chat_data['not_pidors']:
        chat_data['not_pidors'].remove(str(user_id))

    job_queue.run_once(remove_pidor, BOMB_PIDOR_TIMEOUT, context={'id': user_id, 'chat_data': chat_data})

    update.message.reply_text('Ты обосрался! Слово \"%s\" было бомбой! Теперь ты пидор на целый день! Л*ОХ' % word)


def remove_pidor(bot, job):
    user_id = job.context['id']
    bomb_pidors = job.context['chat_data']['bomb_pidors']

    if user_id in bomb_pidors and time.time() - bomb_pidors[user_id] >= BOMB_PIDOR_TIMEOUT:
        bomb_pidors.pop(user_id)
        log.debug("Pidor removed")
    else:
        log.debug("Pidor checked but not removed!")


def bomb_word(bot, update, args, job_queue, chat_data):
    if len(args) == 0:
        update.message.reply_text('/bomb <word : %d chars min>' % MIN_LENGTH)
        return

    if len(args) > 1:
        update.message.reply_text('Ска, ты тупой? Одно слово бля!')
        return

    word = str(args[0]).lower()
    user_id = update.message.from_user.id

    if 'bombs' not in chat_data:
        chat_data['bombs'] = {}

    if 'bomb_pidors' not in chat_data:
        chat_data['bomb_pidors'] = {}

    log.debug(chat_data['bombs'])
    if user_id in chat_data['bombs']:
        update.message.reply_text('Ска не еби до завтра!')
    elif len(word) < MIN_LENGTH:
        update.message.reply_text('Слово слишком короткое, как и твой член!')
    else:
        chat_data['bombs'][user_id] = word
        chat_data['chat_id'] = update.message.chat_id
        job_queue.run_once(remove_bomb, BOMB_TIMEOUT, context={'bomber': user_id, 'chat_data': chat_data})
        update.message.reply_text('Word bomb has been planted: %s' % word)


def start():
    return [CommandHandler('bomb', bomb_word, pass_args=True, pass_job_queue=True, pass_chat_data=True)]
