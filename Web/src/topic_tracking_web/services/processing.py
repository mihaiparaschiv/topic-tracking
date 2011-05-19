from django.conf import settings
from topic_tracking.util.from_config import processing_client_from_config


_pc = processing_client_from_config(settings.CONFIG['processing']['client'])


def get_processing_service_client():
    if not _pc.is_connected():
        _pc.connect()
    return _pc
