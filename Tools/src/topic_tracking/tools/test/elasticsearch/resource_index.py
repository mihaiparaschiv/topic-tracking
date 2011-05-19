from pprint import pprint
from pyes.es import ES
from topic_tracking.model import Resource
from topic_tracking.model.id import makeIdFromURI
from topic_tracking.util.codec.json_codec import JSONCodec
from topic_tracking.util.codec.mongo_codec import MongoCodec
from topic_tracking.util.mongo import MongoConnectionManager
from topic_tracking.util.from_config import message_queue_client_from_config


def build_payload_string(features, boost):
    payload_sum = reduce(lambda x, y: x + (y * boost) ** 2.0, features.values(), 0)
    payload_sum = payload_sum ** 0.5

    payloads = []
    for k, v in features.iteritems():
        payloads.append((k, v / payload_sum * boost))

    payloads = (f[0] + '|' + str(f[1]) for f in payloads)
    return ' '.join(payloads)


if __name__ == '__main__':

    # MongoDB
    host = 'localhost'
    port = 27017
    mcm = MongoConnectionManager(host, port, MongoCodec())
    database = 'processed'
    resource_collection = mcm.get_collection(database, 'resources', Resource)

    # message queue
    mq_config = {
        'transport': 'socket',
        'protocol': 'binary',
        'host': 'localhost',
        'port': 9091
        }
    mq_client = message_queue_client_from_config(mq_config)
    mq_codec = JSONCodec()
    processed_resource_queue = 'processed_resources'

    # ElasticSearch
    es = ES('localhost:9200', timeout=60)
    es_index = 'topic_tracking'

    # dequeue one resource
    mq_client.connect()
    message = mq_client.getMessage(processed_resource_queue)
    resource = mq_codec.decode(message.body, Resource)
    mq_client.deleteMessage(processed_resource_queue, message.id)
    mq_client.disconnect()

    # save the resource to mongo
    resource._id = makeIdFromURI(resource.uri)
    resource_collection.insert_model(resource)

    # index the resource
    for boost in [1, 1000]:
        es_doc = {}
        es_doc['content'] = resource.content
        es_doc['title'] = resource.title
        es_doc['entities'] = build_payload_string(resource.entities, boost)
        es_doc['terms'] = build_payload_string(resource.terms, boost)
        id = '%s_%d' % (resource._id, boost)
        r = es.index(es_doc, es_index, 'resource', id)
        pprint(r)
