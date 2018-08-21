#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import json
import logging
import os
import re

import spotipy
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from gtts import gTTS
from spotipy.oauth2 import SpotifyClientCredentials
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

SPOTIFY_ID = os.environ['SPOTIFY_ID']
SPOTIFY_SECRET = os.environ['SPOTIFY_SECRET']

# youtube api
PLAYLIST_ID = os.environ['PLAYLIST_ID']
BOT_TOKEN = os.environ['BOT_TOKEN']
#DEVELOPER_KEY = ''

CLIENT_SECRETS_FILE = 'client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/youtube']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'


all_users = []
with open('users.txt') as file:
    all_users += ['@' + line.rstrip('\n') for line in file]
all_ids = {}
with open('users.json') as file:
    all_ids.update(json.load(file))
not_pidors = set()
pidor_active = False
pidor_user = None
jobs = None


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
    #youtube = build(API_SERVICE_NAME, API_VERSION, developerKey=DEVELOPER_KEY)
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


# bot api

def start(bot, update):
    update.message.reply_text('Здаровки')

def help(bot, update):
    update.message.reply_text('RTFM')

def echo(bot, update):
    global not_pidors
    global pidor_active
    global pidor_user

    bot.latest_update = datetime.datetime.now()
    entities = update.message.parse_entities().values()
    if '#нарубите' in entities:
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', update.message.text)
        for url in urls:
            if 'spotify' in url:
                url = youtube_search(spotify_query(url))
            if 'youtube' in url.lower():
                url = re.search('watch?.*v=(.{11}).*', url).group(1)

            add_to_playlist(url)
            #update.message.reply_text('added video: ' + url)
        if len(urls) == 0:
            bot.send_message(update.message.chat_id, 'https://www.youtube.com/playlist?list=' + PLAYLIST_ID, disable_web_page_preview=True)

    if '#скажи' in entities:
        text = update.message.text[7:]
        tts = gTTS(text=text, lang='ru')
        tts.save("speech.mp3")
        #bot.send_audio(chat_id=update.message.chat_id, audio=open('speech.mp3', 'rb'))
        bot.send_voice(chat_id=update.message.chat_id, voice=open('speech.mp3', 'rb'))

    if '#таймер' in entities:
        amount = float(update.message.text[8:])

        if amount < 2. or amount > 20.:
            update.message.reply_text('только пидоры ставят такие таймеры')
            #return

        if pidor_active:
            update.message.reply_text(pidor_user + ' уже запустил таймер')
            return

        update.message.reply_text('bomb has been planted')
        pidor_active = True
        pidor_user = update.message.from_user.name
        not_pidors = set()
        not_pidors.add(pidor_user)
        jobs.run_once(pidors_reminder_callback, 60 * (amount - 1), context=update.message.chat_id)
        jobs.run_once(pidors_callback, 60 * amount, context=update.message.chat_id)

    if '#айди' in entities:
        update.message.reply_text(update.message.from_user.id)

    if 'пидор' in update.message.text.lower() or 'пидр' in update.message.text.lower() or 'пiдор' in update.message.text.lower():
        not_pidors.add(update.message.from_user.name)
        #not_pidors.add(update.message.from_user.id)
        print(update.message.from_user.name + ' теперь не пидор')


def pidors_reminder_callback(bot, job):
    bot.send_message(chat_id=job.context, text='Осталась минутка, детишки')


def pidors_callback(bot, job):
    global pidor_active

    text = 'А вот и список пидарёх: '
    for user in all_users:
        if user not in not_pidors:
            text += user + ', '
            
    for user_id in all_ids:
        if user_id not in not_pidors:
            text += all_ids[user_id] + ', '
            try:
                #bot.send_message(chat_id=str(user_id), text='Гони юзернейм, пидор')
                pass
            except Exception:
                pass

    pidor_active = False
    bot.send_message(chat_id=job.context, text=text[:-2])


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    global jobs

    #os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    updater = Updater(BOT_TOKEN)
    jobs = updater.job_queue
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))

    dp.add_handler(MessageHandler(Filters.text, echo))
    #dp.add_handler(InlineQueryHandler(inlinequery))

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
