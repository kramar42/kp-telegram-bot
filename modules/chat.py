#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

from telegram.ext import MessageHandler, Filters

from module import get_module


def chat(bot, update, chat_data):
    entities = update.message.parse_entities().values()
    music = get_module('music')
    if '#нарубите' in entities and music:
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', update.message.text)
        for url in urls:
            if 'spotify' in url:
                url = music.youtube_search(music.spotify_query(url))
            if 'youtube' in url.lower():
                url = re.search('watch?.*v=(.{11}).*', url).group(1)

            music.add_to_playlist(url)
        if len(urls) == 0:
            bot.send_message(update.message.chat_id, 'https://www.youtube.com/playlist?list=' + PLAYLIST_ID, disable_web_page_preview=True)

    if 'pidor_active' in chat_data:
        text = update.message.text.lower()
        for pidor_str in ['пидор', 'пидар', 'пидр', 'пидорас', 'підор', 'підар', 'підр', 'підорас', 'підерас']:
            if 'не ' + pidor_str in text:
                # FIX
                chat_data['not_pidors'].add(str(update.message.from_user.id))
                return


def start():
    return [MessageHandler(Filters.text, chat, pass_chat_data=True)]
