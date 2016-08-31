import pandas as pd
import numpy as np


def clean_scotus():
    pass


def get_clean_jurisdiction(jurisdiction_df, case_metadata):
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
    jurisdiction_df: pandas DataFrame of raw jurisdicitons file
    case_metadata: pandas DataFrame of clean case_metadata


    """
    # TODO: finish horozontal categories
    # TODO: finish vertical categories

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
    id_to_court = case_meatadata.court.to_dict()

    # count the number of cases in each juridiction
    for case in case_meatadata.index:
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
