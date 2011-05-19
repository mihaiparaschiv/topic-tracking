from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.transport import TSocket
from thrift.transport.TTransport import TFramedTransportFactory
from topic_tracking.model import Story, Topic
from topic_tracking.model_management.helper.index import IndexHelper
from topic_tracking.service.story_updating import StoryUpdatingService
from topic_tracking.topic_management.topic_management_handler import \
    TopicManagementHandler
from topic_tracking.util.from_config import elasticsearch_from_config, \
    mongo_from_config
from topic_tracking.util.similarity.model_query import ModelQueryBuilder
import logging.config
import sys
import yaml


if __name__ == '__main__':

    config_file = sys.argv[1]
    config = yaml.load(file(config_file, 'r'))

    # logging
    logging.config.dictConfig(config['logging'])
    logger = logging.getLogger()

    # MongoDB
    mcm = mongo_from_config(config['mongo'])
    database = config['mongo']['databases']['processed']
    story_collection = mcm.get_collection(database, 'stories', Story)
    topic_collection = mcm.get_collection(database, 'topics', Topic)

    # elasticsearch
    es = elasticsearch_from_config(config['elasticsearch'])
    main_index = config['elasticsearch']['indexes']['main']

    # helpers
    index_helper = IndexHelper(es)

    MAX_CLAUSES = 20
    MAX_ENTITY_CLAUSES = 10
    ENTITY_BOOST = 10
    TERM_BOOST = 1
    query_builder = ModelQueryBuilder(MAX_CLAUSES, MAX_ENTITY_CLAUSES, ENTITY_BOOST, TERM_BOOST)

    # set up the server
    handler = TopicManagementHandler(story_collection, topic_collection,
        es, main_index, query_builder)
    processor = StoryUpdatingService.Processor(handler)
    port = config['topic_management']['server']['port']
    serverTransport = TSocket.TServerSocket(port)
    serverTransport.host = 'localhost'
    transportFactory = TFramedTransportFactory()
    protocolFactory = TBinaryProtocol.TBinaryProtocolFactory()
    server = TServer.TThreadedServer(processor, serverTransport,
        transportFactory, protocolFactory)

    # start the server
    logging.info('Starting the topic management service on port %d.' % port)
    server.serve()
