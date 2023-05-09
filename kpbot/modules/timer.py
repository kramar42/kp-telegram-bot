import random
import time

from telegram.constants import ParseMode
from telegram.ext import CommandHandler

from ..alias import get_alias, get_chat_aliases
from .. import reply

WAIT_AMOUNT = 60 * 60 * 2


def create_mention(user_id, alias):
    return f"[{alias}](tg://user?id={user_id})"


def pidors_list_text(chat_id, not_pidors):
    aliases = get_chat_aliases(chat_id)
    names = [create_mention(uid, alias) for uid,alias in aliases.items() if uid not in not_pidors]
    random.shuffle(names)
    return ', '.join(names)


async def pidors_reminder_callback(context):
    msg = context.bot.send_message(chat_id=context.job.chat_id, text='Залишилась хвилинка, дітлахи')
    await reply(msg)


async def pidors_callback(context):
    chat_data = context.chat_data
    text = 'А ось і список підорків: ' + pidors_list_text(context.job.chat_id, chat_data['not_pidors'])
    del chat_data['pidor_active']
    if len(chat_data['not_pidors']) == 1:
        not_pidor = chat_data['not_pidors'].pop()
        alias = get_alias(context.job.chat_id, not_pidor)
        response = context.bot.send_message(context.job.chat_id,
                                         f'Sector clear. {create_mention(not_pidor, alias)} єдиний не підор.',
                                         ParseMode.MARKDOWN_V2)
        await reply(response)
        response = context.bot.send_sticker(context.job.chat_id, 'CAADBQADpgMAAukKyAN5s5AIa4Wx9AI')
        await reply(response)
    else:
        response = context.bot.send_message(chat_id=context.job.chat_id, text=text, parse_mode=ParseMode.MARKDOWN_V2)
        await reply(response)


async def timer(update, context):
    args = context.args
    if len(args) == 0:
        args = ['']
    try:
        amount = float(args[0])
    except (IndexError, ValueError):
        reply = update.effective_message.reply_text('/timer <float: minutes>')
        await reply(reply)
        return

    chat_data = context.chat_data
    if 'bomb_pidors' in chat_data and update.effective_message.from_user.id in chat_data['bomb_pidors']:
        reply = update.effective_message.reply_text('Підори не можуть ставити таймери')
        await reply(reply)
        return

    if amount < 15. or amount > 60.:
        reply = update.effective_message.reply_text('Тількі підори ставлять такі таймери')
        await reply(reply)
        return
    if 'pidor_active' in chat_data:
        pidor_user = chat_data['pidor_user']
        alias = get_alias(update.effective_message.chat_id, pidor_user)
        reply = update.effective_message.reply_text(f'{alias} вже запустив таймер')
        await reply(reply)
        return
    if 'pidor_time' in chat_data and time.time() - chat_data['pidor_time'] < WAIT_AMOUNT:
        reply = update.effective_message.reply_text('Заїбали зі своїми таймерами')
        await reply(reply)
        return

    chat_id = update.effective_message.chat_id
    chat_data['pidor_active'] = True
    chat_data['pidor_user'] = update.effective_message.from_user.id
    chat_data['pidor_time'] = time.time()
    chat_data['not_pidors'] = set()
    chat_data['not_pidors'].add(update.effective_message.from_user.id)

    context.job_queue.run_once(pidors_reminder_callback, 60 * (amount - 1), chat_id=chat_id)
    context.job_queue.run_once(pidors_callback, 60 * amount, chat_id=chat_id)
    reply = update.effective_message.reply_text('Bomb has been planted')
    await reply(reply)


handlers = [CommandHandler('timer', timer)]
