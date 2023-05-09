import random

from telegram.ext import CommandHandler

from ..db import send_and_archive


async def sasai(update, context):
    who = ' '.join(context.args)
    if random.randint(0, 1) == 0:
        reply = update.effective_chat.send_message(f'{who} нахиляється і робить ніжний сасай {update.effective_message.from_user.name}')
    else:
        reply = update.effective_chat.send_message(f'{update.effective_message.from_user.name} робить бездоганний сасай {who}')

    await send_and_archive(reply)


handlers = [CommandHandler('sasai', sasai)]
