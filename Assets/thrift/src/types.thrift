namespace java topicTracking.service.types
namespace py topic_tracking.service.types


typedef i64 Timestamp
typedef map<string,double> Features
typedef string ModelId


/* General *******************************************************************/

struct Resource {
    1:  required    ModelId     _id,
    2:  optional    string      uri,
    3:  optional    string      type,
    4:  optional    Timestamp   discovered,
    5:  optional    string      title,
    6:  optional    string      content,
    7:  optional    Timestamp   published,
    8:  optional    string      author,
    9:  optional    ModelId     story_id,
    10: optional    Features    terms,
    11: optional    Features    entities
}

struct Story {
    1:  required    ModelId     _id,
    2:  optional    string      title,
    3:  optional    string      status,
    4:  optional    Timestamp   created,
    5:  optional    Timestamp   updated,
    6:  optional    i32         resource_count,
    7:  optional    double      score,
    8:  optional    double      closing_score,
    9:  optional    bool        closing_closed,
    10: optional    Features    terms,
    11: optional    Features    entities
}

struct Topic {
    1:  required    ModelId     _id,
    2:  optional    string      title,
    3:  optional    string      status,
    4:  optional    Timestamp   created,
    5:  optional    Timestamp   updated,
    6:  optional    Features    terms,
    7:  optional    Features    entities
}

struct StoryUpdate {
    1:  required    ModelId     _id,
    2:  optional    ModelId     story_id,
    3:  optional    string      type,
    4:  optional    string      value
}


/* Discovery *****************************************************************/

struct DiscoveredResource {
    1:  required    ModelId     _id,
    2:  optional    string      uri,
    3:  optional    string      type,
    4:  optional    Timestamp   discovered,
    5:  optional    string      title,
    6:  optional    string      content,
    7:  optional    Timestamp   published,
    8:  optional    string      author,
    9:  optional    i32         source,
    10: optional    i32         content_extracted,
    11: optional    string      feed_content
}

struct Feed {
    1:  required    ModelId     _id,
    2:  optional    string      uri,
    3:  optional    string      source,
    4:  optional    Timestamp   next_reading
}

struct DiscoveredURI {
    1:  required    ModelId     _id,
    2:  required    string      uri
}