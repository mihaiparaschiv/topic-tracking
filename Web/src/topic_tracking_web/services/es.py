from django.conf import settings
from topic_tracking.util.from_config import elasticsearch_from_config


_es = elasticsearch_from_config(settings.CONFIG['elasticsearch'])
_main_index = settings.CONFIG['elasticsearch']['indexes']['main']


def get_es():
    return _es

def get_es_main_index():
    return _main_index
