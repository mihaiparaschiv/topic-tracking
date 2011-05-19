from topic_tracking.constants import FEATURE_SEPARATOR
import re
import unicodedata


def make_feature_key(key):
    if isinstance(key, (tuple, list)):
        key = FEATURE_SEPARATOR.join(key)
    return unicode(key)


def normalize_feature_name(value):
    value = unicode(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    value = re.sub('[-\s]+', '-', value)
    return value