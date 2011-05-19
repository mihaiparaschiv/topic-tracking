from topic_tracking.model import Story, Topic, TopicSnapshot
from topic_tracking.model_management.helper.index import IndexHelper
from topic_tracking.model_management.topic_builder import TopicBuilder
from topic_tracking.util.from_config import elasticsearch_from_config, \
    mongo_from_config
from topic_tracking.util.score import compute_exponential_decay_constant
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
    snapshot_collection = mcm.get_collection(database, 'topic_snapshots', TopicSnapshot)

    # elasticsearch
    es = elasticsearch_from_config(config['elasticsearch'])
    main_index = config['elasticsearch']['indexes']['main']

    # helpers
    index_helper = IndexHelper(es)

    # query builder
    max_clauses = config['model_management']['similarity']['max_clauses']
    max_entity_clauses = config['model_management']['similarity']['max_entity_clauses']
    entity_boost = config['model_management']['similarity']['entity_boost']
    term_boost = config['model_management']['similarity']['term_boost']
    query_builder = ModelQueryBuilder(max_clauses, max_entity_clauses, entity_boost, term_boost)

    # settings
    min_similarity = config['model_management']['topic_building']['min_similarity']

    # exponential decay
    half_life = config['model_management']['topic_building']['story_half_life']
    decay_constant = compute_exponential_decay_constant(half_life)

    topic_builder = TopicBuilder(story_collection, topic_collection, snapshot_collection,
        query_builder, es, index_helper, main_index,
        min_similarity, decay_constant)

    topic_collection.drop()
    snapshot_collection.drop()

    story_ids = ['msnbc-5305c6f46a09cb04bdbbe6ebeeb503c0',
                 'offalyexpress-ac9ae9871e1fbeb0617066a3a2313677',
                 'smh-bad45a9957cfc693dcb726feacd925a6',
                 'latimes-a93cdbe497cb1a340fe846406ffcd8a0',
                 'CBSnews-41356c9a7cc3b5c0891b56b6f78e67b0']
    for story_id in story_ids:
        story = story_collection.find_one_model(story_id)
        topic_builder.build_from_story(story)
