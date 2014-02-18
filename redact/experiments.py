import preprocessing as d

class FScore:
    """
    Compute F1-Score based on gold set and test set.
    """

    def __init__(self):
        self.gold = 0
        self.test = 0
        self.correct = 0

    def increment(self, gold_set, test_set):
        "Add examples from sets."
        self.gold += len(gold_set)
        self.test += len(test_set)
        self.correct += len([1 for g in gold_set 
                             if any([t == g or g == t for t in test_set])])

    def fscore(self): 
        pr = self.precision() + self.recall()
        if pr == 0: return 0.0
        return (2 * self.precision() * self.recall()) / float(pr)

    def precision(self): 
        if self.test == 0: return 0.0
        return self.correct / float(self.test)

    def recall(self): 
        if self.gold == 0: return 0.0
        return self.correct / float(self.gold)    

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

class Prediction:
  """
  A prediction of a redaction made by a model. 

  Attributes
  -----------
  
  index : 
     Index of example.

  side :
     The side of the pair with the redaction.

  text :
     The predicted redaction text.

  position : 
     The predicted redaction image position.

  range : 
       
  """

  def __init__(self, index, side, text, position, range):
    self.index = index
    self.side = side
    self.text = text
    self.position = position
    self.range = range

  def __str__(self):
    return str(self.to_dict())

  @staticmethod
  def from_dict(d):
    return Prediction(d["i"], d["side"], d["text"], d["position"], -1)

  def to_dict(self):
    return {"i": self.index, 
            "side": self.side, 
            "text": self.text, 
            "position": self.position,
            "range": self.range.to_dict()}

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
