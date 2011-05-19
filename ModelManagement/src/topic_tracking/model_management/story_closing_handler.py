from topic_tracking.constants import STORY_UPDATE_STORY_CLOSED, \
    STORY_STATUS_OPEN
from topic_tracking.model import StoryUpdate
from topic_tracking.service.story_updating import StoryUpdatingService
import logging
import time


class StoryClosingHandler(StoryUpdatingService.Iface):

    _logger = logging.getLogger('model_management.StoryClosingHandler')

    def __init__(self, resource_collection, story_collection, update_collection,
            su_client, decay_constant, search_timeout, min_closing_score, min_story_life):

        # mongo
        self._resource_collection = resource_collection
        self._story_collection = story_collection
        self._update_collection = update_collection

        # story updating
        self._su_client = su_client

        # settings
        self._decay_constant = decay_constant
        self._search_timeout = search_timeout
        self._min_closing_score = min_closing_score
        self._min_story_life = min_story_life

        # current time = last resource publishing time
        self._current_time = None

    def start(self):

        self._resource_collection.ensure_index('published')

        while True:

            # find current time
            sort = [('published', -1)]
            last_resource = self._resource_collection.find_one_model(sort=sort)
            if last_resource is None:
                logging.debug('No resources found.')
                time.sleep(self._search_timeout)
                continue
            self._current_time = last_resource.published

            # check all open stories if they need to be closed
            query = {'status': STORY_STATUS_OPEN}
            count = 0
            for story in self._story_collection.find_models(query):
                if self._check_closing_condition(story):
                    # create an update
                    update = StoryUpdate()
                    update.story_id = story._id
                    update.type = STORY_UPDATE_STORY_CLOSED
                    update.value = self._current_time
                    # queue the update
                    self._update_collection.insert_model(update)
                    # apply the update
                    self._su_client.update(story._id)
                    logging.info('Closing story %s after %d seconds.' %
                        (story, self._current_time - story.created))
                count += 1
            logging.debug('Checked %d stories.' % count)

            time.sleep(self._search_timeout)

    def _check_closing_condition(self, story):
        story_score = story.closing_score
        story_time = story.updated

        # test if the closing score has never been computed
        if story_time is None:
            return False

        # test if the story is old enough for closing
        if self._current_time - story.created < self._min_story_life:
            return False

        # compute current score
        story_score *= self._decay_constant ** (self._current_time - story_time)
        if story_score < self._min_closing_score:
            return True

        return False
