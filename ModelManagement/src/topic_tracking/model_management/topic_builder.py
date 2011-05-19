from operator import itemgetter
from topic_tracking.model import Topic, TopicSnapshot
import logging
import sys


class TopicBuilder(object):

    MAX_SELECTED_STORIES = 10
    MAX_SNAPSHOT_ENTITIES = sys.maxint
    MAX_SNAPSHOT_TERMS = sys.maxint


    _logger = logging.getLogger('model_management.TopicBuilder')

    def __init__(self, story_collection, topic_collection, snapshot_collection,
            query_builder, es, index_helper, index, min_similarity, decay_constant):

        # MongoDB
        self._story_collection = story_collection
        self._topic_collection = topic_collection
        self._snapshot_collection = snapshot_collection

        # ElasticSearch
        self._query_builder = query_builder
        self._es = es
        self._index_helper = index_helper
        self._index = index

        # settings
        self._min_similarity = min_similarity
        self._decay_constant = decay_constant

    def build_from_story(self, story):
        # copy the story's model into a new topic
        kwargs = {}
        kwargs['_id'] = 't_' + story._id
        kwargs['title'] = story.title
        kwargs['created'] = story.created
        kwargs['updated'] = story.created
        topic = Topic(**kwargs)
        self._add_story(topic, story)
        self._topic_collection.insert_model(topic)

        self._logger.info('Created topic %s from story %s.' % (topic, story))

        # save the first snapshot
        self._save_snapshot(topic, story.created)

        # build the topic
        self.update_topic(topic)

    def update_topic(self, topic):
        """Search for matching stories in the order in which they have been
        created. Update the topic for each match.
        """

        self._logger.info('Topic %s: update started.' % topic)

        current_time = topic.updated

        # last batch of story ids - used because there may be multiple stories
        # with the same timestamp
        last_story_ids = []

        while True:

            # search for matching stories
            fss = self._find_stories_by_topic(topic, self.MAX_SELECTED_STORIES,
                current_time, last_story_ids + topic.story_ids)

            # we have no more stories in the index
            if len(fss) == 0:
                break

            story = None

            # pick the first story that passes the score threshold
            for fs in fss:
                score = fs['_score']
                id = fs['_id']

                if current_time < fs['_source']['created']:
                    current_time = fs['_source']['created']
                    # the story list is reset here because the number of stories
                    # with the same timestamp may be greater than the batch size
                    last_story_ids = []
                last_story_ids.append(id)

                if score >= self._min_similarity:
                    story = self._story_collection.find_one_model(id)
                    break

            # update the topic scores after each round
            self._update_topic(topic, current_time)

            if story is not None:
                self._add_story(topic, story)
                self._logger.info('Added story %s with score %f.' % (story, score))
                self._save_snapshot(topic, story.created)
            else:
                self._logger.debug('No story match.')

            if len(last_story_ids) > 1:
                self._logger.debug('Last story ids: %s' % last_story_ids)

        self._topic_collection.update_model(topic)

        self._logger.info('Topic %s: update complete.' % topic)

    def _add_story(self, topic, story):

        # compute the score decay factor
        topic_time = topic.updated
        story_time = story.created
        current_time = max(topic_time, story_time)
        story_factor = self._decay_constant ** (current_time - story_time)

        # update the topic's features
        self._add_story_features(topic.entities, story.entities, story_factor)
        # --- quick hack for removing common terms
        clean_story_terms = TopicBuilder.HACK_remove_ignorable_terms(story.terms)
        logging.debug('Removed %d out of %d terms.' %
            (len(story.terms) - len(clean_story_terms), len(story.terms)))
        # ---
        self._add_story_features(topic.terms, clean_story_terms, story_factor)

        # add the story reference
        topic.story_ids.append(story._id)

    def _add_story_features(self, topic_features, story_features, story_factor):
        """Adds the story's features to the topic. Requires that the topic model
        is up to date."""

        for k, v_story in story_features.iteritems():
            v_topic = topic_features.get(k, 0)
            v_story *= story_factor
            topic_features[k] = v_topic + v_story

    def _update_topic(self, topic, current_time):
        """Updates the topic's features for the given time."""

        # compute exponential decay factor
        factor = self._decay_constant ** (current_time - topic.updated)

        for features in (topic.entities, topic.terms):
            for k, _ in features.iteritems():
                # TODO: see if we need to remove values that are
                # below a threshold
                features[k] *= factor

        topic.updated = current_time

    def _save_snapshot(self, topic, created):
        # select features
        key = itemgetter(1)
        entities = dict(sorted(topic.entities.items(), key=key,
            reverse=True)[:self.MAX_SNAPSHOT_ENTITIES])
        terms = dict(sorted(topic.terms.items(), key=key,
            reverse=True)[:self.MAX_SNAPSHOT_TERMS])

        # create and insert snapshot
        snapshot = TopicSnapshot(topic_id=topic._id, story_ids=topic.story_ids,
            terms=terms, entities=entities, created=created)
        self._snapshot_collection.insert_model(snapshot)

    def _find_stories_by_topic(self, topic, count, min_time, excludable_story_ids):
        """Finds the best matching stories for the given topic, which have been
        created earlier than the specified time.
        """

        model_query = self._query_builder.build_model_query(topic)

        filters = []
        filters.append({'numeric_range': {'created': {'gte': min_time}}})

        # build story exclusion filters
        for story_id in excludable_story_ids:
            filters.append({'not': {'filter': {'term': {'_id': story_id}}}})

        query = {
            'query': {
                'filtered': {
                    'query': model_query,
                    'filter': {
                        'and': filters
                    }
                }
            },
            'sort': [
                {'created': 'asc'},
                {'_score': 'desc'}
            ],
            'size': count
        }

        result = self._es.search(query, self._index, 'story')
        return result['hits']['hits']


    IGNORED_TERMS = ['v_be', 'v_do', 'v_have', 'v_make', 'v_propose', 'v_say', 'v_take']

    @classmethod
    def HACK_remove_ignorable_terms(cls, story_terms):
        return dict([item for item in story_terms.iteritems()
            if item[0] not in cls.IGNORED_TERMS])
