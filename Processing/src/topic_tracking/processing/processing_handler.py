from topic_tracking.processing.context import ProcessingContext
from topic_tracking.service.processing import ProcessingService
from topic_tracking.service.processing.ttypes import ProcessingException
import logging
import time


class ProcessingHandler(ProcessingService.Iface):

    _logger = logging.getLogger('processing.ProcessingHandler')

    def __init__(self, commands):
        self._commands = commands

    def process(self, discoveredResource):
        context = ProcessingContext()
        context[ProcessingContext.DISCOVERED_RESOURCE] = discoveredResource
        self._logger.info('Processing: %s' % discoveredResource)

        try:
            t1 = time.clock()
            for command in self._commands:
                t2 = time.clock()
                command.execute(context)
                t3 = time.clock()
                self._logger.debug('%s: %f' % (command.__class__.__name__, (t3 - t2)))
            t4 = time.clock()
            self._logger.debug('Success: %f' % (t4 - t1))
            resource = context[ProcessingContext.BUILT_RESOURCE]
            return resource
        except ProcessingException, e:
            self._logger.error(e)
            raise e


