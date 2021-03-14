# -*- coding: utf-8 -*-

import logging

from pymongo import MongoClient
from telegram.ext import MessageHandler, Filters


class DatabaseClient:
    def __init__(self):
        self._connected = False
        self._log = logging.getLogger()

    @property
    def connected(self):
        return self._connected

    def connect(self, uri):
        try:
            self._client = MongoClient(uri, serverSelectionTimeoutMS=2000)
            self._client.server_info() # check connection
            self._connected = True
            self._log.info(f'connected to {uri}')
        except:
            self._log.error(f"can't connect to {uri}")

    def save_message(self, message):
        if not self.connected:
            return

        msg = self._process_message(message)

        db_name = f'chat_{message.chat.id}'
        messages = self._client[db_name]['messages']
        messages.insert_one(msg)

    def _process_message(self, message):
        fields_to_remove = [
            'chat',
            'delete_chat_photo',
            'group_chat_created',
            'supergroup_chat_created',
            'channel_chat_created'
        ]
        fields_to_remove_if_empty = [
            'entities',
            'caption_entities',
            'photo',
            'new_chat_members',
            'new_chat_photo'
        ]

        msg = message.to_dict()
        for field in fields_to_remove:
            msg.pop(field, None)

        for field in fields_to_remove_if_empty:
            if not msg[field]:
                msg.pop(field, None)

        if 'reply_to_message' in msg:
            msg['reply_to_message'] = self._process_message(message.reply_to_message)

        return msg


client = DatabaseClient()


def archive(update, context):
    client.save_message(update.effective_message)


handlers = [MessageHandler(Filters.all, archive)]
