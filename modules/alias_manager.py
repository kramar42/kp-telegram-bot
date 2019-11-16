#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from telegram.ext import CommandHandler, Filters, MessageHandler

# This module is responsible for managing chat members' aliases.

MAX_ALIAS_LENGTH = 24

log = logging.getLogger()


def initialize_containers(chat_data):
    if 'user_aliases' not in chat_data:
        chat_data['user_aliases'] = {}


# Checks if user lis present in user_aliases. If no - adds user's full name as default alias.
def add_unknown_user(bot, update, chat_data):
    initialize_containers(chat_data)
    user_id = update.message.from_user.id
    if user_id not in chat_data['user_aliases']:
        chat_data['user_aliases'][user_id] = update.message.from_user.full_name
        # Message is suppressed for now. Uncomment once the feature is fully enabled and used by other modules.
        # update.message.reply_text(
        #     'Оп, а это шо за пидарок? Я буду называть тебя %s.'
        #     ' Что бы поменять это напиши "/alias_update %d Пидр-Хуидр"' %
        #     (update.message.from_user.full_name, user_id))


# Update alias. Returns an error if one of the following conditions has been met:
# - Call format doesn't match /alias_update <int: user_id> <new_alias>.
# - Alias is too long.
# - Alias is used by someone in the chat.
def alias_update(bot, update, args, chat_data):
    if len(args) < 2:
        args = ['']
    try:
        target_user_id = int(args[0])
    except (IndexError, ValueError):
        update.message.reply_text('Блет, ты што, тупой? /alias_update <int: user_id> <new_alias>')
        return

    target_user_alias = ' '.join(args[1:])
    if len(target_user_alias) > MAX_ALIAS_LENGTH:
        update.message.reply_text('гиперкомпенсация из-за маленькой пипки? давай блядь покороче имя')
        return

    if target_user_alias in list(chat_data['user_aliases'].values()):
        update.message.reply_text('такой алиас уже есть, лохобаза')
        return

    chat_data['user_aliases'][target_user_id] = target_user_alias
    update.message.reply_text('окда')


# Builds the message with mapping of user ids to aliases for known users.
def list_of_known_aliases(chat_data):
    msg = 'вот кого я знаю:\n'
    return msg + '\n'.join(list(map(lambda x: '%d: %s' % (x[0], x[1]), chat_data['user_aliases'].items())))


# Prints list of known aliases.
def alias_list(bot, update, args, chat_data):
    update.message.reply_text(list_of_known_aliases(chat_data))


# Removes user from aliases map for given chat. Returns an error if call format does not match
# /alias_remove <int: user_id>, or if user id was not found in the mapping for this chat.
def alias_remove(bot, update, args, chat_data):
    if len(args) != 1:
        args = ['']
    try:
        target_user_id = int(args[0])
    except (IndexError, ValueError):
        update.message.reply_text('Блет, ты што, тупой? /alias_remove <int: user_id>')
        return

    if target_user_id not in chat_data['user_aliases']:
        msg = "лол, я не знаю никого в этом чате с таким ойди.\n" + list_of_known_aliases(chat_data)
        update.message.reply_text(msg)

    del chat_data['user_aliases'][target_user_id]
    update.message.reply_text('окда')


def start():
    return [MessageHandler(Filters.text, add_unknown_user, pass_chat_data=True),
            CommandHandler('alias_update', alias_update, pass_args=True, pass_chat_data=True),
            CommandHandler('alias_list', alias_list, pass_args=True, pass_chat_data=True),
            CommandHandler('alias_remove', alias_remove, pass_args=True, pass_chat_data=True)
            ]
