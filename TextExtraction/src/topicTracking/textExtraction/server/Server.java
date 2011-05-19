package topicTracking.textExtraction.server;

import org.apache.thrift.server.TNonblockingServer;
import org.apache.thrift.server.TServer;
import org.apache.thrift.transport.TNonblockingServerSocket;
import org.apache.thrift.transport.TNonblockingServerTransport;

import topicTracking.service.textExtraction.TextExtractionService;

public class Server {
	private static final int PORT = 9090;

	public static void main(final String[] args) throws Exception {
		Handler handler = new Handler();
		TextExtractionService.Processor processor;
		processor = new TextExtractionService.Processor(handler);
		TNonblockingServerTransport serverTransport = new TNonblockingServerSocket(PORT);
		TNonblockingServer.Args serverArgs = new TNonblockingServer.Args(serverTransport);
		TServer server = new TNonblockingServer(serverArgs.processor(processor));

		String str = "Starting the text extraction service on port " + PORT;
		System.out.println(str);

		server.serve();
	}
}
