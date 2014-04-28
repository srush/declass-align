"""
topicmodel.py
Wrapper for gensim topic modeling
"""
from gensim import corpora, models, similarities
from nltk.corpus import stopwords
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class TopicModel:
    def __init__(self, docs):
        """docs is a list of strings, 
        each is a document 
        """
        self.tokens = tokenize(docs)
        self.dictionary = make_id2word(self.tokens)
        self.corpus = make_corpus(self.dictionary)
       
def tokenize(docs):
    """Tokenize the documents by splitting ea. string;
    also cast tokens in unicode, with error replace
    """
    tokens = map(lambda doc: \
            [unicode(token, errors='replace') \
                for token in doc.lower().split()], docs)
    return tokens    

def make_id2word(tokens):
    """
    Some preprocessing to make id2word dictionary
    """
    dictionary = corpora.Dictionary(tokens)
    return dictionary

def make_corpus(dictionary):
    """Make gensim corpus given id2word dictionary
        pre-process by removing words that appear
        but once.
    """
    # Remove stopwords and words that appear only once
    stoplist = stopwords.words('english')
    stop_ids = [dictionary.token2id[stopword]
                    for stopword in stoplist
                    if stopword in dictionary.token2id]
    once_ids = [tokenid for tokenid, docfreq
                    in dictionary.dfs.iteritems()
                    if docfreq == 1]
    dictionary.filter_tokens(stop_ids + once_ids)
    dictionary.compactify()
    #dictionary.save('corpus.dict')
 
    corpus = [dictionary.doc2bow(text) for text in tokens]
    return corpus

def lda(corpus, n):
    """ 
    lda topic model wrapper
    """
    # Train model on corpus
    lda = models.LdaModel(corpus, id2word=dictionary, num_topics=n) 
    # Transform the corpus using LDA model
    corpus_lda = lda[corpus]
    return lda, corpus_lda

def hdp_lda(corpus):
    """
    hdp topic model wrapper
    """
    
    



















