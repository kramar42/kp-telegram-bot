from gtts import gTTS
from telegram.ext import CommandHandler

from ..db import send_and_archive


async def say(update, context):
    text = ' '.join(context.args)
    tts = gTTS(text=text, lang='uk')
    # TODO make callback methods async & save speech to temp file with random name
    tts.save('speech.mp3')
    with open('speech.mp3', 'rb') as speech:
        reply = update.effective_chat.send_voice(voice=speech)
        await send_and_archive(reply)


handlers = [CommandHandler('say', say)]
