package topicTracking.messageQueue.server;

import org.apache.thrift.server.TNonblockingServer;
import org.apache.thrift.server.TServer;
import org.apache.thrift.transport.TNonblockingServerSocket;
import org.apache.thrift.transport.TNonblockingServerTransport;

import topicTracking.service.messageQueue.MessageQueueService;

import com.mongodb.DB;
import com.mongodb.Mongo;

public class Server {
	private static final int PORT = 9091;
	
	// one hundred years in milliseconds
	private static final long RESCHEDULING_DELAY = 3600L * 24 * 365 * 100 * 1000;

	public static void main(final String[] args) throws Exception {
		Mongo mongo = new Mongo();
		DB db = mongo.getDB("queue");
		
		MongoDBHandler handler = new MongoDBHandler(db, RESCHEDULING_DELAY);
		MessageQueueService.Processor processor;
		processor = new MessageQueueService.Processor(handler);
		TNonblockingServerTransport serverTransport = new TNonblockingServerSocket(PORT);
		TNonblockingServer.Args serverArgs = new TNonblockingServer.Args(serverTransport);
		TServer server = new TNonblockingServer(serverArgs.processor(processor));

		String str = "Starting the message queue service on port " + PORT;
		System.out.println(str);

		server.serve();
	}
}
