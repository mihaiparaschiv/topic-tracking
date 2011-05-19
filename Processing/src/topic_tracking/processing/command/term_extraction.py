from itertools import chain
from nltk.corpus import stopwords
from nltk.tree import Tree
from topic_tracking.processing.context import ProcessingContext
from topic_tracking.service.processing.ttypes import ProcessingException
from topic_tracking.util.command import Command
from topic_tracking.util.feature import make_feature_key, normalize_feature_name
import nltk


class TermExtractionCommand(Command):

    def __init__(self, lemmatizer, min_term_count):
        self._lemmatizer = lemmatizer
        self._min_term_count = min_term_count
        self._stopwords = stopwords.words('english')

    def execute(self, context):
        sentences = context[ProcessingContext.TAGGED_SENTENCES]
        trees = nltk.batch_ne_chunk(sentences, binary=False)

        terms = {}

        # chain the iterators of all trees in order to access their
        # children directly
        nodes = chain(*trees)

        for node in nodes:
            if isinstance(node, Tree):
                # self.__process_named_entity(terms, node)
                pass
            else:
                self.__process_term(terms, node)

        if len(terms) < self._min_term_count:
            raise ProcessingException('Insufficient terms')

        context[ProcessingContext.EXTRACTED_TERMS] = terms

    """
    def __process_named_entity(self, terms, node):
        tokens = tuple([token for (token, _) in node.leaves()])
        ne = ' '.join(tokens)
        ne_type = node.node

        ne = ne.lower()
        ne = ne.replace('.', '')
        key = make_feature_key((ne_type, ne))
        terms[key] = 1
    """

    def __process_term(self, terms, node):
        """Adds the term to the terms table."""

        term = node[0]
        pos = node[1]
        pos_key = pos[0].lower()

        # continue only if we have a noun or a verb
        if not pos_key in ('n', 'v'):
            return

        term = self._lemmatizer.lemmatize(term, pos_key)
        if term is None:
            return

        term = normalize_feature_name(term)
        if term in self._stopwords:
            return

        key = make_feature_key(term)

        if key not in terms:
            terms[key] = 0
        terms[key] += 1
