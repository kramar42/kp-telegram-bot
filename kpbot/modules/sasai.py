import random

from telegram.ext import CommandHandler

from .. import reply


async def sasai(update, context):
    who = ' '.join(context.args)
    if random.randint(0, 1) == 0:
        response = update.effective_chat.send_message(f'{who} нахиляється і робить ніжний сасай {update.effective_message.from_user.name}')
    else:
        response = update.effective_chat.send_message(f'{update.effective_message.from_user.name} робить бездоганний сасай {who}')

    await reply(response)


handlers = [CommandHandler('sasai', sasai)]
