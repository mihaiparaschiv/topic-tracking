from topic_tracking.service.types.ttypes import DiscoveredResource, \
    DiscoveredURI, Feed, Resource, Story, StoryUpdate, Topic


# list of fields that are displayed by __str__
_fields = {}
_fields[DiscoveredResource] = ('_id', 'uri')
_fields[DiscoveredURI] = ('_id', 'uri')
_fields[Feed] = ('_id', 'uri')
_fields[Resource] = ('_id', 'uri', 'title')
_fields[Story] = ('_id', 'title')
_fields[StoryUpdate] = ('_id', 'story_id', 'type')
_fields[Topic] = ('_id', 'title')


def _str(self):
    fields = self.__class__._str_fields
    s = ['%s=%r' % (key, self.__dict__[key]) for key in fields]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(s))


# replace the __str__ method for each model class
for kls, fields in _fields.iteritems():
    kls._str_fields = fields
    kls.__str__ = _str
