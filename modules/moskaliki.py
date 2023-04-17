from datetime import datetime

from telegram.ext import CommandHandler

war_start = datetime.fromisoformat('2022-02-24 04:00:00')


async def moskaliki(update, context):
    seconds = (datetime.now() - war_start).total_seconds()
    number = 0.694 * seconds
    await update.effective_chat.send_message(f'пройшло {number:.1f} москаликів з початку наступу')


handlers = [CommandHandler('moskaliki', moskaliki)]
