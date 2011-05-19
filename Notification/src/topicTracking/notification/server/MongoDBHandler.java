package topicTracking.notification.server;

import org.apache.thrift.TException;

import topicTracking.service.exceptions.InvalidArgumentException;
import topicTracking.service.messageQueue.MessageQueueService;
import topicTracking.service.messageQueue.MessageQueueService.Client;
import topicTracking.service.notification.Constants;
import topicTracking.service.notification.NotificationService;

import com.mongodb.BasicDBObject;
import com.mongodb.DB;
import com.mongodb.DBCollection;
import com.mongodb.DBCursor;
import com.mongodb.DBObject;
import com.mongodb.MongoException.DuplicateKey;
import com.mongodb.WriteConcern;
import com.mongodb.util.JSON;

public class MongoDBHandler implements NotificationService.Iface {

	private final DBCollection subscriptionCollection;
	private Client mq_client;

	public MongoDBHandler(DB db, MessageQueueService.Client mq_client) {
		this.subscriptionCollection = db.getCollection("subscriptions");
		this.mq_client = mq_client;
		db.setWriteConcern(WriteConcern.SAFE);
	}

	@Override
	public void subscribe(String topic, String protocol, String endpoint)
			throws InvalidArgumentException, TException {
		if (!protocol.equals(Constants.PROTOCOL_MESSAGE_QUEUE)) {
			throw new InvalidArgumentException();
		}

		DBObject document = new BasicDBObject();
		String _id = topic + '_' + protocol + '_' + endpoint;
		document.put("_id", _id);
		document.put("topic", topic);
		document.put("protocol", protocol);
		document.put("endpoint", endpoint);
		
		try {
			subscriptionCollection.insert(document);
		} catch (DuplicateKey e) {
		}
	}

	@Override
	public void unsubscribe(String topic, String protocol, String endpoint)
			throws TException {
		DBObject document = new BasicDBObject();
		document.put("topic", topic);
		document.put("protocol", protocol);
		document.put("endpoint", endpoint);
		subscriptionCollection.remove(document);
	}

	@Override
	public void publish(String topic, String body) throws TException {
		DBObject notification = new BasicDBObject();
		notification.put("topic", topic);
		notification.put("body", body);
		notification.put("created_at", System.currentTimeMillis());

		DBObject query = new BasicDBObject();
		query.put("topic", topic);

		DBCursor subscriptions = subscriptionCollection.find(query);

		for (DBObject subscription : subscriptions) {
			String protocol = subscription.get("protocol").toString();
			String endpoint = subscription.get("endpoint").toString();
			if (protocol.equals(Constants.PROTOCOL_MESSAGE_QUEUE)) {
				sendToQueue(endpoint, notification);
			}
		}
	}

	private void sendToQueue(String queue, DBObject notification) {
		String body = JSON.serialize(notification);
		try {
			mq_client.put_message(queue, body);
		} catch (TException e) {
			e.printStackTrace();
		}
	}

}
