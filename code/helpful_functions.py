from pipeline.download_data import url_to_dict


def case_info(op_id):
    """
    Given the case id returns a link to the opinion file on court listener
    """
    # API url
    op_api = 'https://www.courtlistener.com/api/rest/v3/opinions/%s/?format=json'\
              % op_id

    # get data from opinion and cluster api
    op_data = url_to_dict(op_api)
    cl_data = url_to_dict(op_data['cluster'])

    # url to opinion text
    opinion_url = 'https://www.courtlistener.com' + op_data['absolute_url']

    print cl_data['case_name']
    print 'date_filed: %s' % cl_data['date_filed']
    print opinion_url
