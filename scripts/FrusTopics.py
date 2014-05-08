#training the lda model: 03:51:48 to 04:00:33
#40 topics
#94091 unique items in dict
#26933 docs


import topicmodel.topicmodel as topicmodel
import topicmodel.frus as frus

all_texts = frus.get_texts()
m = topicmodel.TopicModel(all_texts)
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

# sum(topic_to_redacts.values()) = 4343. Yup, corresponds, i checked.
# What's the most heavily redacted topic?

toptopic = max(topic_to_redacts.iterkeys(), \
                key = lambda key: topic_to_redacts[key])
# 6

num_redactions = topic_to_redacts[toptopic]
# 535 redactions

lda.print_topic(toptopic, topn=10)

# '0.014*political + 0.011*military + 0.008*communist + 0.007*probably + 0.007*government + 0.006*support + 0.006*may + 0.005*power + 0.005*economic + 0.005*policy'
 
import heapq
top10 = heapq.nlargest(10, topic_to_redacts.iterkeys(), key=lambda key:topic_to_redacts[key])

#[36, 27, 35, 3, 16, 32, 12, 9, 13, 2]


"""
0.012*political + 0.010*government + 0.007*party + 0.006*communist + 0.005*power + 0.005*regime + 0.005*may + 0.004*leaders + 0.004*support + 0.004*leadership
0.015*memorandum + 0.015*security + 0.014*national + 0.014*assistant + 0.012*affairs + 0.012*secretary + 0.011*state + 0.009*president + 0.007*special + 0.007*policy
0.014*military + 0.012*joint + 0.011*operations + 0.010*staff + 0.010*forces + 0.010*defense + 0.010*chiefs + 0.009*support + 0.008*intelligence + 0.007*states
0.021*million + 0.010*program + 0.010*year + 0.007*payments + 0.006*balance + 0.005*defense + 0.005*budget + 0.004*billion + 0.004*development + 0.004*system
0.007*vietnam + 0.007*saigon + 0.007*intelligence + 0.006*national + 0.006*one + 0.006*thieu + 0.005*president + 0.005*information + 0.004*agency + 0.004*press
0.030*secretary + 0.017*ambassador + 0.009*conversation + 0.008*state + 0.008*memorandum + 0.008*washington + 0.007*government + 0.007*president + 0.005*united + 0.005*might
0.017*military + 0.016*forces + 0.012*air + 0.011*north + 0.010*enemy + 0.009*force + 0.007*president + 0.006*south + 0.006*vietnam + 0.005*korea
0.015*economic + 0.010*countries + 0.010*aid + 0.009*states + 0.008*policy + 0.008*assistance + 0.007*development + 0.007*relations + 0.007*united + 0.006*world
0.028*soviet + 0.015*communist + 0.013*china + 0.012*military + 0.012*chinese + 0.011*soviets + 0.011*probably + 0.007*policy + 0.007*political + 0.006*believe
0.053*congo + 0.018*congolese + 0.015*belgian + 0.014*brazil + 0.009*belgium + 0.008*belgians + 0.007*katanga + 0.006*leopoldville + 0.006*brussels + 0.006*brazilian



