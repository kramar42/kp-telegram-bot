import os

import openai
from telegram.ext import CommandHandler

from .. import reply

ALLOWED_CHATS = {-1001127597296}
DEFAULT_SYSTEM_PROMPT = """
Ти жартівливий чат бот, який:
- саркастично відповідає на питання
- задає зустрічні суперечливі питання
- уникає відповіді
- відповідає жартами
"""


def get_response(message, system_prompt=DEFAULT_SYSTEM_PROMPT):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message},
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.5,
        max_tokens=150,
    )
    return response.choices[0].message["content"]


async def ask(update, context):
    if update.effective_chat.id not in ALLOWED_CHATS:
        response = update.effective_chat.send_message("Сорян, фіча не доступна у цьому чаті")
        await reply(response)
        return

    if not os.environ.get("OPENAI_API_KEY"):
        response = update.effective_chat.send_message("А ключика то немає, тому сам розбирайся")
        await reply(response)
        return

    message = " ".join(context.args)
    response = get_response(message)
    await reply(update.effective_chat.send_message(response))


handlers = [CommandHandler("ask", ask)]
