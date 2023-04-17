from gtts import gTTS
from telegram.ext import CommandHandler


async def say(update, context):
    text = ' '.join(context.args)
    tts = gTTS(text=text, lang='uk')
    # TODO make callback methods async & save speech to temp file with random name
    tts.save('speech.mp3')
    with open('speech.mp3', 'rb') as speech:
        await update.effective_chat.send_voice(voice=speech)


handlers = [CommandHandler('say', say)]
