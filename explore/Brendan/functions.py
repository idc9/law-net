__author__ = 'brendan'

from bs4 import BeautifulSoup
import re
from nltk.corpus import stopwords
from code.pipeline import download_data
from nltk.stem.porter import PorterStemmer

p_stemmer = PorterStemmer()


def soup_to_tokens(soup):
    soup_text = soup.get_text()
    letters_only = re.sub("[^a-zA-Z]", " ", soup_text)
    lowercase = letters_only.lower()
    tokens = lowercase.split()
    tokens = [token for token in tokens if token not in stopwords.words("english")]
    tokens = [p_stemmer.stem(i) for i in tokens]
    tokens = [token for token in tokens if len(token) >= 3]
    tokens_as_string = ' '.join(tokens)
    return tokens_as_string


def extract_opinion_texts(filepath):

        try:
            file_data = download_data.json_to_dict(filepath)
            raw_text = file_data[u'html']
            souped_text = BeautifulSoup(raw_text)
            words = soup_to_tokens(souped_text) + '\n'

        except ValueError:
            words = ''

        return words


def words_to_tf(words):
    tf_dict = {}

    for word in words:
        if word in tf_dict.keys():
            tf_dict[word] += 1
        else:
            tf_dict[word] = 1

    return tf_dict