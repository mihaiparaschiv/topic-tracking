from pyes.es import ES
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport, THttpClient
from topic_tracking.service.message_queue import MessageQueueService
from topic_tracking.service.processing import ProcessingService
from topic_tracking.service.story_updating import StoryUpdatingService
from topic_tracking.service.text_extraction import TextExtractionService
from topic_tracking.util.codec.mongo_codec import MongoCodec
from topic_tracking.util.mongo import MongoConnectionManager
from topic_tracking.util.thrift_client import ThriftClientWrapper


def mongo_from_config(config):
    host = config['host']
    port = config['port']
    return MongoConnectionManager(host, port, MongoCodec())


def elasticsearch_from_config(config):
    host = config['host']
    port = config['port']
    server = '%s:%d' % (host, port)
    timeout = config['timeout']
    return ES(server, timeout)


def _thrift_service_from_config(config, thrift_factory, client_wrapper_factory):
    # set up the transport
    transport = None
    c_transport = config['transport']
    if c_transport == 'socket':
        c_host = config['host']
        c_port = int(config['port'])
        transport = TSocket.TSocket(c_host, c_port)
        transport = TTransport.TFramedTransport(transport)
    elif c_transport == 'http':
        transport = THttpClient

    # set up the protocol
    protocol = None
    c_protocol = config['protocol']
    if c_protocol == 'binary':
        protocol = TBinaryProtocol.TBinaryProtocol(transport)

    thrift_client = thrift_factory(protocol)
    return client_wrapper_factory(thrift_client)


def message_queue_client_from_config(config):
    return _thrift_service_from_config(config,
        MessageQueueService.Client, ThriftClientWrapper)


def text_extraction_client_from_config(config):
    return _thrift_service_from_config(config,
        TextExtractionService.Client, ThriftClientWrapper)


def story_updating_client_from_config(config):
    return _thrift_service_from_config(config,
        StoryUpdatingService.Client, ThriftClientWrapper)


def processing_client_from_config(config):
    return _thrift_service_from_config(config,
        ProcessingService.Client, ThriftClientWrapper)
