from topic_tracking.model import Story
import logging
from topic_tracking.constants import STORY_STATUS_OPEN


class StoryProvider(object):

    _logger = logging.getLogger('model_management.StoryProvider')

    def __init__(self, story_collection, story_finder, min_similarity):
        self._story_collection = story_collection
        self._story_finder = story_finder
        self._min_similarity = min_similarity

    def provide_for_resource(self, resource):

        # selected story
        story = None

        # make sure we have an updated index
        self._story_finder.refresh()

        # find the most similar story
        fss = self._story_finder.find_stories_by_resource(resource, 1)
        if len(fss) > 0 and fss[0]['_score'] >= self._min_similarity:
            story = self._story_collection.find_one_model(fss[0]['_id'])
            self._logger.debug('Found story %s for resource %s with score %f.' %
                (story, resource, fss[0]['_score']))

        # create an empty story if none was found
        if story is None:
            id = 's_%s' % resource._id
            title = resource.title
            story = Story(_id=id, title=title, resource_count=0, status=STORY_STATUS_OPEN,
                terms={}, entities={}, score=0.0, closing_score=0.0)
            self._story_collection.insert_model(story)
            self._logger.debug('New story for resource %s.' % resource)

        return story
