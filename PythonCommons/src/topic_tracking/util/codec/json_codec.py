from topic_tracking.util.codec.base_codec import BaseCodec
import json


class JSONCodec(BaseCodec):
    """Handles encoding and decoding of models to and from JSON strings."""

    def encode(self, model):
        return json.dumps(self._get_data(model))

    def decode(self, string, factory):
        doc = json.loads(string)
        return factory(**doc)
