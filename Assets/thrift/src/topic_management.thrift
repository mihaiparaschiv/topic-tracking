namespace java topicTracking.service.topicManagement
namespace py topic_tracking.service.topic_management


include "exceptions.thrift"
include "types.thrift"


service TopicManagementService {
    
    /**
     * Creates a topic from a set of features.
     * 
     * @param features JSON formatted dictionary of the seed features
     * 
     * @return the new topic's id
     */
    types.ModelId create_from_features(1:types.Features features) throws ()
    
    /**
     * Creates a topic from a story.
     * 
     * @param id Story id
     * 
     * @return the new topic's id
     */
    types.ModelId create_from_story(1:types.ModelId id) throws (1: exceptions.NotFoundException notFound)
    
    /**
     * Creates a topic from a story.
     * 
     * @param id Story id
     * 
     * @return JSON representation of the summary
     */
    string get_summary(1: types.ModelId id, 2: types.Timestamp startTime, 3: types.Timestamp endTime)
}
