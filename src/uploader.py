import pymongo


class Uploader:
    _mongo: pymongo.MongoClient = None
    _database: str = None
    _collection: str = None

    def __init__(self, mongodb, database, collection):
        self._mongo = mongodb
        self._database = database
        self._collection = collection

    def _get_collection(self):
        return self._mongo[self._database][self._collection]

    def drop_collection(self):
        self._get_collection().drop()

    def insert_batch(self, batch):
        res = self._get_collection().insert_many(batch)
        # todo check results

    def insert(self, data):
        res = self._get_collection().insert(data)
