from topic_tracking.model import Resource, Story, StoryUpdate
from topic_tracking.model_management.helper.index import IndexHelper
from topic_tracking.model_management.processed_resource_handler import \
    ProcessedResourceHandler
from topic_tracking.model_management.story.finder import StoryFinder
from topic_tracking.model_management.story.provider import StoryProvider
from topic_tracking.util.codec.json_codec import JSONCodec
from topic_tracking.util.from_config import elasticsearch_from_config, \
    mongo_from_config, message_queue_client_from_config, \
    story_updating_client_from_config
import logging.config
import sys
import yaml
from topic_tracking.util.similarity.model_query import ModelQueryBuilder


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

    # message queue
    mq_client = message_queue_client_from_config(config['message_queue']['client'])
    mq_client.connect()
    mq_codec = JSONCodec()
    processed_resource_queue = 'processed_resources'

    # elasticsearch
    es = elasticsearch_from_config(config['elasticsearch'])
    main_index = config['elasticsearch']['indexes']['main']
    open_index = config['elasticsearch']['indexes']['open']

    # story updating
    su_client = story_updating_client_from_config(config['story_updating']['client'])

    # helpers
    index_helper = IndexHelper(es)

    # story finder
    max_clauses = config['model_management']['similarity']['max_clauses']
    max_entity_clauses = config['model_management']['similarity']['max_entity_clauses']
    entity_boost = config['model_management']['similarity']['entity_boost']
    term_boost = config['model_management']['similarity']['term_boost']
    query_builder = ModelQueryBuilder(max_clauses, max_entity_clauses, entity_boost, term_boost)
    story_finder = StoryFinder(es, open_index, query_builder)

    # story provider
    min_similarity = config['model_management']['story_selection']['min_similarity']
    story_provider = StoryProvider(story_collection, story_finder, min_similarity)

    processed_resource_handler = ProcessedResourceHandler(
        mq_client, mq_codec, processed_resource_queue,
        resource_collection, update_collection, su_client,
        index_helper, main_index, story_provider)

    mq_client.connect()
    su_client.connect()
    processed_resource_handler.start()
    mq_client.disconnect()
    su_client.disconnect()
