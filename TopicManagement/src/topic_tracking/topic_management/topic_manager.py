from bson.objectid import ObjectId
import copy
from topic_tracking.model import Topic
import logging
import time


class TopicManager(object):

    _logger = logging.getLogger('topic_management.TopicManager')

    def __init__(self, story_collection, topic_collection, es, index, query_builder, min_similarity):
        self._story_collection = story_collection
        self._topic_collection = topic_collection
        self._es = es
        self._index = index
        self._query_builder = query_builder
        self._min_similarity = min_similarity

    def create_from_features(self, title, terms, entities):
        """Inserts a topic in MongoDB and indexes it in ElasticSearch."""

        kwargs = {}
        # TODO: find a better way to assign ids
        kwargs['_id'] = 't_' + str(ObjectId())
        kwargs['title'] = title
        kwargs['created'] = int(time.time())
        kwargs['terms'] = terms
        kwargs['entities'] = entities
        topic = Topic(**kwargs)
        self._topic_collection.insert_model(topic)

        self._logger.info('Created topic %s.' % topic)

        # add to ES

        return topic

    def create_from_story(self, title, story):

        # only the first story is considered
        terms = copy.copy(story.terms)
        entities = copy.copy(story.entities)

        return self.create_from_features(title, terms, entities)

    def archive(self, topic):
        pass

    def delete(self, topic):
        self._topic_collection.delete_model(topic)

    def get_summary(self, topic, startTime, endTime, count):
        hits = self._find_stories_by_topic(topic, startTime, endTime, count)
        stories = []
        for hit in hits:
            stories.append(self._story_collection.find_one_model(hit['_id']))
        return stories

    def _find_stories_by_topic(self, topic, startTime, endTime, count):
        model_query = self._query_builder.build_model_query(topic)

        filters = []
        filters.append({'numeric_range': {'created': {'gte': startTime, 'lt': endTime}}})

        query = {
            'query': {
                'filtered': {
                    'query': model_query,
                    'filter': {
                        'and': filters
                    }
                }
            },
            'size': count
        }

        result = self._es.search(query, self._index, 'story')
        hits = result['hits']['hits']
        return [hit for hit in hits if hit['_score'] > self._min_similarity]
