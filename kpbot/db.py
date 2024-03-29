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

        if self._connected:
            await self._db[collection].insert_one(document)

    async def archive(self, message):
        chat_id = message.chat_id
        msg = cleanup_message(message.to_dict())

        await self.insert(f"chat:{chat_id}", msg)

    async def message_handler(self, update, _):
        message = update.effective_message
        await self.archive(message)

    def get_handlers(self):
        return [MessageHandler(filters.ALL, self.message_handler)]


client = DatabaseClient()


def select_keys(dictionary, keys):
    """
    If `keys` is a sequence, return new dict with specified keys only.
    If `keys` is a dict, recursively apply selection for each key in `keys`, no
    top-level keys in `dictionary` are removed.
    """
    if isinstance(keys, dict):
        return {k: (select_keys(dictionary[k], keys[k]) if k in keys else dictionary[k])
                    for k in dictionary}
    else:
        return {k: dictionary[k] for k in keys if k in dictionary}


def cleanup_message(msg: dict):
    fields_to_remove = (
        "channel_chat_created",
        "chat",
        "delete_chat_photo",
        "entities",
        "group_chat_created",
        "supergroup_chat_created",
    )

    # select fields to save to db
    msg = select_keys(msg, set(msg.keys()) - set(fields_to_remove))

    # process only last photo
    if "photo" in msg:
        msg["photo"] = msg["photo"][-1]

    # select nested fields
    msg = select_keys(msg, {
        "animation": ("file_id", "file_unique_id", "set_name"),
        "document": ("file_id", "file_unique_id", "set_name"),
        "photo": ("file_id", "file_unique_id"),
        "sticker": ("emoji", "file_id", "file_unique_id", "set_name"),
        "video_note": ("duration", "file_id", "file_unique_id"),
        "video": ("duration", "file_id", "file_unique_id"),
        "voice": ("duration", "file_id", "file_unique_id"),
    })

    # cleanup reply if exists
    if "reply_to_message" in msg:
        msg["reply_to_message"] = cleanup_message(msg["reply_to_message"])

    return msg
