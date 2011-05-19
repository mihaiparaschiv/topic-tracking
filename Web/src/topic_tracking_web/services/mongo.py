from django.conf import settings
from topic_tracking.model import Resource, Story, Topic
from topic_tracking.util.from_config import mongo_from_config


_mcm = mongo_from_config(settings.CONFIG['mongo'])
_db = settings.CONFIG['mongo']['databases']['processed']


def get_connection_manager():
    return _mcm

def get_resource_collection():
    return _mcm.get_collection(_db, 'resources', Resource)

def get_stories_collection():
    return _mcm.get_collection(_db, 'stories', Story)

def get_topics_collection():
    return _mcm.get_collection(_db, 'topics', Topic)
