namespace java topicTracking.service.storyUpdating
namespace py topic_tracking.service.story_updating


include "exceptions.thrift"


service StoryUpdatingService {
    void update(1:string id) throws (1: exceptions.NotFoundException notFound)
}
