__author__ = 'brendan'

import pyLDAvis.gensim
import pyLDAvis
from classes import dictionary, corpus_memory_friendly, lda

LDAvis = pyLDAvis.gensim.prepare(topic_model=lda, corpus=corpus_memory_friendly, dictionary=dictionary)
pyLDAvis.save_html(LDAvis, r'C:\Users\brendan\PycharmProjects\law-net\explore\Brendan\bs_data\ldavis.html')
pyLDAvis.display(LDAvis)