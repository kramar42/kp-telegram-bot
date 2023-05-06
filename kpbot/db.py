import logging

from motor.motor_asyncio import AsyncIOMotorClient

log = logging.getLogger(__name__)


class DatabaseClient:
    def __init__(self):
        self._connected = False

    @property
    def connected(self):
        return self._connected

    def connect(self, uri):
        self._client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=200)
        self._connected = True
        log.info(f"connected to {uri}")


def connect(db_uri):
    if not db_uri:
        log.info("skipped DB connection")
        return

    global client
    client.connect(db_uri)


client = DatabaseClient()
