import logging
import time


function = 'function() { \
rc = this.resource_count; \
lmrc = this.last_merge_resource_count; \
if (lmrc == 0) \
    return rc > 1; \
return (rc - lmrc) / lmrc >= %f; \
}'


class StoryMerger(object):

    _logger = logging.getLogger('model_management.StoryMerger')

    def __init__(self, resource_collection, story_collection, index_helper, story_finder,
            min_similarity, search_delay, resource_count_ratio):

        # mongo
        self._resource_collection = resource_collection
        self._story_collection = story_collection

        # utilities
        self._index_helper = index_helper
        self._story_finder = story_finder

        # properties
        self._min_similarity = min_similarity
        self._search_delay = search_delay
        self._resource_count_ratio = resource_count_ratio

    def start(self):
        query = {'$where': function % (self._resource_count_ratio)}
        while True:
            story_a = self._story_collection.find_one_model(query)

            if story_a is None:
                self._logger.debug('Sleeping for %f seconds.' % self._search_delay)
                time.sleep(self._search_delay)
                continue

            self._index_helper.refresh_story_index()
            fss = self._story_finder.find_stories_by_story(story_a, 1)

            if len(fss) == 0 or fss[0]['_score'] < self._min_similarity:
                self._logger.debug('Story %s: No match found.' % story_a)
                self._on_no_merge(story_a)
            else:
                storyB_id = fss[0]['_id']
                sim_score = fss[0]['_score']
                story_b = self._story_collection.find_one_model(storyB_id)
                self._logger.info('Story %s: found story %s, with score: %s.' %
                    (story_a, story_b, sim_score))
                self._on_merge(story_a, story_b)

    def _on_no_merge(self, story):
        story.last_merge_resource_count = story.resource_count
        self._story_collection.update_model(story)

    def _on_merge(self, story_a, story_b):
        # pick the story with most resources
        if story_a.resource_count < story_b.resource_count:
            story_a, story_b = story_b, story_a

        # update story a
        self._update_features(story_a.terms, story_b.terms)
        self._update_features(story_a.entities, story_b.entities)
        story_a.last_merge_resource_count = story_a.resource_count
        story_a.resource_count += story_b.resource_count

        # update resources from removed story
        spec = {'story_id': story_b._id}
        document = { '$set': { 'story_id': story_a._id }}
        self._resource_collection.update(spec, document, multi=True)
        self._logger.debug('Updated story_id for %d resources.' % story_b.resource_count)

        # delete story b
        self._story_collection.remove_model(story_b)
        self._index_helper.delete_story(story_b)

        # save story a
        self._story_collection.save_model(story_a)
        self._index_helper.index_story(story_a)

        self._logger.debug('Story %s updated with data from story %s.' %
            (story_a, story_b))

    def _update_features(self, story_features, resource_features):
        for k, v in resource_features.iteritems():
            v_story = story_features.get(k, 0)
            story_features[k] = v + v_story
