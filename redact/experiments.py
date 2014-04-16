
import pandas as pd

class FScore:
    """
    Compute F1-Score based on gold set and test set.
    """

    def __init__(self, wrapper=lambda a:a, name=""):
        self.gold = 0
        self.test = 0
        self.correct = 0
        self.name = name
        self.wrapper = wrapper

    def increment(self, gold, test):
        """
        Add examples from sets.
        
        Parameters
        ----------
        gold : Set 
            Container of gold items.

        test : Set 
            Container of test items.
            
        """
        gold_set = map(self.wrapper, gold)
        test_set = map(self.wrapper, test)
        self.gold += len(gold_set)
        self.test += len(test_set)
        self.correct += len([1 for g in gold_set 
                             if any([t == g or g == t for t in test_set])])

    @property
    def fscore(self): 
        pr = self.precision + self.recall
        if pr == 0: return 0.0
        return (2 * self.precision * self.recall) / float(pr)

    @property
    def precision(self): 
        if self.test == 0: return 0.0
        return self.correct / float(self.test)

    @property
    def recall(self): 
        if self.gold == 0: return 0.0
        return self.correct / float(self.gold)    

    def add_to_dict(self, d):
        d["F-Score"].append(self.fscore)
        d["Recall"].append(self.recall)
        d["Precision"].append(self.precision)


    def from_sets(self, gold_sets, test_sets):
        assert (len(gold_sets) == len(test_sets))
        for gold, test in zip(gold_sets, test_sets):
            self.increment(gold, test)
        return self

    @staticmethod
    def make_pandas_table(fscores):
        d = {"F-Score":[], "Recall": [], "Precision":[]}
        names = []
        for fscore in fscores:
            fscore.add_to_dict(d)
            names.append(fscore.name)
        return pd.DataFrame(d, index=names)

    @staticmethod
    def output_header():
        "Output a scoring header."
        print "%10s  %10s  %10s  %10s   %10s"%(
            "Type", "Total", "Precision", "Recall", "F1-Score")
        print "==============================================================="

    def output_row(self, name):
        "Output a scoring row."
        print "%10s        %4d     %0.3f        %0.3f        %0.3f"%(
            name, self.gold, self.precision(), self.recall(), self.fscore())

    def latex_row(self, name):
        "Output a scoring row."
        return " %0.2f & %0.2f & %0.2f "%(100* self.precision(), 100 * self.recall(), 100 * self.fscore())



# def main():    
#     if sys.argv[1] == "gold":
#         for i, r in enumerate(HumanPair.get_all_from_pickle()):
#             for j, redact in enumerate(r.redactions):
#                 prediction = Prediction(i, redact.side - 1, redact.text, 
#                                         redact.start[1], text.Range(0,0,0,0))
#                 print "__CORRECT__", json.dumps(prediction.to_dict())
#         exit()



  #   aligner = algorithms[sys.argv[1]]
  # for i, r in enumerate(HumanPair.get_all_from_pickle()):
  #   print "ALIGN", i
  #   if False:
  #     try:
  #       d1, d2, image1, image2, new_redacts1, new_redacts2,   = d.make_docs(r)
  #       cPickle.dump((d1, d2, image1, image2, new_redacts1, new_redacts2), 
  #                    open("/home/srush/data/declass/tmp/data.%d.pickle"%i, "wb"))
  #     except Exception:
  #       print "fail"
  #   if True:
  #     try:
  #       # d1, d2, image1, image2, new_redacts1, new_redacts2 = \
  #       #     cPickle.load(open("/home/srush/data/declass/tmp/data.%d.pickle"%i, "rb"))
  #       d1, d2, image1, image2, new_redacts1, new_redacts2 = d.make_docs(r)
  #     except IOError:
  #       print "no doc"
  #     for prediction in aligner.align(d1, d2, image1, image2, i):
  #       print "__PREDICTED__: ", json.dumps(prediction.to_dict())
