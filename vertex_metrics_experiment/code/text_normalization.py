import string
from nltk import word_tokenize


class StemTokenizer():
    def __init__(self, stemmer):
        self.stemmer = stemmer
        self.translate_table = dict((ord(char), None) for char in string.punctuation)

    def __call__(self, text):

        # remove puncuation
        text = text.translate(self.translate_table)

        # lower case words
        text = text.lower()

        # tokenize and stem
        return [self.stemmer.stem(w) for w in word_tokenize(text)]


class Tokenizer():
    def __init__(self):
        self.translate_table = dict((ord(char), None) for char in string.punctuation)

    def __call__(self, text):

        # remove puncuation
        text = text.translate(self.translate_table)

        # lower case words
        text = text.lower()

        # tokenize
        return word_tokenize(text)
