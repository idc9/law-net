import os
import glob
import re
from bs4 import BeautifulSoup

from pipeline.download_data import json_to_dict


def make_text_files(data_dir, court_name, network_name=None,
                    op_id_good=None, op_id_bad=None):
    """
    Convertes the .json files to text files and
    does some initial pre-processing

    Parameters
    ---------

    data_dir: path to data directory

    court_name: which court to process

    network_name: where to save the processes text files

    op_id_good: ignore cases that are NOT in this list

    op_id_bad: ignore cases that ARE in this list

    Output
    ------
    saves a bunch of .txt files
    """
    if not network_name:
        network_name = court_name

    input_path = data_dir + 'raw/' + court_name + '/opinions/'
    output_path = data_dir + network_name + '/textfiles/'

    if not os.path.exists(input_path):
        raise ValueError('input folder does not exist')

    # json case files in directory
    json_files = os.listdir(input_path)

    # CL ids of downloaded cases
    op_ids = set([re.findall('\d+', f)[0] for f in json_files])

    # focues on good cases
    if op_id_good is not None:
        op_ids = op_ids.intersection(set(op_id_good))

    # ignore bad cases
    if op_id_bad is not None:
        op_ids = op_ids.difference(set(op_id_bad))

    # crate a text file for each case
    for op_id in op_ids:

        # path to opinion file
        file_path = input_path + op_id + '.json'

        # grab the json
        json_file = json_to_dict(file_path)

        # get the text out of the json file
        text = get_text_from_json(json_file)

        filename = output_path + op_id + '.txt'
        with open(filename, "w") as text_file:
            # text_file.write(text)
            # unicode makes me want to cry sometimes
            text_file.write(text.encode("UTF-8"))


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
