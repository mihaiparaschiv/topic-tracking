from threading import Lock
from topic_tracking.constants import STORY_STATUS_OPEN, \
    STORY_UPDATE_RESOURCE_INSERTED, STORY_UPDATE_STORY_CLOSED, STORY_STATUS_CLOSED
from topic_tracking.service.exceptions.ttypes import NotFoundException
from topic_tracking.service.story_updating import StoryUpdatingService
import logging


class StoryUpdatingHandler(StoryUpdatingService.Iface):

    _logger = logging.getLogger('model_management.StoryUpdatingHandler')

    def __init__(self, resource_collection, story_collection, update_collection,
            index_helper, main_index, open_index, decay_constant):

        # mongo
        self._resource_collection = resource_collection
        self._story_collection = story_collection
        self._update_collection = update_collection

        # index
        self._index_helper = index_helper
        self._main_index = main_index
        self._open_index = open_index

        # settings
        self._decay_constant = decay_constant

        # synchronization
        self._lock = Lock()

    def update(self, id):
        """Finds all available updates and applies them."""

        self._lock.acquire()

        story = self._story_collection.find_one_model(id)
        if story is None:
            raise NotFoundException()

        closing_requested = False

        # loop through all available updates
        updates = self._update_collection.find_models({'story_id':story._id})
        for update in updates:
            if update.type == STORY_UPDATE_RESOURCE_INSERTED:
                # process a resource insertion request
                # no changes are made to the resource model
                resource_id = update.value
                resource = self._resource_collection.find_one_model(resource_id)
                self._update_with_resource(story, resource)
                # put the resource in the open index
                self._index_helper.index_resource(resource, self._open_index)
            elif update.type == STORY_UPDATE_STORY_CLOSED:
                # store the closing time
                story.closing_closed = update.value
                closing_requested = True
            self._update_collection.remove_model(update)

        if closing_requested:
            story.status = STORY_STATUS_CLOSED
            # remove the story and its resources from the open story index
            self._index_helper.delete_story(story, self._open_index)
            q = {'story_id':story._id}
            for resource in self._resource_collection.find_models(q):
                self._index_helper.delete_resource(resource, self._open_index)
            self._logger.info('Closed story %s.' % story)
        else:
            self._index_helper.index_story(story, self._open_index)

        # save the story
        self._story_collection.save_model(story)
        self._index_helper.index_story(story, self._main_index)

        self._lock.release()

    def _update_with_resource(self, story, resource):
        """Updates a story with resource information."""

        # features
        self._update_features(story.entities, resource.entities)
        self._update_features(story.terms, resource.terms)

        # current processing time
        current_time = max(story.updated, resource.published)

        # score
        self._update_score(story, resource, current_time)

        # time information
        if story.resource_count == 0:
            story.created = current_time
        story.updated = current_time

        story.resource_count += 1

    def _update_features(self, story_features, resource_features):
        """Resource's scores are added to the story's scores."""

        for k, v in resource_features.iteritems():
            v_story = story_features.get(k, 0)
            story_features[k] = v + v_story

    def _update_score(self, story, resource, current_time):
        """Add the resource score to that of the story.
        
        If the story is open, increase its closing score.
        """

        resource_score = 1.0

        if story.status == STORY_STATUS_OPEN:
            story_score = story.closing_score
            story_time = story.updated

            # test if the closing score has never been computed
            if story_time is None:
                story_time = current_time

            resource_time = resource.published

            story_score *= self._decay_constant ** (current_time - story_time)
            resource_score *= self._decay_constant ** (current_time - resource_time)
            story_score += resource_score

            story.closing_score = story_score

        story.score += resource_score
