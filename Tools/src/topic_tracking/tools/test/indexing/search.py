from pymongo import Connection
from time import clock
from collections import defaultdict


SELECTED_DOCUMENTS_COUNT = 10


def find_similar(document, reversed_index_collection):
    features = document['features']
    scores = defaultdict(int)
    
    print("Results for document %s with %d features" % (document['_id'], len(features)))
    t1 = clock()
    for feature in features:
        print('Computing for feature %s' % feature)
        fp = reversed_index_collection.find_one({'_id': feature})
        references = fp['references']
        for doc_id, value in references.items():
            scores[doc_id] += value
    score_list = sorted(scores.items(), key=lambda x: x[1])
    t2 = clock()
    
    print('tested %d documents in %f' % (len(scores), (t2 - t1)))
    print("Most similar documents are %s" % str(score_list[:5]))
    

# DATABASE

connection = Connection()
db = connection.indexing
index_collection = db.index
reversed_index_collection = db.reverse_index


# FIND SIMILAR DOCUMENTS

cursor = index_collection.find()
for i in range(SELECTED_DOCUMENTS_COUNT):
    document = cursor.next()
    find_similar(document, reversed_index_collection)


print("Done")