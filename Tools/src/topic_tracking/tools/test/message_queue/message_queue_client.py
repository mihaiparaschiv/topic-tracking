from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport
from topic_tracking.service.message_queue import MessageQueueService

transport = TSocket.TSocket('localhost', 9091)
transport = TTransport.TFramedTransport(transport)
protocol = TBinaryProtocol.TBinaryProtocol(transport)

client = MessageQueueService.Client(protocol)
transport.open()

queue = 'base'
data = 'cool'
client.put_message(queue, data)

while True:
    message = client.get_message(queue)
    print(message)

transport.close()
