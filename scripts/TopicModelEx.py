import redact.baselines as baselines
import redact.experiments
import cv2
import numpy as np
import redact.images as im 

from redact.data.human import * 
import redact.data.passwd as passwd
db = passwd.get_db()
cursor = passwd.get_cursor(db)
all = HumanPair.get_all(cursor)

# Let's try to find the most common topics of the 
# predicted redacted text of 10 document pairs.

IMAGE_PATH = "/media/sophie/Sophie Drive/images/Img/"

# Fetch the 10 document pairs
documents = []
failed = []
for i, a in enumerate(all[:10]):
    try:
        documents.append(baselines.make_docs(a, IMAGE_PATH))
    except Exception:
        print "fail", i
        failed.append(i)
        pass

# Now make the predictions
text_aligner = baselines.TextAligner()
predictions = [text_aligner.align(p1, p2, i)
                    for i, (p1, p2) in enumerate(documents)]

predictions = [list(p) for p in predictions]
# Each predicted text is an item in this list
# INSTEAD: MAKE SUBLIST FOR EACH DOC PAIR?
# In the following we will treat each prediction as a separate 
# doc for the topic model.
predicted_text = [p.text for doc in predictions for p in doc]

# Convert strings to vectors
# Treat each prediction as a document.
from gensim import corpora, models, similarities
from nltk.corpus import stopwords

# from nltk.tokenize import RegexpTokenizer
# tokenizer = RegexpTokenizer(r'\w+')
# equivalent to one-liner below:
tokenized = tokenizer.batch_tokenize(predicted_text)
dictionary = corpora.Dictionary(tokenized)

# DICTERATOR: remove stop words and words that appear only once 
stoplist = stopwords.words('english')
stoplist.append('SUBJECT')
stoplist.append('DATE')
stop_ids = [dictionary.token2id[stopword] 
                for stopword in stoplist 
                if stopword in dictionary.token2id]
once_ids = [tokenid for tokenid, docfreq 
                in dictionary.dfs.iteritems() 
                if docfreq == 1]
dictionary.filter_tokens(stop_ids + once_ids)
dictionary.compactify()
dictionary.save('corpusDictionary.dict')

# Make the corpus
corpus = [dictionary.doc2bow(text) for text in tokenized]

# TFIDF model
# Initialize tfidf model
tfidf = models.TfidfModel(corpus) 
corpus_tfidf = tfidf[corpus]

# LSI
lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=10)
corpus_lsi = lsi[corpus_tfidf]

# Train the LDA model on the initial corpus
lda = models..LdaModel(corpus, id2word=dictionary, num_topics=5)
lda.print_topics()

# Use HDP-- why? Non-parametric baysesian method
# So we can avoid chicken-egg problem of det. num topics
#hdp = models.hdpmodel.HdpModel(corpus, id2word=dictionary)
#corpus_hdp = hdp[corpus]
#HDP Not working?






