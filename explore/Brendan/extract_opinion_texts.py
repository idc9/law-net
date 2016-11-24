__author__ = 'brendan'

import os
import beesh
import functions
import time
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
start = time.time()

# %%%%%%%%% Script Inputs %%%%%%%%%%
courtname = 'scotus'
cases_to_check = 1000000000  # cap on how many cases to process
corpus_doc = r'C:\Users\brendan\PycharmProjects\law-net\explore\Brendan\bs_data\corpus.txt'
order_doc = r'C:\Users\brendan\PycharmProjects\law-net\explore\Brendan\bs_data\corpus_map.txt'
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# Delete old versions
os.remove(corpus_doc)
os.remove(order_doc)
# And create new versions
open(corpus_doc, 'w')
open(order_doc, 'w')

cwd = os.getcwd()
if '\explore\Brendan' in cwd:
    proj_dir = cwd[:-15]
data_dir = proj_dir + r'data/'

print '... loading edges...'
edgelist = beesh.csv_to_list(r'C:\Users\brendan\PycharmProjects\law-net\data\clean\%s' % courtname,
                                      'edgelist.csv', 1, 0)
edgeload_time = time.time()
print '... edges loaded. (%s sec)' % str(edgeload_time - start)[:8], '\n'

cases_checked = 0
corpus_size = 0
corpus_cases = []
cases_extracted = []
print '...building corpus...'

for row in edgelist:
    citing = int(row[1])
    cited = int(row[2])

    if citing not in cases_extracted:
        cases_extracted.append(citing)
        cases_checked += 1
        tokens = functions.extract_opinion_texts(filepath=data_dir + r'\raw\%s\opinions\%s.json' % (courtname, citing))

        if tokens != '':
            with open(corpus_doc, 'a') as file:
                file.write(tokens)
            with open(order_doc, 'a') as file:
                file.write(str(citing) + '\n')

    if cited not in cases_extracted:
        cases_extracted.append(cited)
        cases_checked += 1
        tokens = functions.extract_opinion_texts(filepath=data_dir + r'\raw\%s\opinions\%s.json' % (courtname, cited))

        if tokens != '':
            with open(corpus_doc, 'a') as file:
                file.write(tokens)
            with open(order_doc, 'a') as file:
                file.write(str(cited) + '\n')

    if cases_checked == cases_to_check:
        break
    if cases_checked % 1000 == 0:
        print '%s cases checked' % cases_checked

end = time.time()
elapsed = end - start
print 'script took %s seconds to run (%s minutes/%s hours)' % (str(elapsed)[:5],
                                                               str(elapsed/60.)[:5],
                                                               str(elapsed/60./60.)[:5])