import random
from time import clock
from topic_tracking.util.tree import HierarchicalDict


key_count = 100000
keys_tuples = []
keys_strings = []

for _ in range(key_count):
    key = (str(random.randint(0, 10)), str(random.randint(0, 10)), str(random.random()))
    keys_tuples.append(key)
    keys_strings.append('_'.join(key))

tree = HierarchicalDict()
map_strings = {}
map_tuples = {}


# insert

t1 = clock()
for key in keys_tuples:
    tree.set(key, 1)
t2 = clock()
print('tree insert: %f' % (t2 - t1))

t1 = clock()
for key in keys_strings:
    map_strings[key] = 1
t2 = clock()
print('string map insert: %f' % (t2 - t1))

t1 = clock()
for key in keys_tuples:
    map_tuples[key] = 1
t2 = clock()
print('tuple map insert: %f' % (t2 - t1))


# read

t1 = clock()
for i in tree:
    pass
t2 = clock()
print('tree read: %f' % (t2 - t1))

t1 = clock()
for i in map_strings.iteritems():
    pass
t2 = clock()
print('string map read: %f' % (t2 - t1))

t1 = clock()
for i in map_tuples.iteritems():
    pass
t2 = clock()
print('tuple map read: %f' % (t2 - t1))
