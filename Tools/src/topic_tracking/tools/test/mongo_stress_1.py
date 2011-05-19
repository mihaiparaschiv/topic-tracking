from pymongo import Connection
from time import clock


ITEM_COUNT = 100000
SAFE = False

connection = Connection()
collection = connection.stress_test.data

collection.remove()

t1 = clock()
for i in range(0, ITEM_COUNT):
    item = {}
    item["name"] = "item_" + str(i)
    collection.insert(item, safe=SAFE)
t2 = clock()
print('inserted %d in %f' % (collection.count(), (t2 - t1)))


t1 = clock()
for item in collection.find():
    item["new_name"] = "item_new_"
    collection.update({'_id': item['_id']}, item, safe=SAFE)
t2 = clock()
print('updated %d in %f' % (collection.count(), (t2 - t1)))
