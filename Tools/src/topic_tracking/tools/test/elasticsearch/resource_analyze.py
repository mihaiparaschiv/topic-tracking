from pprint import pprint
from pyes.es import ES
from topic_tracking.model import Resource
from topic_tracking.model_management.helper.index import IndexHelper
from topic_tracking.util.codec.mongo_codec import MongoCodec
from topic_tracking.util.mongo import MongoConnectionManager


if __name__ == '__main__':

    # MongoDB
    host = 'localhost'
    port = 27017
    mcm = MongoConnectionManager(host, port, MongoCodec())
    database = 'processed'
    resource_collection = mcm.get_collection(database, 'resources', Resource)

    # ElasticSearch
    es = ES('localhost:9200', timeout=60)
    resource_index = 'topic_tracking_resources'
    story_index = 'topic_tracking_stories'

    # utilities
    index_helper = IndexHelper(es, resource_index, story_index)

    # get a resource to mongo
    resource = resource_collection.find_one_model()

    # analyze the resource
    term_string = index_helper._build_payload_string(resource.terms)
    pprint(term_string)
    params = {}
    params['text'] = term_string
    response = es._send_request('GET', resource_index + '/_analyze', None, params)
    pprint(response)
