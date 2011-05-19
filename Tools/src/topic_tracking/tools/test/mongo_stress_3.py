from pymongo import Connection
from time import clock


ITEM_COUNT = 10000
SAFE = False
DISPLAY_RATIO = 0.01

connection = Connection()
collection = connection.stress_test.dict_test
collection.remove()

t1 = clock()
for i in range(0, ITEM_COUNT):
    doc = {'$set': {'references.' + str(i): 1}}
    t11 = clock()
    collection.update({'_id': 'doc'}, doc, upsert=True, safe=SAFE)
    if i % int(ITEM_COUNT * DISPLAY_RATIO):
        t12 = clock()
        print('inserted item %d in %f' % (i, (t12 - t11)))
t2 = clock()
doc = collection.find_one({'_id':'doc'})
print('inserted %d in %f' % (len(doc['references']), (t2 - t1)))
