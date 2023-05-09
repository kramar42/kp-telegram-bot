from . import db


async def reply(reply):
    message = await reply
    await db.client.archive(message)
