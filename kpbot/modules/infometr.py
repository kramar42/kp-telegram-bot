import hashlib

from telegram.ext import CommandHandler

from .. import reply

DIGITS = 3


def check_info(text, chat_id):
    text = f"{chat_id}:{text}"
    return int(hashlib.sha512(text.encode('utf8')).hexdigest()[0:DIGITS], 16) % 101


async def infometr(update, context):
    args = context.args
    if len(args) == 0:
        response = update.effective_message.reply_text('/infa <text>')
        await reply(response)
        return

    info = check_info(' '.join(args), update.effective_message.chat_id)
    response = update.effective_message.reply_text(f'Інфа {info}%')
    await reply(response)


handlers = [CommandHandler('infa', infometr)]
