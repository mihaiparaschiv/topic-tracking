from pymongo.errors import DuplicateKeyError
from topic_tracking.constants import STORY_UPDATE_RESOURCE_INSERTED
from topic_tracking.model import Resource, StoryUpdate
from topic_tracking.model.id import makeIdFromURI
from topic_tracking.service.message_queue.ttypes import EmptyQueueException
import logging
import time


class ProcessedResourceHandler(object):

    _logger = logging.getLogger('model_management.ProcessedResourceHandler')

    EMPTY_QUEUE_TIMEOUT = 1

    def __init__(self, mq_client, mq_codec, processed_resource_queue,
            resource_collection, update_collection, su_client, index_helper, index, story_provider):

        # message queue
        self._mq_client = mq_client
        self._mq_codec = mq_codec
        self._processed_resource_queue = processed_resource_queue

        # mongo
        self._resource_collection = resource_collection
        self._update_collection = update_collection

        # story updating
        self._su_client = su_client

        # utilities
        self._index_helper = index_helper
        self._index = index
        self._story_provider = story_provider

    def start(self):
        while True:
            try:
                # dequeue a processed resource
                message = self._mq_client.getMessage(self._processed_resource_queue)
                resource = self._mq_codec.decode(message.body, Resource)
            except EmptyQueueException:
                self._logger.info('Empty queue. Sleeping...')
                time.sleep(self.EMPTY_QUEUE_TIMEOUT)
                continue

            resource._id = makeIdFromURI(resource.uri)
            story = self._story_provider.provide_for_resource(resource)
            resource.story_id = story._id

            try:
                # save and index the resource
                self._resource_collection.insert_model(resource)
                self._index_helper.index_resource(resource, self._index)
                self._logger.debug('Resource %s: Inserted and indexed.' % resource._id)

                # queue update
                update = StoryUpdate()
                update.story_id = story._id
                update.type = STORY_UPDATE_RESOURCE_INSERTED
                update.value = resource._id
                self._update_collection.insert_model(update)

                self._su_client.update(story._id)

            except DuplicateKeyError:
                self._logger.warning('Resource %s: Already inserted.' % resource._id)

            # delete the queue message
            self._mq_client.deleteMessage(self._processed_resource_queue, message.id)
