# -*- coding: utf-8 -*-

from gtts import gTTS
from telegram.ext import CommandHandler

from .db import client as db_client


def say(update, context):
    text = ' '.join(context.args)
    # TODO guess english text?
    tts = gTTS(text=text, lang='ru')
    # TODO make callback methods async & save speech to temp file with random name
    tts.save('speech.mp3')
    with open('speech.mp3', 'rb') as speech:
        msg = update.effective_chat.send_voice(voice=speech)
        db_client.save_message(msg)


handlers = [CommandHandler('say', say)]
