import logging

from motor.motor_asyncio import AsyncIOMotorClient
from telegram.ext import MessageHandler, filters

log = logging.getLogger(__name__)


class DatabaseClient:
    def __init__(self):
        self._connected = None

    def connect(self, uri, db_name):
        self._client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=500)
        self._db = self._client[db_name]
        log.info(f"connecting to {uri}")

    async def insert(self, collection, document):
        if self._connected is None:
            try:
                await self._client.server_info()
                self._connected = True
                log.info(f"connected to database")
            except Exception as e:
                self._connected = False
                log.error(f"can't connect to database: {e}")

        if not self._connected:
            return
        await self._db[collection].insert_one(document)


def delete_dict_keys(dictionary, keys):
    dictionary = dictionary.copy()
    for key in keys:
        dictionary.pop(key, None)
    return dictionary


def extract_dict_keys(dictionary, keys):
    return {k: dictionary[k] for k in keys if k in dictionary}


def process_field(msg, field, keys):
    msg = msg.copy()
    if field not in msg:
        return msg

    msg[field] = extract_dict_keys(msg[field], keys)
    return msg


def process_message(message):
    msg = message.to_dict()

    fields_to_remove = (
        "channel_chat_created",
        "chat",
        "delete_chat_photo",
        "entities",
        "group_chat_created",
        "supergroup_chat_created",
    )

    msg = delete_dict_keys(msg, fields_to_remove)
    msg = process_field(msg, "animation", ("file_id", "file_unique_id", "set_name"))
    msg = process_field(msg, "document", ("file_id", "file_unique_id", "set_name"))
    msg = process_field(msg, "sticker", ("emoji", "file_id", "file_unique_id", "set_name"))
    msg = process_field(msg, "video", ("duration", "file_id", "file_unique_id"))
    msg = process_field(msg, "video_note", ("duration", "file_id", "file_unique_id"))
    msg = process_field(msg, "voice", ("duration", "file_id", "file_unique_id"))

    if "photo" in msg:
        msg["photo"] = msg["photo"][-1]
        msg = process_field(msg, "photo", ("file_id", "file_unique_id"))

    if "reply_to_message" in msg:
        msg["reply_to_message"] = process_message(message.reply_to_message)

    return msg


def init(db_uri):
    if not db_uri:
        log.info("no DB connection")
        return False

    global client
    client.connect(db_uri, "chat_history")
    return True


async def archive(message):
    chat_id = message.chat_id
    msg = process_message(message)

    global client
    await client.insert(f"chat:{chat_id}", msg)


async def send_and_archive(reply):
    message = await reply
    await archive(message)


async def message_handler(update, context):
    message = update.effective_message
    await archive(message)


client = DatabaseClient()
handlers = [MessageHandler(filters.ALL, message_handler)]
