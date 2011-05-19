from topic_tracking.processing.context import ProcessingContext
from topic_tracking.service.processing.ttypes import ProcessingException
from topic_tracking.util.command import Command
from topic_tracking.util.feature import make_feature_key, normalize_feature_name
from topic_tracking.util.xml import parse_xml
import logging


class AlchemyEntityExtractionCommand(Command):

    _logger = logging.getLogger('processing.commands.AlchemyEntityExtractionCommand')

    def __init__(self, alchemy, cache, min_entity_count):
        self._alchemy = alchemy
        self._cache = cache
        self._min_entity_count = min_entity_count

    def execute(self, context):
        resource = context[ProcessingContext.DISCOVERED_RESOURCE]
        content = context[ProcessingContext.EXTRACTED_CONTENT]

        # cache or API call
        result = self._cache.get(resource.uri)
        if result is None:
            c = content.encode('utf-8')
            try:
                result = self._alchemy.TextGetRankedNamedEntities(c)
            except Exception, e:
                raise ProcessingException(str(e))
            self._cache.put(resource.uri, result)
        else:
            self._logger.debug('Read from cache.')

        # extracted entities
        entities = {}

        # parse the XML data
        tree = parse_xml(result)
        entity_ets = tree.xpath('//entity')

        if len(entity_ets) < self._min_entity_count:
            raise ProcessingException('Insufficient entities')

        for entity_et in entity_ets:
            type = entity_et.find('type').text.lower()
            name = entity_et.find('text').text
            score = float(entity_et.find('relevance').text)

            disambiguated_et = entity_et.find('disambiguated')
            if disambiguated_et is not None:
                name = disambiguated_et.find('name').text

            name = normalize_feature_name(name)

            key = make_feature_key((type, name))
            entities[key] = score

        context[ProcessingContext.EXTRACTED_ENTITIES] = entities
