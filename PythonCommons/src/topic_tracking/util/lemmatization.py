from nltk.corpus import wordnet as wn


class Lemmatizer(object):

    def lemmatize(self, word, pos, word_if_not_found=False):
        lemma = wn.morphy(word, pos)
        if lemma is None:
            if word_if_not_found:
                lemma = word
                lemma = unicode(lemma)

        return lemma
