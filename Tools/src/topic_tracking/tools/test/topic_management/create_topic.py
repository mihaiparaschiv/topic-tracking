from topic_tracking.model import Topic
from topic_tracking.topic_management.topic_manager import TopicManager
from topic_tracking.util.codec.mongo_codec import MongoCodec
from topic_tracking.util.mongo import MongoConnectionManager


if __name__ == '__main__':

    # MongoDB
    host = 'localhost'
    port = 27017
    mcm = MongoConnectionManager(host, port, MongoCodec())
    database = 'processed'
    topic_collection = mcm.get_collection(database, 'topics', Topic)

    # utilities
    topic_manager = TopicManager(topic_collection)

    # topic properties
    title = "North Korea conflict"
    terms = {}
    entities = {'country_north-korea': 1}

    topic = topic_manager.create_from_features(title, terms, entities)

    print(topic)
