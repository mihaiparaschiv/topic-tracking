class MongoCache(object):

    def __init__(self, collection):
        self._collection = collection

    def put(self, id, data):
        doc = {'_id': id, 'data': data}
        self._collection.save(doc)

    def get(self, id):
        cursor = self._collection.find({'_id': id})
        try:
            doc = cursor.next()
            return doc['data']
        except StopIteration:
            return None