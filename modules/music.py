#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

import spotipy
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from spotipy.oauth2 import SpotifyClientCredentials
from telegram.ext import CommandHandler


SPOTIFY_ID = os.environ['SPOTIFY_ID']
SPOTIFY_SECRET = os.environ['SPOTIFY_SECRET']

# youtube api
PLAYLIST_ID = os.environ['PLAYLIST_ID']

CLIENT_SECRETS_FILE = 'client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/youtube']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'


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
