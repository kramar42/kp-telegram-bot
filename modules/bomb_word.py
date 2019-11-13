#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import time
import json # For debugging purposes only.
import telegram
from collections import defaultdict

from telegram.ext import CommandHandler

# Bomb feature:
# once in 24h you can plant word-bomb. If someone in the chat uses this word - he becomes a pidor for 24h

BOMB_TIMEOUT = 60 * 60 * 24 # in seconds
BOMB_PIDOR_TIMEOUT = 60 * 60 * 24
MIN_LENGTH = 3
log = logging.getLogger()

CASE_SENSITIVE_LETTERS = {'B': 'В', 'H': 'Н', 'M': 'М', 'T': 'Т', 'u': 'и', 'r': 'г'}
COMMON_LETTERS = {'a': 'а', 'c': 'с', 'e': 'е', 'i': 'і', 'k': 'к', 'o': 'о', 'p': 'р',
                  'x': 'х', 'y': 'у', '6': 'б', '0': 'о'}

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
        casualties_list_str = []
        for user, count in bombinfo['casualties'].items():
            casualties_list_str.append('%s (%d)' % (get_username_by_id(chat_data, user), count))
            casualties_count += count
        # setting an expiration message
        mins_left = (bombinfo['expiration_timestamp'] - time.time()) / 60
        expiration_readable = '%dh %dm' % (mins_left / 60, mins_left % 60)
        # combining pieces into the single message and sending
        per_bomb_reply_payload_list.append(''
            + '\n   бомба: %s' % bombinfo['word']
            + '\n  бомбёр: %s' % display_user_name
            + '\n   жертв: %d' % casualties_count
            + '\nосталось: %s' % expiration_readable
            + '\n  сосеры: %s'
            % '\n          '.join(casualties_list_str) if casualties_list_str
                                                       else '')

    reply_payload = '```'
    reply_payload += '\n'.join(per_bomb_reply_payload_list)
    reply_payload += '\n```'
    return reply_payload


def remove_bomb(bot, job):
    bomber = job.context['bomber']
    chat_data = job.context['chat_data']
    if bomber in chat_data['bombs']:
        bombinfo = chat_data['bombs'].pop(bomber)
        log.debug("Bomb %s removed!" % bombinfo['word'])


def trigger_bombers(bot, job_queue, update, chat_data, bombers):
    user_id = update.message.from_user.id

    chat_data['bomb_pidors'][user_id] = time.time()

    if 'not_pidors' in chat_data and str(user_id) in chat_data['not_pidors']:
        chat_data['not_pidors'].remove(str(user_id))

    # updating casualties info
    for bomber in bombers:
        chat_data['bombs'][bomber]['casualties'][user_id] += 1

    job_queue.run_once(remove_pidor, BOMB_PIDOR_TIMEOUT, context={'id': user_id, 'chat_data': chat_data})

    if len(bombers) == 1:
        update.message.reply_text(
            'Ты обосрался! Слово \"%s\" было бомбой! Теперь ты пидор на целый день! Л*ОХ' %
            chat_data['bombs'][bomber]['word'])
    else:
        update.message.reply_text(
            'Да ты обделался! Слова \"%s\" были заминированы! ЛО*Х' %
            ', '.join(map(lambda b: chat_data['bombs'][b]['word'],
                          bombers)))


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

    word = normalize_text(str(args[0]))[0]
    user_id = update.message.from_user.id

    initialize_containers(chat_data)

    log.debug(chat_data['bombs'])
    if user_id in chat_data['bombs']:
        update.message.reply_text('Ска не еби до завтра!')
    elif len(word) < MIN_LENGTH:
        update.message.reply_text('Слово слишком короткое, как и твой член!')
    else:
        chat_data['bombs'][user_id] = {}
        chat_data['bombs'][user_id]['word'] = word
        chat_data['bombs'][user_id]['casualties'] = defaultdict(int)
        chat_data['bombs'][user_id]['expiration_timestamp'] = time.time() + BOMB_TIMEOUT
        chat_data['chat_id'] = update.message.chat_id
        job_queue.run_once(remove_bomb, BOMB_TIMEOUT, context={'bomber': user_id, 'chat_data': chat_data})
        update.message.reply_text('Word bomb has been planted: %s' % word)


def bomb_info(bot, update, args, job_queue, chat_data):
    initialize_containers(chat_data)
    # reply_payload = json.dumps(chat_data['bombs'])
    if not chat_data['bombs']:
        update.message.reply_text('бомб нет лел кок')
        return

    reply_payload = bomb_info_payload_generator(chat_data)

    update.message.reply_text(reply_payload, parse_mode=telegram.ParseMode.MARKDOWN)


def start():
    return [CommandHandler('bomb', bomb_word, pass_args=True, pass_job_queue=True, pass_chat_data=True),
            CommandHandler('bombinfo', bomb_info, pass_args=True, pass_job_queue=True, pass_chat_data=True)]
