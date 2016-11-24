# __author__ = 'brendan'
#
# import os
# import operator
# import beesh
# from code.pipeline import download_data
# from bs4 import BeautifulSoup
# import re
# from nltk.corpus import stopwords
# from math import log
# import time
#
# cwd = os.getcwd()
# if '\explore\Brendan' in cwd:
#     proj_dir = cwd[:-15]
# data_dir = proj_dir + r'data/'
#
# PRINT = True
# courtname = 'scotus'
# cases_to_check = 5  # cap on how many cases to process
# N = 10  # used for "top N" words
# cases_of_interest = []
# start = time.time()
#
# print '... loading edges...'
# edgelist = beesh.csv_to_list(r'C:\Users\brendan\PycharmProjects\law-net\data\clean\%s' % courtname,
#                                       'edgelist.csv', 1, 0)
# edgeload_time = time.time()
# print '... edges loaded. (%s sec)' % str(edgeload_time - start)[:8], '\n'
#
# print '...accumulating cases of interest...'
# for row in edgelist:
#     citing = int(row[1])
#     cited = int(row[2])
#     if citing not in cases_of_interest:
#         cases_of_interest.append(citing)
#     if cited not in cases_of_interest:
#         cases_of_interest.append(cited)
# coi_time = time.time()
# print '...cases of interest accumulated. (%s sec)' % str(coi_time - edgeload_time)[:8], '\n'
# del edgelist
#
# print '...building corpus...'
# tf_matrix_dict = {}
# df_vector = {}
# words_found = []
# cases_checked = 0
# corpus_size = 0
# corpus_cases = []
# for case_no in cases_of_interest:
#     cases_checked += 1
#
#     try:
#
#         filename = '%s.json' % case_no
#         file_path = data_dir + r'\raw\%s\opinions\%s' % (courtname, filename)
#
#         file_data = download_data.json_to_dict(file_path)
#         raw_text = file_data[u'html']
#         souped_text = BeautifulSoup(raw_text)
#         text = souped_text.get_text()
#
#         letters_only = re.sub("[^a-zA-Z]",
#                               " ",
#                               text)
#         lowercase_letters_only = letters_only.lower()
#         words = lowercase_letters_only.split()
#         words = [w for w in words if w not in stopwords.words("english")]
#
#         if len(words) > 0:
#             tf_matrix_dict[case_no] = {}
#
#             for word in words:
#                 # If a new word in the Corpus
#                 if word not in words_found:
#                     words_found.append(word)
#
#                 # If a new word in the document
#                 if word not in tf_matrix_dict[case_no].keys():
#                     tf_matrix_dict[case_no][word] = 1
#                     try:
#                         df_vector[word] += 1
#                     except KeyError:
#                         df_vector[word] = 1
#                 else:
#                     tf_matrix_dict[case_no][word] += 1
#
#             corpus_size += 1
#             corpus_cases.append(case_no)
#
#     except ValueError:
#         pass
#
#     if cases_checked % 1000 == 0:
#         print '... %s cases checked ... ' % cases_checked
#
#     if cases_checked == cases_to_check:
#         break
# del cases_of_interest
# corpus_time = time.time()
# print '...corpus built. (%s sec)' % str(corpus_time - coi_time)[:8], '\n'
# #
# # print '... building df vector...'
# # # Turn DF vector from count to frequency
# # for word in df_vector.keys():
# #     df_vector[word] = float(df_vector[word])/float(corpus_size)
# # df_time = time.time()
# # print '...df vector built. (%s sec)' % str(df_time - corpus_time)[:8], '\n'
# #
# # print '... building importance metric ...'
# # # Create importance metric
# # importance_matrix = {}
# # for case_no in corpus_cases:
# #     importance_matrix[case_no] = {}
# #     for word in words_found:
# #         try:
# #             tf = tf_matrix_dict[case_no][word]
# #             idf = 1./df_vector[word]
# #             importance = tf_matrix_dict[case_no][word]*log(idf)
# #             importance_matrix[case_no][word] = importance
# #         except KeyError:
# #             importance_matrix[case_no][word] = 0
# # imp_time = time.time()
# # print '... importance metric built. (%s sec)' % str(imp_time - df_time)[:8], '\n'
# #
# # print '... calculating top %s words...' % N
# # topN_matrix = {}
# # for case_no in corpus_cases:
# #     topN_matrix[case_no] = {i: '' for i in range(N)}
# #     sorted_importance = sorted(importance_matrix[case_no].items(), key=operator.itemgetter(1), reverse=True)
# #     for i in range(N):
# #         try:
# #             topN_matrix[case_no][i] = sorted_importance[i][0]
# #         except IndexError:
# #             pass
# top_time = time.time()
#
# if PRINT:
#     print '...printing to csvs...'
#     for matrix_to_print, name_of_matrix in [[tf_matrix_dict, 'tf_matrix']]: #,
#                                             # [importance_matrix, 'importance_matrix']]:
#
#         header = ['Case No.'] + words_found
#         matrix = [header]
#         for case_no in corpus_cases:
#             new_row = [case_no]
#             for word in words_found:
#                 try:
#                     new_row.append(matrix_to_print[case_no][word])
#                 except KeyError:
#                     new_row.append(0)
#             matrix.append(new_row)
#         beesh.list_to_csv(r'C:\Users\brendan\PycharmProjects\law-net\explore\Brendan\%s.csv' % name_of_matrix,
#                           matrix)
#
#     # topN_table = [['Case No.'] + range(N)]
#     # for case_no in corpus_cases:
#     #     new_row = [case_no] + [topN_matrix[case_no][i] for i in range(N)]
#     #     topN_table.append(new_row)
#     # beesh.list_to_csv(r'C:\Users\brendan\PycharmProjects\law-net\explore\Brendan\TopWords.csv',
#     #                   topN_table)
#     #
#     print_time = time.time()
#
#     print '... CSVs printed. (%s sec)' % str(print_time - top_time)[:8], '\n'
#
# print 'Total runtime: %s sec' % str(print_time - start)[:8]

import extract_opinion_texts
import classes