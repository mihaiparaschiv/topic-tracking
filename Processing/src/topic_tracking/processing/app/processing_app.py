from topic_tracking.model import DiscoveredResource
from topic_tracking.service.message_queue.ttypes import EmptyQueueException
from topic_tracking.service.processing.ttypes import ProcessingException
from topic_tracking.util.codec.json_codec import JSONCodec
from topic_tracking.util.from_config import message_queue_client_from_config, \
    processing_client_from_config
import logging.config
import sys
import time
import yaml


EMPTY_QUEUE_TIMEOUT = 1


if __name__ == '__main__':

    config_file = sys.argv[1]
    config = yaml.load(file(config_file, 'r'))

    # logging
    logging.config.dictConfig(config['logging'])
    logger = logging.getLogger()

    # message queue
    mq_client = message_queue_client_from_config(config['message_queue']['client'])
    mq_codec = JSONCodec()
    input_queue = 'discovered_resources'
    output_queue = 'processed_resources'

    # processing
    p_client = processing_client_from_config(config['processing']['client'])

    # start service clients
    mq_client.connect()
    p_client.connect()

    # begin processing
    while True:
        try:
            # input
            input_message = mq_client.get_message(input_queue)
            discovered_resource = mq_codec.decode(input_message.body, DiscoveredResource)
            logger.info('Dequeued discovered resource: %s ' % discovered_resource)

            try:
                # process
                resource = p_client.process(discovered_resource)
                # output
                msg_body = mq_codec.encode(resource)
                mq_client.put_message(output_queue, msg_body)
                logger.info('Enqueued processed resource: %s ' % resource)
            except ProcessingException, e:
                logger.error(e)

            # delete the input message
            mq_client.delete_message(input_queue, input_message.id)
        except EmptyQueueException:
            logger.info('Empty queue. Sleeping...')
            time.sleep(EMPTY_QUEUE_TIMEOUT)

    # close service clients
    mq_client.disconnect()
    p_client.disconnect()
