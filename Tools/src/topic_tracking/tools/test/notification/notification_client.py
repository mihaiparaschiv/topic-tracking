from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport
from topic_tracking.service.notification import NotificationService
from topic_tracking.service.notification.constants import PROTOCOL_MESSAGE_QUEUE

transport = TSocket.TSocket('localhost', 9092)
transport = TTransport.TFramedTransport(transport)
protocol = TBinaryProtocol.TBinaryProtocol(transport)

client = NotificationService.Client(protocol)
transport.open()

topic = 'test'
protocol = PROTOCOL_MESSAGE_QUEUE
endpoint = "test-notifications"
client.subscribe(topic, protocol, endpoint)

body = 'The great notification service works!'
client.publish(topic, body)

print('Notification sent.')

transport.close()
