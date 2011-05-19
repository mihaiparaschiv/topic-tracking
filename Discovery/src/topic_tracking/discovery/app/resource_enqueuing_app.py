"""Takes discovered resources and enqueues them for processing."""

from bson.errors import InvalidStringData
from httplib import HTTPException
from pymongo.connection import Connection
from pymongo.errors import DuplicateKeyError
from threading import Thread
from topic_tracking.model import DiscoveredResource
from topic_tracking.model.id import makeIdFromURI
from topic_tracking.util.codec.json_codec import JSONCodec
from topic_tracking.util.from_config import mongo_from_config, \
    message_queue_client_from_config
from topic_tracking.util.http import detect_header_encoding
from topic_tracking.util.thread import WorkerPool
from topic_tracking.util.xml import decode_html
from urllib2 import HTTPRedirectHandler
import logging.config
import sys
import urllib2
import yaml



class WebPageLoader(Thread):

    def __init__(self, resources_collection, opener, config, worker_pool_size=5):
        super(WebPageLoader, self).__init__()
        self._worker_pool = WorkerPool(worker_pool_size)
        self._resources_collection = resources_collection
        self._opener = opener

        logging.config.dictConfig(config['logging'])
        self._logger = logging.getLogger()

    def run(self):

        while True:
            # add the web page processing task  
            for resource in self._resources_collection.find_models():
                self._worker_pool.add_task(self._process_web_page, resource)

    def _process_web_page(self, resource):

        # if the 'http://' doesn't exist
        if (resource.uri[:7] != 'http://'):
            resource.uri = 'http://' + resource.uri
        entire_content = ''

        try:
            handle = self._opener.open(resource.uri)
            resource.uri = handle.url
            encoding = detect_header_encoding(handle.headers.dict)
            entire_content = decode_html(handle.read(), encoding)
            resource.content = entire_content
            handle.close()
            self._logger.info('Reading %s. Success.' % resource.uri)
            self._enqueue(resource)
        except (IOError, HTTPException), e:
            # mark for retry
            self._logger.error('Reading %s. IO error %s.' % (resource.uri, e))
        except UnicodeDecodeError, e:
            # mark for no more retries
            self._logger.error('Reading %s. Unicode error %s.' % (resource.uri, e))
        except InvalidStringData:
            self._logger.error('String not valid')

    def _enqueue(self, resource):

        # Discovered URI - capped collection --db.discovered_uri
        mongoConnection = Connection()
        db = mongoConnection.feed_reading_discovery

        # settings
        max_content_length = config['discovery']['resource_enqueueing']['max_content_length']

        # message queue
        mq_client = message_queue_client_from_config(config['message_queue']['client'])
        mq_client.connect()
        mq_codec = JSONCodec()
        queue = 'discovered_resources'

        try:
            #insert into capped
            db.discovered_uri.insert({'_id':makeIdFromURI(resource.uri), 'uri':resource.uri})
            #insert into queue
            if len(resource.content) > max_content_length:
                self._logger.warning('Skipped %s: Content length is %s.' %
                    (resource, len(resource.content)))
            msg_body = mq_codec.encode(resource)
            mq_client.putMessage(queue, msg_body)
            self._logger.debug("Enqueued: %s" % resource._id)
        except DuplicateKeyError:
            pass

        # remove resource from collection
        self._resources_collection.remove_model(resource)


if __name__ == '__main__':

    # configuration file
    config_file = sys.argv[1]
    config = yaml.load(file(config_file, 'r'))

    # logging
    logging.config.dictConfig(config['logging'])
    logger = logging.getLogger()

    # MongoDB
    mcm = mongo_from_config(config['mongo'])
    database = config['mongo']['databases']['discovery']
    resources_collection = mcm.get_collection(database, 'resources', DiscoveredResource)

    # url opener
    redirect_handler = HTTPRedirectHandler()
    redirect_handler.max_redirections = config['url']['max_redirections']
    opener = urllib2.build_opener(redirect_handler)

    # load pages to the queue
    loader = WebPageLoader(resources_collection, opener, config)
    loader.start()

