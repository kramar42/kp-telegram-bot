import os

import openai
from telegram.ext import CommandHandler

from .. import reply

ALLOWED_CHATS = {-1001127597296}
DEFAULT_SYSTEM_PROMPT = """
You are a humorous chat bot that:
- sarcastically responds to questions
- asks contradictory questions in return
- avoids giving direct answers
- responds with jokes

Chat members: крамар, баря, грандіозіус, староста, ромашка, ярко, агент ГУР, ДО, вже не дід, дядя батя, лупчик, дз, жекуня
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
        max_tokens=400,
    )
    return response.choices[0].message["content"]


async def ask(update, context):
    if update.effective_chat.id not in ALLOWED_CHATS:
        await reply(update.effective_message.reply_text("Сорян, фіча не доступна у цьому чаті"))
        return

    if not os.environ.get("OPENAI_API_KEY"):
        await reply(update.effective_message.reply_text("А ключика то немає, тому сам розбирайся"))
        return

    message = " ".join(context.args)
    response = get_response(message)
    await reply(update.effective_message.reply_text(response))


handlers = [CommandHandler("ask", ask)]
