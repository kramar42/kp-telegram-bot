import random

from telegram.ext import CommandHandler

from .. import reply
from ..alias import get_alias


async def sasai(update, context):
    message = update.effective_message
    author = get_alias(message.chat_id, message.from_user.id) or message.from_user.name[1:]
    target = " ".join(context.args)

    if random.randint(0, 1) == 0:
        text = f"{target} нахиляється і робить ніжний сасай {author}"
    else:
        text = f"{author} робить бездоганний сасай {target}"

    await reply(update.effective_chat.send_message(text))


handlers = [CommandHandler("sasai", sasai)]
