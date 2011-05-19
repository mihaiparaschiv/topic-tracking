from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.transport import TSocket
from thrift.transport.TTransport import TFramedTransportFactory
from topic_tracking.model import Resource, Story, StoryUpdate
from topic_tracking.model_management.helper.index import IndexHelper
from topic_tracking.model_management.story_updating_handler import \
    StoryUpdatingHandler
from topic_tracking.service.story_updating import StoryUpdatingService
from topic_tracking.util.from_config import elasticsearch_from_config, \
    mongo_from_config
from topic_tracking.util.score import compute_exponential_decay_constant
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
    resource_collection = mcm.get_collection(database, 'resources', Resource)
    story_collection = mcm.get_collection(database, 'stories', Story)
    update_collection = mcm.get_collection(database, 'updates', StoryUpdate)

    # elasticsearch
    es = elasticsearch_from_config(config['elasticsearch'])
    main_index = config['elasticsearch']['indexes']['main']
    open_index = config['elasticsearch']['indexes']['open']

    # helpers
    index_helper = IndexHelper(es)

    # exponential decay
    half_life = config['model_management']['story_closing']['resource_half_life']
    decay_constant = compute_exponential_decay_constant(half_life)

    # set up the server
    handler = StoryUpdatingHandler(
        resource_collection, story_collection, update_collection,
        index_helper, main_index, open_index, decay_constant)
    processor = StoryUpdatingService.Processor(handler)
    port = config['story_updating']['server']['port']
    serverTransport = TSocket.TServerSocket(port)
    serverTransport.host = 'localhost'
    transportFactory = TFramedTransportFactory()
    protocolFactory = TBinaryProtocol.TBinaryProtocolFactory()
    server = TServer.TThreadedServer(processor, serverTransport,
        transportFactory, protocolFactory)

    # start the server
    logging.info('Starting story updating service on port %d.' % port)
    server.serve()
