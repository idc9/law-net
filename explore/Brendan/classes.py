__author__ = 'brendan'

import gensim
import logging
import os
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

topic_info_doc = r'C:\Users\brendan\PycharmProjects\law-net\explore\Brendan\bs_data\topic_info.txt'
doc_info_doc = r'C:\Users\brendan\PycharmProjects\law-net\explore\Brendan\bs_data\doc_info.txt'

# Create dictionary from consolidated text file
dictionary = gensim.corpora.Dictionary(line.lower().split() for line in
                                open(r'C:\Users\brendan\PycharmProjects\law-net\explore\Brendan\bs_data\corpus.txt'))

# Create corpus, the set of documents, from consolidated text file where each new line represents a new document
class MyCorpus(object):

    def __iter__(self):
        for line in open(r'C:\Users\brendan\PycharmProjects\law-net\explore\Brendan\bs_data\corpus.txt'):
            # assume there's one document per line, tokens separated by whitespace
            yield dictionary.doc2bow(line.lower().split())

    def __len__(self):
        len = 0
        for line in open(r'C:\Users\brendan\PycharmProjects\law-net\explore\Brendan\bs_data\corpus.txt'):
            len += 1
        return len

print 'corpus being constructed...'
corpus_memory_friendly = MyCorpus()
print '...corpus constructed.'

print 'performing lda...'
n = 20
lda = gensim.models.LdaModel(corpus=corpus_memory_friendly,
                             id2word=dictionary,
                             num_topics=n,
                             update_every=1,
                             chunksize=20000,
                             passes=1)

#####################
# Saving & printing
#####################
# os.remove(topic_info_doc) if os.path.exists(topic_info_doc) else 0  # Delete old version
# logfile = open(topic_info_doc, 'w')
# topic_dists = {}
# for i in range(n):
#     print>>logfile, lda.show_topic(i, 20)
#
#     # Used to grab topic info
#     # topic_dists[i] = lda.show_topic(i, 20)
#
# # Recall order cases were loaded into corpus
# doc_order = []
# for line in open(r'C:\Users\brendan\PycharmProjects\law-net\explore\Brendan\bs_data\corpus_map.txt'):
#     doc_order.append(int(line))
#
# doc_dists = {}
# os.remove(doc_info_doc) if os.path.exists(doc_info_doc) else 0  # Delete old version
# logfile = open(doc_info_doc, 'w')
# i = 0
# for vector in corpus_memory_friendly:
#     # print>>logfile, lda.get_document_topics(vector)
#
#     case_no = doc_order[i]
#     doc_dist = lda.get_document_topics(vector)
#     print>>logfile, '%s : %s' % (case_no, str(lda.get_document_topics(vector)))
#
#     # Used to grab doc info
#     # case_no = doc_order[i]
#     # doc_dists[case_no] = lda.get_document_topics(vector)
#
#     i += 1