#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import random
import time

import telegram
from telegram.ext import CommandHandler


WAIT_AMOUNT = 60 * 60 * 2

all_ids = {}
with open('userids.json') as file:
    all_ids.update(json.load(file))


def pidors_reminder_callback(bot, job):
    bot.send_message(chat_id=job.context['chat_id'], text='Осталась минутка, детишки')


def pidors_reminder_last_callback(bot, job):
    bot.send_message(chat_id=job.context['chat_id'], text='10 сек и Вы пидоры, господа: ' + pidors_list_text(),
                     parse_mode=telegram.ParseMode.MARKDOWN)


def pidors_list_text(not_pidors):
    names = ['[%s](tg://user?id=%s)' % (all_ids[id], id) for id in all_ids.keys() if id not in not_pidors]
    random.shuffle(names)
    return ', '.join(names)


def pidors_callback(bot, job):
    text = 'А вот и список пидарёх: ' + pidors_list_text(job.context['not_pidors'])
    del job.context['pidor_active']
    if len(job.context['not_pidors']) == 1:
        not_pidor = job.context['not_pidors'].pop()
        bot.send_message(job.context['chat_id'],
                         'Sector clear. [%s](tg://user?id=%s) единственный не пидор.' % (all_ids[not_pidor], not_pidor),
                         telegram.ParseMode.MARKDOWN)
        bot.send_sticker(job.context['chat_id'], 'CAADBQADpgMAAukKyAN5s5AIa4Wx9AI')
    else:
        bot.send_message(chat_id=job.context['chat_id'], text=text,
                         parse_mode=telegram.ParseMode.MARKDOWN)


def timer(bot, update, args, job_queue, chat_data):
    if len(args) == 0:
        args = ['']
    try:
        amount = float(args[0])
    except (IndexError, ValueError):
        update.message.reply_text('/timer <float: minutes>')
        return

    if 'bomb_pidors' in chat_data and update.message.from_user.id in chat_data['bomb_pidors']:
        update.message.reply_text('Пидоры не могут ставить таймеры')
        return

    if amount < 15. or amount > 60.:
        update.message.reply_text('Только пидоры ставят такие таймеры')
        return
    if 'pidor_active' in chat_data:
        pidor_user = str(chat_data['pidor_user'])
        update.message.reply_text('%s уже запустил таймер' % all_ids[pidor_user])
        return
    if 'pidor_time' in chat_data and time.time() - chat_data['pidor_time'] < WAIT_AMOUNT:
        update.message.reply_text('Заебали со своими таймерами')
        return

    chat_id = update.message.chat_id
    chat_data['pidor_active'] = True
    chat_data['pidor_user'] = update.message.from_user.id
    chat_data['pidor_time'] = time.time()
    chat_data['not_pidors'] = set()
    # FIX ids from json file are parsed as strings
    chat_data['not_pidors'].add(str(update.message.from_user.id))
    chat_data['chat_id'] = chat_id
    job_queue.run_once(pidors_reminder_callback, 60 * (amount - 1), context=chat_data)
    job_queue.run_once(pidors_callback, 60 * amount, context=chat_data)
    update.message.reply_text('Bomb has been planted')


def start():
    return [CommandHandler('timer', timer, pass_args=True, pass_job_queue=True, pass_chat_data=True)]
