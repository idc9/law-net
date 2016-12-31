import re
import glob

from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords


def text_normalization(text, stop_words=None, stemmer=None):
    """
    Normalizes a text file
    - remove non-letters
    - lower case words
    - stem words
    - remove stop words

    Parameters
    ----------
    text: string to normalize

    stop_words: list of stop words to kill (optional)

    stemmer: a stemmer fuction from NLTK

    Output
    ------
    the normalized string
    """
    # lowers = text.lower()
    # return lowers.translate(None, string.punctuation)

    # Remove non-letters
    letters_only = re.sub("[^a-zA-Z]", " ", text)

    # Convert to lower case, split into individual words
    words = letters_only.lower().split()

    # stem words
    if stemmer:
        words = [stemmer.stem(w) for w in words]

        # stem the stop words
        if stop_words:
            stop_words = [stemmer.stem(w) for w in stop_words]

    # remove stop words
    if stop_words:
        stop_words = set(stop_words)  # set is faster
        words = [w for w in words if w not in stop_words]

    # join the words back into one string separated by space
    return " ".join(words)


def get_normalized_text_dict(input_path):
    """
    Normalizes each text file in the corpus and puts them into a dict

    Note this function loads all text files into memory at once

    Output
    ------
    dict with CL ids as keys and strings as values
    """

    # CL ids of all cases
    text_files = glob.glob(input_path + "*.txt")
    CLids = set([re.findall('\d+', f)[0] for f in text_files])

    # which stemmer to use
    stemmer = PorterStemmer()

    # stop words
    stop_words = stopwords.words("english")

    normalized_text_dict = {}
    for clid in CLids:

        # open text file
        file_path = input_path + clid + '.txt'
        textfile = open(file_path, 'r')
        text = textfile.read()

        # intitial text normalization and save in dict
        normalized_text_dict[clid] = text_normalization(text)

    return normalized_text_dict
