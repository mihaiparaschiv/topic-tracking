from topic_tracking.model import Story, Resource
from topic_tracking.model_management.helper.index import IndexHelper
from topic_tracking.util.from_config import elasticsearch_from_config, \
    mongo_from_config
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

    # elasticsearch
    es = elasticsearch_from_config(config['elasticsearch'])
    main_index = config['elasticsearch']['indexes']['main']
    # open_index = config['elasticsearch']['indexes']['open']

    # helpers
    index_helper = IndexHelper(es)

    for resource in resource_collection.find_models():
        index_helper.index_resource(resource, main_index)
        logger.debug('Indexed resource %s.' % resource)

    for story in story_collection.find_models():
        index_helper.index_story(story, main_index)
        logger.debug('Indexed story %s.' % story)

    logger.info('Re-indexing complete.')
