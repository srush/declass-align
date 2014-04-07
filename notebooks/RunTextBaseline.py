"""
Run Text Baseline Algorithm on Annotated Set
"""
import pandas
import redact.baselines as baselines
import redact.experiments
import matplotlib.pyplot as plt
import cv2
import numpy as np
import redact.images as im
import redact.experiments as ex
from redact.progress import ProgressBar

from redact.data.human import * 
import redact.data.passwd as passwd
db = passwd.get_db()
cursor = passwd.get_cursor(db)
all = HumanPair.get_all(cursor)

# This one is slow so we add a progress bar.
p = ProgressBar(len(all))
documents = []
failed = []
for i, a in enumerate(all):
    p.animate(i)
    try:
        documents.append(baselines.make_docs(a))
    except Exception:
        print "fail", i
	failed.append(i)
        pass

# Collect the set of gold predictions.
gold_predictions = []
for predictions in baselines.make_gold_predictions(all):
    gold_predictions.append(predictions)

#ensure that same number of test + gold
for f in failed:
    del gold_predictions[f]

# Construct our text predictions.
text_aligner = baselines.TextAligner()
text_predictions = [text_aligner.align(p1, p2, i)
                    for i, (p1, p2) in enumerate(documents)]

fscore = ex.FScore(wrapper=baselines.PredictionText, name="TextMatch")
fscore.from_sets(gold_predictions, text_predictions)

#the Results
fscore = ex.FScore.make_pandas_table([fscore])
fscore.to_csv('../results/text_baseline_scores.csv', sep="\t")

#now let's dump the test and gold predictions to CSV
#the above code altered the objects in-place so we need to regenerate.
out_gold = open('../results/text_baseline_gold.csv', 'w')
out_gold.write("index\tside\ttext\tposition\trange\n")
for predictions in baselines.make_gold_predictions(all):
    for p in predictions:
	out_gold.write(str(p.index) + "\t" + \
			str(p.side) + "\t" + \
			p.text + "\t" + \
			str(p.position) + "\t" + \
			str(p.range) + "\n")
out_gold.close()


out_test = open('../results/text_baseline_test.csv', 'w')
out_test.write("index\tside\ttext\tposition\trange\n")
text_aligner = baselines.TextAligner()
for i, (p1, p2) in enumerate(documents):
	predictions = text_aligner.align(p1, p2, i)
	for p in predictions:
		out_test.write(str(p.index) + "\t" + \
				str(p.side) + "\t" + \
				p.text + "\t" + \
				str(p.position) + "\t" + \
				str(p.range) + "\n")

out_test.close()

