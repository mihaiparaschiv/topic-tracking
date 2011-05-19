class StoryFinder(object):

    def __init__(self, es, index, query_builder):
        self._es = es
        self._index = index
        self._query_builder = query_builder

    def refresh(self):
        self._es.refresh(self._index)

    def find_stories_by_resource(self, resource, count):
        model_query = self._query_builder.build_model_query(resource)
        query = {
            'query': model_query,
            'size': count
        }
        return self._find_stories_by_model(query)

    def find_stories_by_story(self, story, count):
        model_query = self._query_builder.build_model_query(story)
        query = {
            'query': {
                'filtered': {
                    'query': model_query,
                    'filter': {
                        'not': {
                            'filter': {
                                'term': {'_id': story._id}
                            }
                        }
                    }
                }
            },
            'size': count
        }
        return self._find_stories_by_model(query)

    def _find_stories_by_model(self, query):
        result = self._es.search(query, self._index, 'story')
        return result['hits']['hits']
