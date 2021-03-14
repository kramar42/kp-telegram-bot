# -*- coding: utf-8 -*-

import json
import random
import time

import telegram
from telegram.ext import CommandHandler

from .db import client as db_client


WAIT_AMOUNT = 60 * 60 * 2

all_ids = {}
with open('userids.json') as file:
    all_ids.update(json.load(file))


def pidors_reminder_callback(context):
    msg = context.bot.send_message(chat_id=context['chat_id'], text='Осталась минутка, детишки')
    db_client.save_message(msg)


def pidors_reminder_last_callback(context):
    msg = context.bot.send_message(chat_id=context['chat_id'], text='10 сек и Вы пидоры, господа: ' + pidors_list_text(),
                                   parse_mode=telegram.ParseMode.MARKDOWN)
    db_client.save_message(msg)


def pidors_list_text(not_pidors):
    names = [f'[{all_ids[id]}](tg://user?id={id})' for id in all_ids if id not in not_pidors]
    random.shuffle(names)
    return ', '.join(names)


def pidors_callback(context):
    text = 'А вот и список пидарёх: ' + pidors_list_text(context['not_pidors'])
    del context['pidor_active']
    if len(context['not_pidors']) == 1:
        not_pidor = context['not_pidors'].pop()
        msg = context.bot.send_message(context['chat_id'],
                                       f'Sector clear. [{all_ids[not_pidor]}](tg://user?id={not_pidor}) единственный не пидор.',
                                       telegram.ParseMode.MARKDOWN)
        db_client.save_message(msg)
        msg = context.bot.send_sticker(context['chat_id'], 'CAADBQADpgMAAukKyAN5s5AIa4Wx9AI')
        db_client.save_message(msg)
    else:
        msg = context.bot.send_message(chat_id=context['chat_id'], text=text,
                                       parse_mode=telegram.ParseMode.MARKDOWN)
        db_client.save_message(msg)


def timer(update, context):
    args = context.args
    if len(args) == 0:
        args = ['']
    try:
        amount = float(args[0])
    except (IndexError, ValueError):
        reply = update.message.reply_text('/timer <float: minutes>')
        db_client.save_message(reply)
        return

    chat_data = context.chat_data
    if 'bomb_pidors' in chat_data and update.message.from_user.id in chat_data['bomb_pidors']:
        reply = update.message.reply_text('Пидоры не могут ставить таймеры')
        db_client.save_message(reply)
        return

    if amount < 15. or amount > 60.:
        reply = update.message.reply_text('Только пидоры ставят такие таймеры')
        db_client.save_message(reply)
        return
    if 'pidor_active' in chat_data:
        pidor_user = str(chat_data['pidor_user'])
        reply = update.message.reply_text('{} уже запустил таймер'.format(all_ids[pidor_user]))
        db_client.save_message(reply)
        return
    if 'pidor_time' in chat_data and time.time() - chat_data['pidor_time'] < WAIT_AMOUNT:
        reply = update.message.reply_text('Заебали со своими таймерами')
        db_client.save_message(reply)
        return

    chat_id = update.message.chat_id
    chat_data['pidor_active'] = True
    chat_data['pidor_user'] = update.message.from_user.id
    chat_data['pidor_time'] = time.time()
    chat_data['not_pidors'] = set()
    # FIX ids from json file are parsed as strings
    chat_data['not_pidors'].add(str(update.message.from_user.id))
    chat_data['chat_id'] = chat_id
    context.job_queue.run_once(pidors_reminder_callback, 60 * (amount - 1), context=chat_data)
    context.job_queue.run_once(pidors_callback, 60 * amount, context=chat_data)
    reply = update.message.reply_text('Bomb has been planted')
    db_client.save_message(reply)


handlers = [CommandHandler('timer', timer)]
