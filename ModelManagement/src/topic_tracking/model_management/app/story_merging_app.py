from topic_tracking.model import Resource, Story
from topic_tracking.model_management.helper.index import IndexHelper
from topic_tracking.model_management.story.finder import StoryFinder
from topic_tracking.model_management.story_merger import StoryMerger
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
    resource_index = config['elasticsearch']['indexes']['resources']
    story_index = config['elasticsearch']['indexes']['stories']

    # settings
    sm_config = config['model_management']['story_merging']
    min_similarity = sm_config['min_similarity']
    search_delay = sm_config['search_delay']
    resource_count_ratio = sm_config['resource_count_ratio']

    # helpers
    index_helper = IndexHelper(es, resource_index, story_index)
    max_clauses = config['model_management']['similarity']['max_clauses']
    max_entity_clauses = config['model_management']['similarity']['max_entity_clauses']
    story_finder = StoryFinder(es, story_index, max_clauses, max_entity_clauses)

    inserted_resource_handler = StoryMerger(resource_collection, story_collection,
        index_helper, story_finder, min_similarity, search_delay, resource_count_ratio)

    inserted_resource_handler.start()
