"""Output resources have an id equal to their URI. This assures that any duplicates
which result from the discovery process are removed.
"""
from pymongo import DESCENDING
from pymongo.connection import Connection
from pymongo.errors import DuplicateKeyError, CollectionInvalid
from topic_tracking.discovery.processing.entry_processing import EntryProcessor
from topic_tracking.model import Feed, DiscoveredResource
from topic_tracking.util.from_config import mongo_from_config
import calendar
import feedparser
import logging.config
import sys
import time
import yaml

class FeedCrawler(object):
    
    def __init__(self, feeds_collection, resources_collection, config):
        self._feeds_collection = feeds_collection
        self._resources_collection = resources_collection
        self._config = config
        
        # configure logging
        logging.config.dictConfig(config['logging'])
        self._logger = logging.getLogger()
    
    def compute_next_reading(self, line):

        start_time = int(time.time())
        now_int = time.gmtime(start_time)

        # last 5 updates for our feed(line), sorted by the published date
        last_entries = []
        spec = {'feed': line}
        feeds = self._feeds_collection.find_models(spec, timeout=False).sort('published', DESCENDING).limit(5)
        
        for x in feeds:
            last_entries.append(x['published'])

        if not last_entries:
            return now_int
        
        else:
            aux = []
            for i in range(1, len(last_entries)):
                aux.append(last_entries[i - 1] - last_entries[i])
    
            try:
                average = float(sum(aux)) / len(aux)
            except ZeroDivisionError:
                return time.gmtime(last_entries[0])
                pass
            return time.gmtime(last_entries[0] + average)
        
    def add(self):
        
        feeds = self._feeds_collection.find_models(timeout=False).sort('next_reading', DESCENDING)

        # Discovered URI - capped collection
        mongoConnection = Connection()
        db = mongoConnection.feed_reading_discovery
        try:
            discovered_uri_collection = db.create_collection('discovered_uri', capped=True, size=500 * 1048576, max=5000)
        except CollectionInvalid:
            discovered_uri_collection = db['discovered_uri']
        db.discovered_uri.ensure_index('_id')

        for feed in feeds:
        
            line = feed._id
            source = feed.source
            
            d = feedparser.parse(line)
            print line
            
            # add the articles from the feed to the resources_collection
            for i in range(0, len(d.entries)):
    
                entry = d.entries[i]
                
                # feed reading
                entry_processor = EntryProcessor()
                resource = entry_processor.resources_process(source, entry, self._config)
                resource_uri = entry_processor.discovered_uri_process(entry)
                
                try:
                    resources_collection.insert_model(resource)
                    self._logger.info('Added article ID %s' % resource._id)
                    db.discovered_uri.insert({'_id':resource_uri._id, 'uri':resource_uri.uri})
                    
                    # modify the next reading 
                    feed.next_reading = calendar.timegm(self.compute_next_reading(line))
                    self._feeds_collection.update_model(feed)
                
                except DuplicateKeyError:
                    pass

    def add_from_scratch(self):

        # creates an index for "_id"
        resources_collection.ensure_index('_id')
        
        # add articles
        # TODO: modify so that it adds in order
        self.add()
        
if __name__ == '__main__':
   
    # configuration
    config_file = sys.argv[1]
    config = yaml.load(file(config_file, 'r'))

    # MongoDB
    mcm = mongo_from_config(config['mongo'])
    
    # Collection: discovery
    database = config['mongo']['databases']['discovery']
    feeds_collection = mcm.get_collection(database, 'feeds', Feed)
    resources_collection = mcm.get_collection(database, 'resources', DiscoveredResource)

    # start feed crawler
    feed_crawler = FeedCrawler(feeds_collection, resources_collection, config)
    feed_crawler.add_from_scratch()
    while True:
        feed_crawler.add()
