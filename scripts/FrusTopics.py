#training the lda model: 03:51:48 to 04:00:33
#40 topics
#94091 unique items in dict
#26933 docs


import topicmodel.topicmodel as topicmodel
import topicmodel.frus as frus

all_texts = frus.get_texts()
m = frus.topicmodel.Topicmodel(all_texts)
lda = m.lda(40)

for t in lda.show_topics(topics=40, topn=10):
    print t
    print

# Now we have all topics across all documents
# For each text, get most likely topic
lda_corpus = lda[m.corpus]  

from collections import defaultdict
topic_to_docs = defaultdict(list)


for doc_id, topics in enumerate(lda_corpus):
    # Return (topic, prob) with highest prob for this doc
    topic, prob = max(topics, key=lambda topic:topic[1])
    topic_to_docs[topic].append(doc_id)

doc_to_redacts = defaultdict()
#get num of redactions per doc
redactions = frus.get_redactions(all_texts)
for doc, redact_list in enumerate(redactions):
    doc_to_redacts[doc] = len(redact_list)

# Given topic, get number of redactions
topic_to_redacts = defaultdict()

for topic in topic_to_docs.keys():
    num_redact = sum([doc_to_redacts[doc] for doc in topic_to_docs[topic]])
    topic_to_redacts[topic] = num_redact

# sum(topic_to_redact.values()) = 4343. Yup, corresponds, i checked.
# What's the most heavily redacted topic?

toptopic = max(topic_to_redacts.iterkeys(), \
                key = lambda key: topic_to_redacts[key])
# 6

num_redactions = topic_to_redacts[toptopic]
# 535 redactions

lda.print_topic(toptopic, topn=10)

# '0.014*political + 0.011*military + 0.008*communist + 0.007*probably + 0.007*government + 0.006*support + 0.006*may + 0.005*power + 0.005*economic + 0.005*policy'
 


