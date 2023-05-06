import hashlib

from telegram.ext import CommandHandler

from ..db import send_and_archive

DIGITS = 3


def check_info(text, chat_id):
    text = f"{chat_id}:{text}"
    return int(hashlib.sha512(text.encode('utf8')).hexdigest()[0:DIGITS], 16) % 101


async def infometr(update, context):
    args = context.args
    if len(args) == 0:
        reply = update.effective_message.reply_text('/infa <text>')
        await send_and_archive(reply)
        return

    info = check_info(' '.join(args), update.effective_message.chat_id)
    reply = update.effective_message.reply_text(f'Інфа {info}%')
    await send_and_archive(reply)


handlers = [CommandHandler('infa', infometr)]
