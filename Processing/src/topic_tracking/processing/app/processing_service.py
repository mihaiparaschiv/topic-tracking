from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.transport import TSocket
from thrift.transport.TTransport import TFramedTransportFactory
from AlchemyAPI import AlchemyAPI
from topic_tracking.cache import MongoCache
from topic_tracking.processing.command.alchemy_entity_extraction import \
    AlchemyEntityExtractionCommand
from topic_tracking.processing.command.building import BuildingCommand
from topic_tracking.processing.command.parsing import ParsingCommand
from topic_tracking.processing.command.term_extraction import \
    TermExtractionCommand
from topic_tracking.processing.command.text_extraction import \
    TextExtractionCommand
from topic_tracking.processing.processing_handler import ProcessingHandler
from topic_tracking.service.processing import ProcessingService
from topic_tracking.util.from_config import mongo_from_config, \
    text_extraction_client_from_config
from topic_tracking.util.lemmatization import Lemmatizer
import logging.config
import sys
import yaml


if __name__ == '__main__':

    config_file = sys.argv[1]
    config = yaml.load(file(config_file, 'r'))

    # logging
    logging.config.dictConfig(config['logging'])
    logger = logging.getLogger()

    # MongoDB
    mcm = mongo_from_config(config['mongo'])

    # text extraction
    te_client = text_extraction_client_from_config(config['text_extraction']['client'])

    # cache database
    cache_db = config['mongo']['databases']['cache']

    # commands
    commands = list()

    # command: TextExtraction
    min_content_length = config['processing']['commands'] \
        ['text_extraction']['min_content_length']
    commands.append(TextExtractionCommand(te_client, min_content_length))

    # command: Parsing
    commands.append(ParsingCommand())

    # command: TermExtraction
    lemmatizer = Lemmatizer()
    min_term_count = config['processing']['commands'] \
        ['term_extraction']['min_term_count']
    commands.append(TermExtractionCommand(lemmatizer, min_term_count))

    # command: AlchemyEntityExtraction
    alchemy = AlchemyAPI()
    alchemy.setAPIKey(config['alchemyapi']['key'])
    alchemy_cache_collection = mcm.connection[cache_db][config['alchemyapi']['cache']['namespace']]
    alchemy_cache = MongoCache(alchemy_cache_collection)
    min_entity_count = config['processing']['commands'] \
        ['entity_extraction']['min_entity_count']
    commands.append(AlchemyEntityExtractionCommand(alchemy, alchemy_cache, min_entity_count))

    # command: Building
    commands.append(BuildingCommand())

    # start service clients
    te_client.connect()

    # set up the server
    handler = ProcessingHandler(commands)
    processor = ProcessingService.Processor(handler)
    port = config['processing']['server']['port']
    serverTransport = TSocket.TServerSocket(port)
    serverTransport.host = 'localhost'
    transportFactory = TFramedTransportFactory()
    protocolFactory = TBinaryProtocol.TBinaryProtocolFactory()
    server = TServer.TThreadedServer(processor, serverTransport,
        transportFactory, protocolFactory)

    # start the server
    logging.info('Starting the processing service on port %d.' % port)
    server.serve()

    # close service clients
    te_client.disconnect()
