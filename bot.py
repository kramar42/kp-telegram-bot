#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import json
import logging
import os
import re
import time
import random

import spotipy
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from gtts import gTTS
from spotipy.oauth2 import SpotifyClientCredentials
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

SPOTIFY_ID = os.environ['SPOTIFY_ID']
SPOTIFY_SECRET = os.environ['SPOTIFY_SECRET']

# youtube api
PLAYLIST_ID = os.environ['PLAYLIST_ID']
BOT_TOKEN = os.environ['BOT_TOKEN']

CLIENT_SECRETS_FILE = 'client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/youtube']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

WAIT_AMOUNT = 60 * 60 * 2

all_ids = {}
with open('userids.json') as file:
    all_ids.update(json.load(file))


def create_youtube_service():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_console()
    return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)


def create_spotify_service():
    client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIFY_ID, client_secret=SPOTIFY_SECRET)
    return spotipy.Spotify(client_credentials_manager=client_credentials_manager)


YOUTUBE = create_youtube_service()
SPOTIFY = create_spotify_service()


def spotify_query(s):
    if s.find('album') > 0:
        results = SPOTIFY.album(s)
        q = results['name']
    elif s.find('track') > 0:
        results = SPOTIFY.track(s)
        q = results['name'] + ' '

    artists = ' '.join(map(lambda a: a['name'], results['artists']))
    return q + ' ' + artists


def youtube_search(q):
    search_response = YOUTUBE.search().list(q=q, part='id,snippet', maxResults=1, type='video').execute()

    if search_response.get('items', []):
        search_result = search_response['items'][0]
        return search_result['id']['videoId']


def build_resource(properties):
  resource = {}
  for p in properties:
    prop_array = p.split('.')
    ref = resource
    for pa in range(0, len(prop_array)):
      is_array = False
      key = prop_array[pa]
      if key[-2:] == '[]':
        key = key[0:len(key)-2:]
        is_array = True

      if pa == (len(prop_array) - 1):
        if properties[p]:
          if is_array:
            ref[key] = properties[p].split(',')
          else:
            ref[key] = properties[p]
      elif key not in ref:
        ref[key] = {}
        ref = ref[key]
      else:
        ref = ref[key]
  return resource


def add_to_playlist(url):
    properties = {
        'snippet.playlistId': PLAYLIST_ID,
        'snippet.resourceId.kind': 'youtube#video',
        'snippet.resourceId.videoId': url,
        'snippet.position': ''
    }
    resource = build_resource(properties)
    YOUTUBE.playlistItems().insert(
        body=resource,
        part='snippet'
    ).execute()


def get_name_or_id(user):
    result = user.username
    if result is None:
        result = str(user.id)
    return result


# bot api

def start(bot, update):
    update.message.reply_text('Здаровки')


def help(bot, update):
    update.message.reply_text('RTFM')

def september_3rd_timeout(bot, job):
    del job.context['september_3rd']

def echo(bot, update, job_queue, chat_data):
    entities = update.message.parse_entities().values()
    if '#нарубите' in entities:
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', update.message.text)
        for url in urls:
            if 'spotify' in url:
                url = youtube_search(spotify_query(url))
            if 'youtube' in url.lower():
                url = re.search('watch?.*v=(.{11}).*', url).group(1)

            add_to_playlist(url)
        if len(urls) == 0:
            bot.send_message(update.message.chat_id, 'https://www.youtube.com/playlist?list=' + PLAYLIST_ID, disable_web_page_preview=True)

    if 'pidor_active' in chat_data:
        text = update.message.text.lower()
        for pidor_str in ['пидор', 'пидар', 'пидр', 'пидорас',
                'підор', 'підар', 'підр', 'підорас', 'підерас']:
            if 'не ' + pidor_str in text:
                # FIX
                chat_data['not_pidors'].add(str(update.message.from_user.id))
                return

    if 'september_3rd' not in chat_data and update.message.date.month == 9 and update.message.date.day == 3:
        chat_data['chat_id'] = update.message.chat_id
        chat_data['september_3rd'] = True
        bot.send_message(chat_data['chat_id'],'''Я календарь переверну,
И снова третье сентября.
На фото я твоё взгляну,
И снова третье сентября.

https://youtu.be/PQ02jz-UgeA''')
        job_queue.run_once(september_3rd_timeout, WAIT_AMOUNT, context=chat_data)


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
        bot.send_message(chat_id=job.context['chat_id'], text='Sector clear',
                         parse_mode=telegram.ParseMode.MARKDOWN)
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

    if amount < 15. or amount > 60.:
        update.message.reply_text('Только пидоры ставят такие таймеры')
        return
    if 'pidor_active' in chat_data:
        update.message.reply_text('% уже запустил таймер' % all_ids[chat_data['pidor_user']])
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


def say(bot, update, args):
    text = ' '.join(args)
    # TODO guess english text?
    tts = gTTS(text=text, lang='ru')
    # TODO make callback methods async & save speech to temp file with random name
    tts.save('speech.mp3')
    with open('speech.mp3', 'rb') as speech:
        bot.send_voice(chat_id=update.message.chat_id, voice=speech)


def sasai(bot, update, args):
    who = ' '.join(args)
    bot.send_message(chat_id=update.message.chat_id, text='%s наклоняется и делает нежный сасай %s' %
            (who, update.message.from_user.name))


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('timer', timer,
                                        pass_args=True,
                                        pass_job_queue=True,
                                        pass_chat_data=True))
    dp.add_handler(CommandHandler('say', say, pass_args=True))
    dp.add_handler(CommandHandler('sasai', sasai, pass_args=True))

    dp.add_handler(MessageHandler(Filters.text, echo, pass_job_queue=True, pass_chat_data=True))
    #dp.add_handler(InlineQueryHandler(inlinequery))

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

