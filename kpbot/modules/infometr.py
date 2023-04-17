import hashlib

from telegram.ext import CommandHandler

DIGITS = 3


def check_info(text):
    return int(hashlib.sha512(text.encode('utf8')).hexdigest()[0:DIGITS], 16) % 101


async def infometr(update, context):
    args = context.args
    if len(args) == 0:
        await update.effective_message.reply_text('/infa <text>')
        return

    info = check_info(' '.join(args))
    await update.effective_message.reply_text(f'Інфа {info}%')


handlers = [CommandHandler('infa', infometr)]
