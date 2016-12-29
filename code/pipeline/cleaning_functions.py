import pandas as pd
import numpy as np
import networkx as nx
import os

# from load_data import get_network
from download_data import json_to_dict, download_bulk_resource


def get_network(case_metadata, edgelist):
    G = nx.DiGraph()
    G.add_nodes_from(case_metadata.index.tolist())
    for index, edge in edgelist.iterrows():
        ing = edge['citing']
        ed = edge['cited']

        G.add_edge(ing, ed)
    return G


def get_cert_cases_scotus(data_dir, remove=False):
    """
    Finds the certiorari cases from SCOTUS

    Output
    ------
    python list of certiorari cases
    """
    court_name = 'scotus'
    op_dir = data_dir + 'raw/' + court_name + '/opinions/'
    if not os.path.exists(op_dir):
        download_bulk_resource(court_name, 'opinions', data_dir)

    # grab all scotus cases
    case_metadata = pd.read_csv(data_dir + 'raw/case_metadata_master_r.csv',
                                index_col='id')

    case_metadata = case_metadata[case_metadata.court == 'scotus']
    case_metadata['date'] = pd.to_datetime(case_metadata['date'])

    case_ids = set(case_metadata.index)

    # grab scotus-scotus edges
    edgelist = pd.read_csv(data_dir + 'raw/edgelist_master_r.csv')
    edgelist = edgelist[edgelist.citing.isin(case_ids) & edgelist.cited.isin(case_ids)]

    # build the scotus network
    G = get_network(case_metadata, edgelist)
    degrees = G.degree()

    # cases in case_metadata missing opinion files
    missing_opinion = []

    # find zero degree cases that contain the words: 'denied' or 'certiorari'
    case_metadata['cert_case'] = False
    for case, _ in case_metadata.iterrows():
        op_path = op_dir + str(case) + '.json'
        if os.path.isfile(op_path):
            if degrees[case] == 0:

                opinion = json_to_dict(op_path)
                for key in opinion.keys():
                    value = opinion[key]
                    if type(value) is unicode:
                        if 'denied' in value or 'certiorari' in value:
                            case_metadata.loc[case, 'cert_case'] = True
        else:
            missing_opinion.append(case)

    if remove:
        # remove opinion files
        for file_name in os.lisdir(op_dir):
            os.remove(file_name)

        os.rmdir(op_dir)

    print 'there were %d cases missing opinions' % len(missing_opinion)
    print missing_opinion

    return case_metadata[case_metadata['cert_case']].index.tolist()


def find_time_travelers(data_dir):
    """
    Some edges cite forwards in time...
    """
    case_metadata = pd.read_csv(data_dir + 'raw/case_metadata_master_r.csv',
                                 index_col='id')

    edgelist = pd.read_csv(data_dir + 'raw/edgelist_master_r.csv')
    # some edges travel forwards in time
    edgelist['timetravel'] = False
    for index, edge in edgelist.iterrows():
        ing_date = case_metadata.loc[edge['citing'], 'date']
        ed_date = case_metadata.loc[edge['cited'], 'date']

        if ing_date < ed_date:
            edgelist.loc[index, 'timetravel'] = True

    return edgelist[edgelist['timetravel']].drop(['timetravel'], axis=1)


