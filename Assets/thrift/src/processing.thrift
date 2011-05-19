namespace java topicTracking.service.processing
namespace py topic_tracking.service.processing


include "types.thrift"


exception ProcessingException {
    1:  optional    string      message,
}


service ProcessingService {
    types.Resource process(1:types.DiscoveredResource discoveredResource)
        throws (1: ProcessingException processingException),
}
