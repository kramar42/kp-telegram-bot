from . import db


async def reply(response):
    message = await response
    await db.client.archive(message)
