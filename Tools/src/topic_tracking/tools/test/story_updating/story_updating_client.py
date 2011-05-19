from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport
from topic_tracking.service.story_updating import StoryUpdatingService

transport = TSocket.TSocket('localhost', 9093)
transport = TTransport.TFramedTransport(transport)
protocol = TBinaryProtocol.TBinaryProtocol(transport)

client = StoryUpdatingService.Client(protocol)
transport.open()
client.update('fake story id')
transport.close()

print('ready')
