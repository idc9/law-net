import os
import glob
import re
from bs4 import BeautifulSoup

import nltk
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords

from pipeline.download_data import json_to_dict


def get_text_from_json(json_file):
    """
    Grabs the text of an opinion file from the json file
    """
    # get html from json file
    # check each of these keys for the case text
    html = ''
    keys_to_try = ['html', 'plain_text', 'html_with_citations',
                   'html_lawbox', 'html_columbia']
    for key in keys_to_try:
        contents = json_file[key]

        # if the contents is not empty then extract the text and move on
        if (contents is not None) and len(contents) > 0:
            html = contents
            break

    # parse html with bs4
    parsed_html = BeautifulSoup(html, 'html.parser')

    # grab the text of the opinion
    return parsed_html.get_text()


def make_text_files(data_dir, court_name, CLid_good=None, CLid_bad=None):
    """
    Convertes the .json files to text files and
    does some initial pre-processing

    Parameters
    ---------

    data_dir: path to data directory

    court_name: which court to process

    CLid_good: ignore cases that are NOT in this list

    CLid_bad: ignore cases that ARE in this list

    stop_words: list of stop words to use (if any)

    Output
    ------
    saves a bunch of .txt files
    """

    input_path = data_dir + 'raw/' + court_name + '/opinions/'
    output_path = data_dir + 'vertex_metrics_experiment/textfiles/'

    if not os.path.exists(input_path):
        raise ValueError('input folder does not exist')

    # json case files in directory
    json_files = os.listdir(input_path)

    # CL ids of downloaded cases
    CLids = set([re.findall('\d+', f)[0] for f in json_files])

    # focues on good cases
    if CLid_good:
        CLids = CLids.intersection(set(CLid_good))

    # ignore bad cases
    if CLid_bad:
        CLids = CLids.difference(set(CLid_bad))

    # crate a text file for each case
    for case in CLids:

        # path to opinion file
        file_path = input_path + case + '.json'

        # grab the json
        json_file = json_to_dict(file_path)

        # get the text out of the json file
        text = get_text_from_json(json_file)

        filename = output_path + case + '.txt'
        with open(filename, "w") as text_file:
            # text_file.write(text)
            # unicode makes me want to cry sometimes
            text_file.write(text.encode("UTF-8"))


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


def get_normalized_text_dict(experiment_data_dir):
    """
    Normalizes each text file in the corpus and puts them into a dict

    Output
    ------
    dict with CL ids as keys and strings as values
    """

    # CL ids of all cases
    input_path = experiment_data_dir + 'textfiles/'
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
