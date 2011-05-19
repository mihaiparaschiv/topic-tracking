from datetime import datetime
from pymongo import Connection
from pymongo.errors import DuplicateKeyError
from topic_tracking.model import Resource
import calendar
import feedparser
import logging
import time


class FeedUpdater(object):
    """Reads a feed and inserts new entries."""

    def __init__(self, address, collection, entry_processor):
        self.__address = address
        self.__collection = collection
        self.__entry_processor = entry_processor

    def update(self):
        logging.info('Reading: ' + self.__address)
        feed = feedparser.parse(self.__address)
        for entry in feed.entries:
            self.__process_entry(entry)

    def __process_entry(self, entry):
        res = self.__entry_processor.process(entry)

        try:
            self.__collection.insert_model(res)
            logging.info('Inserted %s' % res._id)
        except DuplicateKeyError:
            pass


class EntryProcessor(object):
    """Builds Resource objects from feedparser entries."""

    def process(self, entry):
        kwargs = self._parse(entry)
        return self._build(kwargs)

    def _parse(self, entry):
        kwargs = {}

        # basic fields
        kwargs['_id'] = entry.link
        kwargs['uri'] = entry.link
        kwargs['type'] = 'article'
        kwargs['discovered'] = time.time()
        kwargs['title'] = entry.title
        kwargs['published'] = calendar.timegm(entry.date_parsed)
        kwargs['author'] = entry.author

        # content
        content = entry.summary
        if entry.has_key('content'):
            c = entry.content[0].value
            if len(c) > len (content):
                content = c
        kwargs['content'] = content

        return kwargs

    def _build(self, kwargs):
        return Resource(**kwargs)
