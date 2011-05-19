namespace java topicTracking.service.notification
namespace py topic_tracking.service.notification


include "exceptions.thrift"


const string PROTOCOL_MESSAGE_QUEUE = "message_queue"


struct Notification {
    1: string body
}

service NotificationService {
    void subscribe(1: string topic, 2: string protocol, 3: string endpoint)
         throws (1: exceptions.InvalidArgumentException invalidArgument),
    void unsubscribe(1: string topic, 2: string protocol, 3: string endpoint),
    void publish(1: string topic, 2: string body)
}
