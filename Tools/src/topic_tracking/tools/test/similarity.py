from scipy import sparse
from numpy import dot
import random
from time import clock


count = 1000000
fill = 0.01
a = sparse.lil_matrix((1, count))
for i in xrange(count):
    if random.random() < fill:
        a[0, i] = 1


# sparse

a = a.tocsc()

t1 = clock()
a_t = a.transpose()
t2 = clock()
print('sparse: transposition: %f' % (t2 - t1))

t1 = clock()
dot(a, a_t)
t2 = clock()
print('sparse: dot product: %f' % (t2 - t1))


# dense

a = a.todense()

t1 = clock()
a_t = a.transpose()
t2 = clock()
print('dense: transposition: %f' % (t2 - t1))

t1 = clock()
dot(a, a_t)
t2 = clock()
print('dense: dot product: %f' % (t2 - t1))


# sequence

sequence = []
for i in xrange(count):
    sequence.append(i)

t1 = clock()
result = 0
for i in sequence:
    result += i * sequence[i]
t2 = clock()
print('sequence: dot product: %f' % (t2 - t1))


# dictionary

dictionary = {}
for i in xrange(count):
    if a[0, i] > 0:
        dictionary[str(i)] = a[0, i]

t1 = clock()
result = 0
for k, v in dictionary.iteritems():
    result += v * dictionary[k]
t2 = clock()
print('dictionary: dot product: %f' % (t2 - t1))
