import logging

from telegram.ext import CommandHandler

from .. import reply
from .ai import DEFAULT_SYSTEM_PROMPT

ADMINS = {50239, 2561393}

log = logging.getLogger(__name__)


async def get_ai_prompt(update, context):
    if update.effective_message.from_user.id not in ADMINS:
        response = update.effective_message.reply_text("піпка ще не виросла такі команди викликати")
        await reply(response)
        return

    response = DEFAULT_SYSTEM_PROMPT
    await reply(update.effective_message.reply_text(response))


async def set_ai_prompt(update, context):
    if update.effective_message.from_user.id not in ADMINS:
        response = update.effective_message.reply_text("піпка ще не виросла такі команди викликати")
        await reply(response)
        return

    new_prompt = update.effective_message.text.replace("/admin_set_ai_prompt", "", 1)
    global DEFAULT_SYSTEM_PROMPT
    DEFAULT_SYSTEM_PROMPT = new_prompt
    log.warning(f"changed AI prompt to: {new_prompt}")

    response = update.effective_message.reply_text("updated AI prompt")
    await reply(response)


handlers = [
    CommandHandler("admin_get_ai_prompt", get_ai_prompt),
    CommandHandler("admin_set_ai_prompt", set_ai_prompt),
]
