from pipeline.download_data import url_to_dict


def case_info(op_id):
    """
    Given the case id returns a link to the opinion file on court listener
    """

    # API url
    url = 'https://www.courtlistener.com/api/rest/v3/opinions/%s/?format=json'\
          % op_id

    # get the absolute url from the API
    api_data = url_to_dict(url)
    courtlistener_url = 'https://www.courtlistener.com'
    opinion_url = courtlistener_url + api_data['absolute_url']

    print api_data['case_name']
    print api_data['date_filed']
    print
    print opinion_url
