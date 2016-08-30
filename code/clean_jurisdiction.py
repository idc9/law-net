import pandas as pd
import numpy as np


def clean_jurisdiction_csv(data_dir):
    """
    cleans the jursidictions.csv file

    # index by abbreviation
    # make column names lower case
    # get rid of weird formatting in juridiction
    # add horizontal jurisdictions
    # add vertical jursidictions
    """
    # TODO: finish horozontal categories
    # TODO: finish vertical categories

    jurisdiction_file = pd.read_csv(data_dir + 'raw/jurisdictions.csv')

    # reindex by abbrev
    jurisdiction_file.set_index('Abbrev', drop=True, inplace=True)
    jurisdiction_file.index.name = 'abbrev'

    # make col names lower case and remove spaces
    jurisdiction_file.columns = [c.encode('ascii', 'ignore')
                                 .lower().replace(' ', '_')
                                 for c in jurisdiction_file.columns]

    # get rid of weird character in Jurisdiction column
    for court in jurisdiction_file.index:
        j = jurisdiction_file.loc[court, 'jurisdiction']
        jurisdiction_file.loc[court, 'jurisdiction'] = j.replace('\xa0', ' ')

    states = get_states()

    # identify horizontal category
    jurisdiction_file['horizontal'] = np.nan
    for court in jurisdiction_file.index:
        jname = jurisdiction_file.loc[court, 'name']
        if 'Virginia' in jname:
            if 'West' in jname:
                jurisdiction_file.loc[court, 'horizontal'] = 'WV'
            else:
                jurisdiction_file.loc[court, 'horizontal'] = 'VA'
        else:
            states_found = [st for st in states.keys() if states[st] in jname]
            if len(states_found) == 1:
                jurisdiction_file.loc[court, 'horizontal'] = states_found[0]
            else:
                # TODO: finish this
                jurisdiction_file.loc[court, 'horizontal'] = 'other'

    # identify vertical category
    jurisdiction_file['vertical'] = np.nan
    for court in jurisdiction_file.index:
        juris = jurisdiction_file.loc[court, 'jurisdiction']

        if 'Appellate' in juris:
            jurisdiction_file.loc[court, 'vertical'] = 'appellate'

        elif 'Supreme' in juris:
            jurisdiction_file.loc[court, 'vertical'] = 'supreme'
        else:
            jurisdiction_file.loc[court, 'vertical'] = 'other'

    jurisdiction_file.to_csv(data_dir + 'clean/jurisdictions.csv')


def load_jurisdictions(data_dir):
    """
    load the juridictions
    """
    jurisdictions = pd.read_csv(data_dir + 'clean/jurisdictions.csv')

    # reindex by abbrev
    jurisdictions.set_index('abbrev', drop=True, inplace=True)
    jurisdictions.index.name = 'abbrev'

    return jurisdictions


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
