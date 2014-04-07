
# In[87]:

import redact.baselines as baselines
import redact.experiments
import matplotlib.pyplot as plt
import cv2
import numpy as np
import redact.images as im
import redact.experiments as ex
from redact.progress import ProgressBar


# Out[87]:

#     
# 

# In[89]:

reload(redact.progress)


# Out[89]:

#     <module 'redact.progress' from '/home/srush/Projects/declass-align/redact/progress.pyc'>

# In[55]:

reload(baselines)


# Out[55]:

#     <module 'redact.baselines' from '/home/srush/Projects/declass-align/redact/baselines.pyc'>

# In[2]:

from redact.data.human import * 
import redact.data.passwd as passwd
db = passwd.get_db()
cursor = passwd.get_cursor(db)
all = HumanPair.get_all(cursor)


# This one is slow so we add a progress bar.

# In[*]:

p = ProgressBar(len(all))
documents = []
for i, a in enumerate(all):
    p.animate(i)
    try:
        documents.append(baselines.make_docs(a))
    except Exception:
        print "fail", i
        pass


# Out[*]:

#      [                       0%                       ]

# Collect the set of gold predictions.

# In[42]:

gold_predictions = []
for predictions in baselines.make_gold_predictions(all):
    gold_predictions.append(predictions)


# Construct our text predictions.

# In[63]:

text_aligner = baselines.TextAligner()
text_predictions = [text_aligner.align(p1, p2, i)
                    for i, (p1, p2) in enumerate(documents)]


# In[ ]:

fscore = ex.FScore(wrapper=baselines.PredictionText, name="TextMatch")
fscore.from_sets(gold_predictions, text_predictions)


# In[ ]:

ex.FScore.make_pandas_table([fscore])

