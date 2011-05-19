package topicTracking.messageQueue.server;

import org.apache.thrift.TException;
import org.bson.types.ObjectId;

import topicTracking.service.messageQueue.EmptyQueueException;
import topicTracking.service.messageQueue.Message;
import topicTracking.service.messageQueue.MessageQueueService;

import com.mongodb.BasicDBObject;
import com.mongodb.DB;
import com.mongodb.DBCollection;
import com.mongodb.DBObject;
import com.mongodb.WriteConcern;

public class MongoDBHandler implements MessageQueueService.Iface {

	private static final long START_BACK_TIME = 10000;
	private final DB db;
	private final long reschedulingDelay;

	public MongoDBHandler(DB db, long reschedulingDelay) {
		this.db = db;
		this.reschedulingDelay = reschedulingDelay;
		db.setWriteConcern(WriteConcern.SAFE);
	}

	private DBCollection prepareCollection(String queue) {
		DBCollection collection = db.getCollection(queue);
		collection.ensureIndex("scheduled_at");
		return collection;
	}

	@Override
	public void clearQueue(String queue) throws TException {
		db.getCollection(queue).drop();
	}

	@Override
	public String putMessage(String queue, String body) throws TException {
		DBCollection collection = prepareCollection(queue);
		long currentTime = System.currentTimeMillis();

		DBObject item = new BasicDBObject();
		item.put("body", body);
		item.put("created_at", currentTime);
		item.put("scheduled_at", currentTime - START_BACK_TIME);

		collection.insert(item);

		return item.get("_id").toString();
	}

	@Override
	public Message getMessage(String queue) throws EmptyQueueException,
			TException {
		DBCollection collection = prepareCollection(queue);
		long currentTime = System.currentTimeMillis();

		DBObject query = new BasicDBObject();
		query.put("scheduled_at", new BasicDBObject("$lte", currentTime));

		DBObject sort = new BasicDBObject();
		sort.put("scheduled_at", 1);

		long scheduled_at = currentTime + reschedulingDelay;
		DBObject update = new BasicDBObject();
		update.put("$set", new BasicDBObject("scheduled_at", scheduled_at));

		DBObject item = collection.findAndModify( //
				query, null, sort, false, update, false, false);

		if (item == null) {
			throw new EmptyQueueException();
		}

		Message message = new Message();
		message.id = item.get("_id").toString();
		message.body = (String) item.get("body");

		return message;
	}

	@Override
	public void deleteMessage(String queue, String id) throws TException {
		DBCollection collection = db.getCollection(queue);

		DBObject item = new BasicDBObject();
		item.put("_id", new ObjectId(id));

		collection.remove(item);
	}
}
