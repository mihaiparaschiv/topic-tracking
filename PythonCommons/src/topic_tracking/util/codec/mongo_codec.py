from topic_tracking.util.codec.base_codec import BaseCodec


class MongoCodec(BaseCodec):
    """Handles encoding and decoding of models to and from dictionaries."""

    def encode(self, model):
        doc = self._get_data(model)
        if '_id' in doc and doc['_id'] is None:
            del doc['_id']
        return doc

    def decode(self, doc, factory):
        return factory(**doc)
