"""
topicmodel.py
Wrapper for gensim topic modeling
"""
from gensim import corpora, models, similarities
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class TopicModel:
    def __init__(self, docs):
        """docs is a list of strings, 
        each is a document 
        """
        self.tokens = tokenize(docs)
        self.dictionary = make_id2word(self.tokens)
        self.corpus = make_corpus(self.dictionary, self.tokens)
     
    def lda(self, n):
        """ 
        lda topic model wrapper
        """
        # Train model on corpus
        lda = models.LdaModel(self.corpus, id2word=self.dictionary, num_topics=n) 
        lda.print_topics()
        # Transform the corpus using LDA model
        #corpus_lda = lda[self.corpus]
        return lda

    def hdp_lda(self):
        """
        hdp topic model wrapper
        """
        hdp = models.HdpModel(self.corpus, id2word=self.dictionary) 
        hdp.print_topics()
        return hdp
      
def tokenize(docs):
    """Tokenize the documents by splitting ea. string;
    also cast tokens in unicode, with error replace
    Returns: a list of lists of tokenized words
    """
    # Convert all strings to lowercase first
    docs = [doc.lower() for doc in docs]

    # Get rid of punctuations; match letters only
    tokenizer = RegexpTokenizer(r'[a-z]+')
    tokens = [[unicode(token, errors='replace') \
                for token in tokenizer.tokenize(doc)] \
                for doc in docs]
  
    return tokens    

def make_id2word(tokens):
    """
    Some preprocessing to make id2word dictionary
    """
    dictionary = corpora.Dictionary(tokens)
    return dictionary

def make_corpus(dictionary, tokens):
    """Make gensim corpus given id2word dictionary
        pre-process by removing words that appear
        but once.
    """
    # Remove stopwords and words that appear only once
    stoplist = stopwords.words('english')
    # Add some words to the stoplist
    stoplist += ['would', 'could', 'going', 'us', \
                'also', 'mr', 'u', 'shall', 'said', \
                'SUBJECT', 'DATE', \
                'declassified', 'line', 'lines', 'paragraph', \
                'text', 'source', 'less']
    stop_ids = [dictionary.token2id[stopword]
                    for stopword in stoplist
                    if stopword in dictionary.token2id]
    once_ids = [tokenid for tokenid, docfreq
                    in dictionary.dfs.iteritems()
                    if docfreq == 1]
    # Remove words one char long
    char_ids = [dictionary.token2id[word]
                    for word in dictionary.token2id
                    if len(word) == 1]

    dictionary.filter_tokens(stop_ids + once_ids + char_ids)
    dictionary.compactify()
    #dictionary.save('corpus.dict')
 
    corpus = [dictionary.doc2bow(text) for text in tokens]
    return corpus

