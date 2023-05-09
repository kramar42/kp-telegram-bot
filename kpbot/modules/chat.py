import logging

from telegram.ext import MessageHandler, filters

from ..db import reply
from . import bomb_word
from .infometr import check_info


async def chat(update, context):
    if check_info(update.effective_message.text, update.effective_message.chat_id) == 100:
        await reply(update.effective_message.reply_text('Інфа 100%'))
    elif any(c in ['Ё', 'ё', 'Ъ', 'ъ', 'Ы', 'ы'] for c in update.effective_message.text):
        await reply(update.effective_message.reply_text('Хуй будеш?'))

    chat_data = context.chat_data
    if 'bombs' in chat_data:
        text = bomb_word.normalize_text(update.effective_message.text)
        bombers = set()
        for bomber, bombinfo in chat_data['bombs'].items():
            logging.getLogger().debug('word: ' + bombinfo['word'])
            if bombinfo['word'] in text:
                bombers.add(bomber)
        if bombers:
            await bomb_word.trigger_bombers(update, context, bombers)

    if 'pidor_active' in chat_data:
        if 'bomb_pidors' not in chat_data or update.effective_message.from_user.id not in chat_data['bomb_pidors']:
            text = update.effective_message.text.lower()
            for pidor_str in ['підор', 'підар', 'підр', 'підорас', 'підерас']:
                if 'не ' + pidor_str in text:
                    chat_data['not_pidors'].add(update.effective_message.from_user.id)
                    return


handlers = [MessageHandler(filters.TEXT & ~filters.COMMAND, chat)]
