from topic_tracking.model import Resource, Story, StoryUpdate
from topic_tracking.model_management.story_closing_handler import \
    StoryClosingHandler
from topic_tracking.util.from_config import mongo_from_config, \
    story_updating_client_from_config
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

    # story updating
    su_client = story_updating_client_from_config(config['story_updating']['client'])

    # exponential decay
    half_life = config['model_management']['story_closing']['resource_half_life']
    decay_constant = compute_exponential_decay_constant(half_life)

    # story closing settings
    search_timeout = config['model_management']['story_closing']['search_timeout']
    min_closing_score = config['model_management']['story_closing']['min_closing_score']
    min_story_life = config['model_management']['story_closing']['min_story_life']

    story_closing_handler = StoryClosingHandler(
        resource_collection, story_collection, update_collection,
        su_client, decay_constant, search_timeout, min_closing_score, min_story_life)

    su_client.connect()
    story_closing_handler.start()
    su_client.disconnect()
