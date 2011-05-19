class IndexHelper(object):

    def __init__(self, es):
        self._es = es

    def refresh_index(self, index):
        self._es.refresh(index)

    def clear_index(self, index):
        type_mappings = self._es.get_mapping(indexes=index)[index]
        self._es.delete_index(index)
        self._es.create_index(index)
        for type, mapping in type_mappings.iteritems():
            self._es.put_mapping(type, mapping, index)

    def _build_common_fields(self, model):
        es_doc = {}
        es_doc['title'] = model.title
        es_doc['entities'] = self._build_payload_string(model.entities)
        es_doc['terms'] = self._build_payload_string(model.terms)
        return es_doc

    def _build_payload_string(self, features):
        payload_sum = reduce(lambda x, y: x + y ** 2.0, features.values(), 0)
        payload_sum = payload_sum ** 0.5

        payloads = []
        for k, v in features.iteritems():
            payloads.append((k, v / payload_sum))

        payloads = (f[0] + '|' + str(f[1]) for f in payloads)
        return ' '.join(payloads)


    # resources --------------------------------------------------------------#

    def index_resource(self, resource, index):
        es_doc = self._build_common_fields(resource)
        es_doc['content'] = resource.content
        self._es.index(es_doc, index, 'resource', resource._id)

    def delete_resource(self, resource, index):
        self._es.delete(index, 'resource', resource._id)


    # stories ----------------------------------------------------------------#

    def index_story(self, story, index):
        es_doc = self._build_common_fields(story)
        es_doc['created'] = story.created
        es_doc['updated'] = story.updated
        es_doc['score'] = story.score
        self._es.index(es_doc, index, 'story', story._id)

    def delete_story(self, story, index):
        self._es.delete(index, 'story', story._id)
