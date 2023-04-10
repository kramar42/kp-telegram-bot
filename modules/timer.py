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


def pidors_reminder_callback(context):
    context.bot.send_message(chat_id=context['chat_id'], text='Залишилась хвилинка, дітлахи')


def pidors_reminder_last_callback(context):
    context.bot.send_message(chat_id=context['chat_id'], text='10 сек і Ви підори, панове: ' + pidors_list_text(),
                             parse_mode=telegram.ParseMode.MARKDOWN)


def pidors_list_text(not_pidors):
    names = [f'[{all_ids[id]}](tg://user?id={id})' for id in all_ids if id not in not_pidors]
    random.shuffle(names)
    return ', '.join(names)


def pidors_callback(context):
    text = 'А вот и список пидарёх: ' + pidors_list_text(context['not_pidors'])
    del context['pidor_active']
    if len(context['not_pidors']) == 1:
        not_pidor = context['not_pidors'].pop()
        context.bot.send_message(context['chat_id'],
                                 f'Sector clear. [{all_ids[not_pidor]}](tg://user?id={not_pidor}) єдиний не підор.',
                                 telegram.ParseMode.MARKDOWN)
        context.bot.send_sticker(context['chat_id'], 'CAADBQADpgMAAukKyAN5s5AIa4Wx9AI')
    else:
        context.bot.send_message(chat_id=context['chat_id'], text=text,
                                 parse_mode=telegram.ParseMode.MARKDOWN)


def timer(update, context):
    args = context.args
    if len(args) == 0:
        args = ['']
    try:
        amount = float(args[0])
    except (IndexError, ValueError):
        update.message.reply_text('/timer <float: minutes>')
        return

    chat_data = context.chat_data
    if 'bomb_pidors' in chat_data and update.message.from_user.id in chat_data['bomb_pidors']:
        update.message.reply_text('Підори не можуть ставити таймери')
        return

    if amount < 15. or amount > 60.:
        update.message.reply_text('Тількі підори ставлять такі таймери')
        return
    if 'pidor_active' in chat_data:
        pidor_user = str(chat_data['pidor_user'])
        update.message.reply_text('{} вже запустив таймер'.format(all_ids[pidor_user]))
        return
    if 'pidor_time' in chat_data and time.time() - chat_data['pidor_time'] < WAIT_AMOUNT:
        update.message.reply_text('Заїбали зі своїми таймерами')
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
    update.message.reply_text('Bomb has been planted')


handlers = [CommandHandler('timer', timer)]
