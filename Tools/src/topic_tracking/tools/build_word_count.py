from topic_tracking.util.lemmatization import Lemmatizer
from topic_tracking.util.word_count import WordCountProvider
import pickle
import string


def makefilter(keep):
    """ Return a functor that takes a string and returns a copy of that
        string consisting of only the characters in 'keep'.
    """

    # make a string of all chars, and one of all those NOT in 'keep'
    allchars = string.maketrans('', '')
    delchars = ''.join([c for c in allchars if c not in keep])

    # return the functor
    return lambda s, a = allchars, d = delchars: s.translate(a, d)


string_clean = makefilter(string.letters + string.digits + '-')


if __name__ == '__main__':
    input = 'res/top5000.csv'
    output = 'res/top5000.pickle'

    provider = WordCountProvider()
    lemmatizer = Lemmatizer()

    with open(input) as f:
        c = 0

        for line in f:
            cols = line.split(',')
            cols = [string_clean(col.lower()) for col in cols]
            (position, word, pos, count) = cols

            if pos in ('n', 'v'):
                lemma = lemmatizer.lemmatize(word, pos, False)
                if not word == lemma:
                    print('Different lemma: %s - %s: %s' % (word, pos, lemma))
                if lemma is not None:
                    word = lemma

            provider.set(word, pos, count)

            c += 1

        print('Found %d terms.' % c)

    with open(output, 'w') as f:
        pickle.dump(provider, f)
        print('Dumped the provider to: %s' % output)
