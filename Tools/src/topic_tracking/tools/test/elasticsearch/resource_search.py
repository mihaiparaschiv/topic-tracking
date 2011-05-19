"""This script assumes we have at least one indexed resource."""


from pprint import pprint
from pyes.es import ES
from topic_tracking.model import Resource
from topic_tracking.util.codec.mongo_codec import MongoCodec
from topic_tracking.util.mongo import MongoConnectionManager


def build_query(resource, explain):

        # build entity queries
        entity_queries = []
        for entity, score in resource.entities.iteritems():
            q = {
                'payload': {
                    'entities': {
                        'value': entity,
                        'boost': score
                        }
                    }
                }
            entity_queries.append(q)

        # build term queries
        term_queries = []
        for term, score in resource.terms.iteritems():
            q = {
                'payload': {
                    'terms':{
                        'value': term,
                        'boost': score
                        }
                    }
                }
            term_queries.append(q)

        # complete query
        query = {
                'query': {
                    'bool': {
                            'should': entity_queries + term_queries
                        }
                },
                'size': 2,
                'explain': explain
            }

        return query


if __name__ == '__main__':

    explain = True

    # MongoDB
    host = 'localhost'
    port = 27017
    mcm = MongoConnectionManager(host, port, MongoCodec())
    database = 'processed'
    resource_collection = mcm.get_collection(database, 'resources', Resource)

    # ElasticSearch
    es = ES('localhost:9200', timeout=60)
    es_index = 'topic_tracking'

    # find the same resource
    resource = resource_collection.find_one_model()
    query = build_query(resource, explain)
    result = es.search(query, es_index, 'resource')

    for r in result['hits']['hits']:
        pprint(r)
    print('Tested resource %s: %s' % (resource._id, resource.uri))
