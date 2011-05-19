from topic_tracking.model import DiscoveredResource, DiscoveredURI
from topic_tracking.model.id import makeIdFromURI
import calendar
import logging
import time


class EntryProcessor(object):
    """Builds Resource objects from feedparser entries."""

    def resources_process(self, source, entry, config):
        
        self._config = config
        
        # configure logging
        logging.config.dictConfig(config['logging'])
        self._logger = logging.getLogger()
        
        # Resource fields
        kwargs = {} 
        
        kwargs['_id'] = makeIdFromURI(entry.link)
        kwargs['uri'] = entry.link
        kwargs['type'] = 'article'
        kwargs['discovered'] = int(time.time())
        kwargs['title'] = entry.title
        
        if 'updated_parsed' in entry:
            kwargs['published'] = calendar.timegm(entry.updated_parsed)
        elif 'date_parsed' in entry:
            kwargs['published'] = calendar.timegm(entry.date_parsed)
        else:
            kwargs['published'] = None

        if 'author' in entry:
            kwargs['author'] = entry.author

        # content
        content = ''
        if 'summary' in entry:
            content = entry.summary
        if 'content' in entry:
            c = entry.content[0].value
            if len(c) > len (content):
                content = c
        kwargs['feed_content'] = content
        kwargs['content'] = ''
        kwargs['source'] = source
        kwargs['content_extracted'] = 1

        return DiscoveredResource(**kwargs)
    
    def discovered_uri_process(self, entry):
        
        # Resource fields
        kwargs = {}

        kwargs['_id'] = makeIdFromURI(entry.link)
        kwargs['uri'] = entry.link

        return DiscoveredURI(**kwargs)
