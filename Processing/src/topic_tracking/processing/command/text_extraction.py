from topic_tracking.processing.context import ProcessingContext
from topic_tracking.service.processing.ttypes import ProcessingException
from topic_tracking.util.command import Command


class TextExtractionCommand(Command):
    """Extracts the text from the HTML page using the dedicated service."""

    def __init__(self, te_client, min_content_length):
        self._te_client = te_client
        self._min_content_length = min_content_length

    def execute(self, context):
        resource = context[ProcessingContext.DISCOVERED_RESOURCE]
        content = self._te_client.extract(resource.content)

        if len(content) < self._min_content_length:
            raise ProcessingException('Insufficient content')

        context[ProcessingContext.EXTRACTED_CONTENT] = content
