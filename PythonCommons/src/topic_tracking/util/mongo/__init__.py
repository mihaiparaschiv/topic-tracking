from pymongo.connection import Connection
from pymongo.cursor import Cursor
from topic_tracking.util.dict import ObjectDictWrapper


class _ModelCursor(Cursor):
    """Provides automatic decoding of models."""

    def __init__(self, mc, *args, **kwargs):
        super(_ModelCursor, self).__init__(mc._collection, *args, **kwargs)
        self._mc = mc

    def next(self):
        document = super(_ModelCursor, self).next()
        model = self._mc._decode(document)
        return model

    def __getitem__(self, index):
        document = super(_ModelCursor, self).__getitem__(index)
        model = self._mc._decode(document)
        return model


class ModelCollection(object):
    """Wraps a PyMongo collection and adds model encoding and decoding
    functionality."""

    def __init__(self, collection, codec, klass):
        self._collection = collection
        self._codec = codec
        self._klass = klass

    def _encode(self, model):
        return self._codec.encode(model)

    def _decode(self, document):
        return self._codec.decode(document, self._klass)

    def insert_model(self, model):
        assert isinstance(model, self._klass)
        document = self._encode(model)
        id = self.insert(document)
        model._id = id

    def update_model(self, model):
        assert isinstance(model, self._klass)
        document = self._encode(model)
        self.update({'_id': document['_id']}, document)

    def save_model(self, model):
        assert isinstance(model, self._klass)
        if model._id is None:
            self.insert_model(model)
        else:
            document = self._encode(model)
            self.save(document)

    def remove_model(self, model):
        assert isinstance(model, self._klass)
        self.remove(model._id)

    def find_models(self, *args, **kwargs):
        return _ModelCursor(self, *args, **kwargs)

    def find_one_model(self, spec_or_id=None, *args, **kwargs):
        document = self.find_one(spec_or_id, *args, **kwargs)
        if document is None:
            return None
        return self._decode(document)

    def __getattr__(self, name):
        attr = self._collection.__getattribute__(name)

        if not callable(attr):
            return attr

        def f(*args, **kwargs):
            if 'safe' in attr.func_code.co_varnames:
                kwargs['safe'] = True
            return attr(*args, **kwargs)
        return f


class MongoConnectionManager(object):
    """Provides access to MongoDB connection properties and collections."""

    def __init__(self, host, port, codec):
        """
        @param host: MongoDB host
        @param port: MongoDB port
        @param codec: model codec
        """

        # basic properties
        self.connection = Connection(host, port)
        self.codec = codec

        # collection wrappers
        self.collections = ObjectDictWrapper()

    def get_collection(self, database, collection, klass):
        c = self.connection[database][collection]
        return ModelCollection(c, self.codec, klass)
