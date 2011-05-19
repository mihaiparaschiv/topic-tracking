package topicTracking.notification.server;

import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.protocol.TProtocol;
import org.apache.thrift.server.TNonblockingServer;
import org.apache.thrift.server.TServer;
import org.apache.thrift.transport.TFramedTransport;
import org.apache.thrift.transport.TNonblockingServerSocket;
import org.apache.thrift.transport.TNonblockingServerTransport;
import org.apache.thrift.transport.TSocket;
import org.apache.thrift.transport.TTransport;

import topicTracking.service.messageQueue.MessageQueueService;
import topicTracking.service.notification.NotificationService;

import com.mongodb.DB;
import com.mongodb.Mongo;

public class Server {
	private static final int PORT = 9092;

	public static void main(final String[] args) throws Exception {
		
		// mongo
		Mongo mongo = new Mongo();
		DB db = mongo.getDB("notification_service");
		
		// message queue client
		TTransport tr = new TSocket("localhost", 9091);
		tr = new TFramedTransport(tr);
        TProtocol proto = new TBinaryProtocol(tr);
        MessageQueueService.Client mq_client = new MessageQueueService.Client(proto);
		
        // notification service server
		MongoDBHandler handler = new MongoDBHandler(db, mq_client);
		NotificationService.Processor processor;
		processor = new NotificationService.Processor(handler);
		TNonblockingServerTransport serverTransport = new TNonblockingServerSocket(PORT);
		TNonblockingServer.Args serverArgs = new TNonblockingServer.Args(serverTransport);
		TServer server = new TNonblockingServer(serverArgs.processor(processor));
		
		String str = "Connecting to the MessageQueue Service";
		System.out.println(str);
        tr.open();

		str = "Starting the notification service on port " + PORT;
		System.out.println(str);

		server.serve();
	}
}
