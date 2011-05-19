from pymongo.errors import DuplicateKeyError
from topic_tracking.model import Feed
from topic_tracking.util.from_config import mongo_from_config
import calendar
import logging.config
import sys
import time
import yaml

now = time.time()
time = calendar.timegm(time.gmtime(now))

if __name__ == '__main__':

    config_file = sys.argv[1]
    config = yaml.load(file(config_file, 'r'))

    # logging
    logging.config.dictConfig(config['logging'])
    logger = logging.getLogger()

    # MongoDB
    mcm = mongo_from_config(config['mongo'])

    # Collection: discovery
    database = config['mongo']['databases']['discovery']
    feeds_collection = mcm.get_collection(database, 'feeds', Feed)
    
    feeds_collection.ensure_index('_id')

    # update feed list
    file_name = config['app']['feed_reading']['feeds_file']
    print "Reading from ", file_name
    f = open(file_name)
    source = 0
    
    # inserts lines in the database
    for line in f:
        if line[0] == '#':
            pass
        else:
            try:
                source = int(line)
            except ValueError:
                line = line.replace('"', '').replace("'", "").replace('\n', '')
                
                feed = Feed(_id=line, uri=line, source=source, next_reading=time)
                try:
                    feeds_collection.insert_model(feed)
                    logger.info('Added feed %s' % feed._id)
                except DuplicateKeyError:
                    logger.info('Duplicated feed %s' % feed._id)
                    pass
    f.close()
