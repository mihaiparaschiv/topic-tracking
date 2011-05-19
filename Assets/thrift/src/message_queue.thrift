namespace java topicTracking.service.messageQueue
namespace py topic_tracking.service.message_queue


struct Message {
    1: string id,
    2: string body
}

exception EmptyQueueException {
}

service MessageQueueService {
    void clearQueue(1: string queue),
    string putMessage(1: string queue, 2: string body),
    Message getMessage(1: string queue) throws (1: EmptyQueueException empty),
    void deleteMessage(1: string queue, 2: string id)
}
