# -*- coding: utf-8 -*-

import logging
import time
import json # For debugging purposes only.
from collections import defaultdict

import telegram
from telegram.ext import CommandHandler

# Bomb feature:
# once in 24h you can plant word-bomb. If someone in the chat uses this word - he becomes a pidor for 24h

BOMB_TIMEOUT = 60 * 60 * 24 # in seconds
BOMB_PIDOR_TIMEOUT = 60 * 60 * 24
MIN_LENGTH = 3
CASE_SENSITIVE_LETTERS = {'B': 'В', 'H': 'Н', 'M': 'М', 'T': 'Т', 'u': 'и', 'r': 'г'}
COMMON_LETTERS = {'a': 'а', 'c': 'с', 'e': 'е', 'i': 'і', 'k': 'к', 'o': 'о', 'p': 'р',
                  'x': 'х', 'y': 'у', '6': 'б', '0': 'о'}

log = logging.getLogger()


def initialize_containers(chat_data):
    if 'bombs' not in chat_data:
        chat_data['bombs'] = {}

    if 'bomb_pidors' not in chat_data:
        chat_data['bomb_pidors'] = {}

    if 'users' not in chat_data:
        chat_data['users'] = {}
        with open('userids.json') as file:
            chat_data['users'].update(json.load(file))


def normalize_text(text):
    case_sensitive = [CASE_SENSITIVE_LETTERS.get(c) or c for c in text]
    return ''.join([COMMON_LETTERS.get(c.lower()) or c.lower() for c in case_sensitive]).split()


def get_username_by_id(chat_data, user_id):
    return chat_data['users'].get(str(user_id), str(user_id))


# Generates info about active bombs
def bomb_info_payload_generator(chat_data):
    per_bomb_reply_payload_list = []
    for user_id, bombinfo in chat_data['bombs'].items():
        # setting the bomb author
        display_user_name = get_username_by_id(chat_data, user_id)
        # setting casualties info
        casualties_count = 0
        casualties_list = []
        for user, count in bombinfo['casualties'].items():
            casualties_list.append('{} ({})'.format(get_username_by_id(chat_data, user), count))
            casualties_count += count
        # setting an expiration message
        mins_left = (bombinfo['expiration_timestamp'] - time.time()) / 60
        expiration_readable = '%dh %dm' % (mins_left / 60, mins_left % 60)
        # combining pieces into the single message and sending
        casualties_list_str = '\n          '.join(casualties_list)
        per_bomb_reply_payload_list.append(f'''
     бімба: {bombinfo['word']}
    бімбер: {display_user_name}
     жертв: {casualties_count}
залишилось: {expiration_readable}
    сосєри: {casualties_list_str}
''')

    reply_payload = '```'
    reply_payload += '\n'.join(per_bomb_reply_payload_list)
    reply_payload += '\n```'
    return reply_payload


def remove_bomb(context):
    bomber = context['bomber']
    chat_data = context['chat_data']
    if bomber in chat_data['bombs']:
        bombinfo = chat_data['bombs'].pop(bomber)
        log.debug(f"Bomb {bombinfo['word']} removed!")


def trigger_bombers(update, context, bombers):
    user_id = update.message.from_user.id

    chat_data = context.chat_data
    chat_data['bomb_pidors'][user_id] = time.time()

    if 'not_pidors' in chat_data and str(user_id) in chat_data['not_pidors']:
        chat_data['not_pidors'].remove(str(user_id))

    # updating casualties info
    for bomber in bombers:
        chat_data['bombs'][bomber]['casualties'][user_id] += 1

    context.job_queue.run_once(remove_pidor, BOMB_PIDOR_TIMEOUT, context={'id': user_id, 'chat_data': chat_data})

    if len(bombers) == 1:
        msg = 'Ти обісрався! Слово \"{}\" було бімбою! Тепер ти підор на цілий день! Л*ОХ'.format(
            chat_data['bombs'][bomber]['word'])
        update.message.reply_text(msg)
    else:
        msg = 'Та ти обхезався! Слова \"{}\" були заміновані! ЛО*Х'.format(
            ', '.join(chat_data['bombs'][b]['word'] for b in bombers))
        update.message.reply_text(msg)


def remove_pidor(context):
    user_id = context['id']
    bomb_pidors = context['chat_data']['bomb_pidors']

    if user_id in bomb_pidors and time.time() - bomb_pidors[user_id] >= BOMB_PIDOR_TIMEOUT:
        bomb_pidors.pop(user_id)
        log.debug("Pidor removed")
    else:
        log.debug("Pidor checked but not removed!")


def bomb_word(update, context):
    args = context.args
    if len(args) == 0:
        update.message.reply_text(f'/bomb <word : {MIN_LENGTH} chars min>')
        return

    if len(args) > 1:
        update.message.reply_text('Ска, ти тупий? Одне слово бля!')
        return

    word = normalize_text(str(args[0]))[0]
    user_id = update.message.from_user.id

    chat_data = context.chat_data
    initialize_containers(chat_data)

    log.debug(chat_data['bombs'])
    if user_id in chat_data['bombs']:
        update.message.reply_text('Ска не їби до завтра!')
    elif len(word) < MIN_LENGTH:
        update.message.reply_text('Слово занадто коротке, як і твій член!')
    else:
        chat_data['bombs'][user_id] = {}
        chat_data['bombs'][user_id]['word'] = word
        chat_data['bombs'][user_id]['casualties'] = defaultdict(int)
        chat_data['bombs'][user_id]['expiration_timestamp'] = time.time() + BOMB_TIMEOUT
        chat_data['chat_id'] = update.message.chat_id
        context.job_queue.run_once(remove_bomb, BOMB_TIMEOUT, context={'bomber': user_id, 'chat_data': chat_data})
        update.message.reply_text(f'Word bomb has been planted: {word}')


def bomb_info(update, context):
    chat_data = context.chat_data
    initialize_containers(chat_data)
    if not chat_data['bombs']:
        update.message.reply_text('бімб нема лел кок')
        return

    reply_payload = bomb_info_payload_generator(chat_data)

    update.message.reply_text(reply_payload, parse_mode=telegram.ParseMode.MARKDOWN)


handlers = [CommandHandler('bomb', bomb_word),
            CommandHandler('bombinfo', bomb_info)]
