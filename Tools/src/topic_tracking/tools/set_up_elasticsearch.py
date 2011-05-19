import logging.config
import sys
import yaml
from topic_tracking.util.from_config import elasticsearch_from_config


if __name__ == '__main__':

    config_file = sys.argv[1]
    config = yaml.load(file(config_file, 'r'))

    # logging
    logging.config.dictConfig(config['logging'])
    logger = logging.getLogger()

    # elasticsearch
    es = elasticsearch_from_config(config['elasticsearch'])

    # load settings
    settings_file = sys.argv[2]
    settings = yaml.load(file(settings_file, 'r'))

    # set up mappings
    for index, type_mappings in settings['mappings'].iteritems():
        es.create_index(index)
        logger.info('Index %s created.' % index)
        for type, mapping in type_mappings.iteritems():
            es.put_mapping(type, mapping, index)
            logger.info('Mapping for %s.%s added.' % (index, type))
