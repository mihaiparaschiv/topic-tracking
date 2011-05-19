from bson.objectid import ObjectId
import copy
from topic_tracking.model import Topic
import logging
import time
from topic_tracking.service.exceptions.ttypes import NotFoundException
from topic_tracking.service.topic_management import TopicManagementService


class TopicManagementHandler(TopicManagementService.Iface):

    _logger = logging.getLogger('topic_management.TopicManagementHandler')

    def __init__(self, story_collection, topic_collection, es, index, query_builder):

        # MongoDB
        self._story_collection = story_collection
        self._topic_collection = topic_collection

        # ElasticSearch
        self._es = es
        self._index = index
        self._query_builder = query_builder

    def create_from_features(self, features):
        pass

    def create_from_story(self, id):
        raise NotFoundException('Story not found.')

    def get_summary(self, id, startTime, endTime):
        pass

    def _create_from_features(self, title, terms, entities):
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

    def create_from_stories(self, title, stories):

        # only the first story is considered
        terms = copy.copy(stories[0].terms)
        entities = copy.copy(stories[0].entities)

        return self.create_from_features(title, terms, entities)

    def archive(self, topic):
        pass

    def delete(self, topic):
        self._topic_collection.delete_model(topic)

    def get_summary(self, topic):
        count = 100
        hits = self._find_stories_by_topic(topic, count)
        stories = []
        for hit in hits:
            stories.append(self._story_collection.find_one_model(hit['_id']))
        return stories

    def _find_stories_by_topic(self, topic, count):
        model_query = self._query_builder.build_model_query(topic)
        query = {
            'query': model_query,
            'size': count
        }
        result = self._es.search(query, self._index, 'story')
        return result['hits']['hits']
