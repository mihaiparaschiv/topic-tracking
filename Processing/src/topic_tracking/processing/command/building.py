from topic_tracking.model import Resource
from topic_tracking.processing.context import ProcessingContext
from topic_tracking.util.command import Command
import logging


class BuildingCommand(Command):

    _logger = logging.getLogger('processing.commands.BuildingCommand')

    def __init__(self):
        pass

    def execute(self, context):
        discovered_resource = context[ProcessingContext.DISCOVERED_RESOURCE]

        # copy fields from input resource
        fields = ('uri', 'type', 'discovered', 'title', 'published', 'author')
        data = {}
        for field in fields:
            data[field] = getattr(discovered_resource, field)

        # add extracted fields
        data['content'] = context[ProcessingContext.EXTRACTED_CONTENT]
        data['terms'] = context[ProcessingContext.EXTRACTED_TERMS]
        data['entities'] = context[ProcessingContext.EXTRACTED_ENTITIES]

        # build resource 
        resource = Resource(**data)
        context[ProcessingContext.BUILT_RESOURCE] = resource
