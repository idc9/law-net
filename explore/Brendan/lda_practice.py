__author__ = 'brendan'

import logging, gensim, bz2
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# load id->word mapping (the dictionary), one of the results of step 2 above
id2word = \
    gensim.corpora.Dictionary.load_from_text(r'C:\Users\brendan\PycharmProjects\law-net\explore\Brendan\bs_data\corpus2.txt')
print id2word[:5]
exit()
# load corpus iterator
mm = gensim.corpora.MmCorpus('wiki_en_tfidf.mm')
# mm = gensim.corpora.MmCorpus(bz2.BZ2File('wiki_en_tfidf.mm.bz2')) # use this if you compressed the TFIDF output

print(mm)