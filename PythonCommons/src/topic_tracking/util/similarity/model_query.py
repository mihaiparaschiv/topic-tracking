class ModelQueryBuilder(object):
    """This class facilitates the creation of ElasticSearch queries based on
    a single model's features.
    """

    def __init__(self, max_clauses, max_entity_clauses, entity_boost, term_boost):
        self._max_clauses = max_clauses
        self._max_entity_clauses = max_entity_clauses
        self._entity_boost = entity_boost
        self._term_boost = term_boost

    def build_model_query(self, model):
        """Creates a query based on the given model."""

        # build entity queries
        entity_queries = self._build_feature_queries(model.entities.iteritems(),
            'entities', 'payload', self._entity_boost, self._max_entity_clauses)

        # build term queries
        remaining_clauses = self._max_clauses - len(entity_queries)
        term_queries = self._build_feature_queries(model.terms.iteritems(),
            'terms', 'payload', self._term_boost, remaining_clauses)

        # build boolean query
        query = {
            'bool': {
                'should': entity_queries + term_queries
            }
        }
        return query

    def _build_feature_queries(self, features, feature_type, query_type, boost, max_clauses):
        """Creates a list of queries for a subset of the given features."""

        features = sorted(features, key=lambda x: x[1], reverse=True)[:max_clauses]
        queries = []
        for feature, score in features:
            q = {
                query_type: {
                    feature_type: {
                        'value': feature,
                        'boost': score * boost
                    }
                }
            }
            queries.append(q)
        return queries