def get_clean_jurisdiction(data_dir):
    """
    Cleans the jursidictions file.
    Clean the case_metadata file first!

    # index by abbreviation
    # make column names lower case
    # get rid of weird formatting in juridiction
    # add horizontal jurisdictions
    # add vertical jursidictions

    Parameters
    ----------

    Output
    ------
    returns the clean jurisdictions data frame
    """
    # TODO: finish horozontal categories
    # TODO: finish vertical categories

    jurisdiction_df = pd.read_csv(data_dir + 'raw/jurisdictions.csv')
    case_metadata = pd.read_csv(data_dir + 'clean/case_metadata_master.csv')

    # reindex by abbrev
    jurisdiction_df.set_index('Abbrev', drop=True, inplace=True)
    jurisdiction_df.index.name = 'court'

    # make col names lower case and remove spaces
    jurisdiction_df.columns = [c.encode('ascii', 'ignore')
                               .lower().replace(' ', '_')
                               for c in jurisdiction_df.columns]

    # get rid of weird character in Jurisdiction column
    for court in jurisdiction_df.index:
        j = jurisdiction_df.loc[court, 'jurisdiction']
        jurisdiction_df.loc[court, 'jurisdiction'] = j.replace('\xa0', ' ')

    states = get_states()

    # identify horizontal category
    jurisdiction_df['horizontal'] = np.nan
    for court in jurisdiction_df.index:
        jname = jurisdiction_df.loc[court, 'name']
        if 'Virginia' in jname:
            if 'West' in jname:
                jurisdiction_df.loc[court, 'horizontal'] = 'WV'
            else:
                jurisdiction_df.loc[court, 'horizontal'] = 'VA'
        else:
            states_found = [st for st in states.keys() if states[st] in jname]
            if len(states_found) == 1:
                jurisdiction_df.loc[court, 'horizontal'] = states_found[0]
            else:
                # TODO: finish this
                jurisdiction_df.loc[court, 'horizontal'] = 'other'

    # identify vertical category
    jurisdiction_df['vertical'] = np.nan
    for court in jurisdiction_df.index:
        juris = jurisdiction_df.loc[court, 'jurisdiction']

        if 'Appellate' in juris:
            jurisdiction_df.loc[court, 'vertical'] = 'appellate'

        elif 'Supreme' in juris:
            jurisdiction_df.loc[court, 'vertical'] = 'supreme'
        else:
            jurisdiction_df.loc[court, 'vertical'] = 'other'

    # update counts
    num_cases = {}
    id_to_court = case_metadata.court.to_dict()

    # count the number of cases in each juridiction
    for case in case_metadata.index:
        court = id_to_court[case]

        if court in num_cases.keys():
            num_cases[court] += 1
        else:
            num_cases[court] = 1

    # update the counts
    for court in jurisdiction_df.index:
        if court in num_cases.keys():
            jurisdiction_df.loc[court, 'count'] = num_cases[court]
        else:
            jurisdiction_df.loc[court, 'count'] = 0

    return jurisdiction_df


def get_states():
    return {'AK': 'Alaska',
            'AL': 'Alabama',
            'AR': 'Arkansas',
            'AS': 'American Samoa',
            'AZ': 'Arizona',
            'CA': 'California',
            'CO': 'Colorado',
            'CT': 'Connecticut',
            'DC': 'District of Columbia',
            'DE': 'Delaware',
            'FL': 'Florida',
            'GA': 'Georgia',
            'GU': 'Guam',
            'HI': 'Hawaii',
            'IA': 'Iowa',
            'ID': 'Idaho',
            'IL': 'Illinois',
            'IN': 'Indiana',
            'KS': 'Kansas',
            'KY': 'Kentucky',
            'LA': 'Louisiana',
            'MA': 'Massachusetts',
            'MD': 'Maryland',
            'ME': 'Maine',
            'MI': 'Michigan',
            'MN': 'Minnesota',
            'MO': 'Missouri',
            'MP': 'Northern Mariana Islands',
            'MS': 'Mississippi',
            'MT': 'Montana',
            'NA': 'National',
            'NC': 'North Carolina',
            'ND': 'North Dakota',
            'NE': 'Nebraska',
            'NH': 'New Hampshire',
            'NJ': 'New Jersey',
            'NM': 'New Mexico',
            'NV': 'Nevada',
            'NY': 'New York',
            'OH': 'Ohio',
            'OK': 'Oklahoma',
            'OR': 'Oregon',
            'PA': 'Pennsylvania',
            'PR': 'Puerto Rico',
            'RI': 'Rhode Island',
            'SC': 'South Carolina',
            'SD': 'South Dakota',
            'TN': 'Tennessee',
            'TX': 'Texas',
            'UT': 'Utah',
            'VA': 'Virginia',
            'VI': 'Virgin Islands',
            'VT': 'Vermont',
            'WA': 'Washington',
            'WI': 'Wisconsin',
            'WV': 'West Virginia',
            'WY': 'Wyoming'}
