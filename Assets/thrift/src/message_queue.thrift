namespace java topicTracking.service.messageQueue
namespace py topic_tracking.service.message_queue


struct Message {
    1: string id,
    2: string body
}

exception EmptyQueueException {
}

service MessageQueueService {
    void clear_queue(1: string queue),
    string put_message(1: string queue, 2: string body),
    Message get_message(1: string queue) throws (1: EmptyQueueException empty),
    void delete_message(1: string queue, 2: string id)
}
