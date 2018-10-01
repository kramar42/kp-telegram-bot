#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gtts import gTTS
from telegram.ext import CommandHandler


def say(bot, update, args):
    text = ' '.join(args)
    # TODO guess english text?
    tts = gTTS(text=text, lang='ru')
    # TODO make callback methods async & save speech to temp file with random name
    tts.save('speech.mp3')
    with open('speech.mp3', 'rb') as speech:
        bot.send_voice(chat_id=update.message.chat_id, voice=speech)


def start():
    return [CommandHandler('say', say, pass_args=True)]
