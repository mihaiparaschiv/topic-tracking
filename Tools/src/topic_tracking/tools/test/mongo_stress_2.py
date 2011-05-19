from pymongo import Connection
from time import clock


COLLECTION_COUNT = 100000

connection = Connection()

t1 = clock()
for i in range(0, COLLECTION_COUNT):
    name = "c_" + str(i)
    collection = connection.stress_test[name]
    id = collection.insert({"data":1})
    count = collection.count()
    collection.remove({"_id":id})
    count2 = collection.count()
    if not count == 1 or not count2 == 0:
        print("%s: %d, %d", (name, count, count2))
        break
t2 = clock()
print('ran in %f' % (t2 - t1))
