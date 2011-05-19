from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport
from topic_tracking.service.text_extraction import TextExtractionService
from topic_tracking.util.http import detect_header_encoding
from topic_tracking.util.xml import decode_html
import urllib

transport = TSocket.TSocket('localhost', 9090)
transport = TTransport.TFramedTransport(transport)
protocol = TBinaryProtocol.TBinaryProtocol(transport)

url = 'http://edition.cnn.com/2010/US/11/29/wikileaks.new.documents/index.html?hpt=T1'
handle = urllib.urlopen(url)
encoding = detect_header_encoding(handle.headers.dict)
html = decode_html(handle.read(), encoding)

client = TextExtractionService.Client(protocol)
transport.open()
content = client.extract(html)
transport.close()

print(content.__class__)
print(content)
