"""
Helper classes for managing human-annotated files. 
"""
from alignment.data.docs import *
import cPickle

class HumanRedact:
    "A redaction identified by a person."
    def __init__(self, start, end, textBound, text, side):
        self.start = start
        self.end = end
        self.textBound = textBound
        self.text = text
        self.side = side

    @staticmethod
    def for_pair(c, id):
        "Get a HumanRedaction by ID."
        q = "select * from DocumentPairHumanRedact where pairId = %s"
        c.execute(q, id)
        keep = []
        for row in c:
            hr = HumanRedact((row["startX"], row["startY"]), 
                             (row["endX"], row["endY"]), 
                             (row["startText"], row["endText"]), 
                             row["text"], row["side"])
        keep.append(hr)
        return keep

class HumanPair:
    "A redaction pair with metadata of identification."
    def __init__(self, d1, d2, page1, page2, redactions, id):
        self.d1 = d1
        self.d2 = d2
        self.page1 = page1
        self.page2 = page2
        self.redactions = redactions
        self.id = id

    @staticmethod
    def get_all(c):
        "Get all of the human redactions for aligned docs."
        q = "select * from DocumentPairHuman where badmatch=0"
        c.execute(q)
        pairs = []
        for row in c:
            redacts = HumanRedact.for_pair(c, row["id"])
            d1 = Document.from_id(c, row["docId1"])
            d2 = Document.from_id(c, row["docId2"])
            pairs.append(HumanPair(d1, d2, 
                                   row["page1"], 
                                   row["page2"], 
                                   redacts, 
                                   row["id"]))
        return pairs

    @staticmethod
    def get_all_from_pickle(file = "/tmp/human.pickle"):
        "Load human redaction from pickle file"
        return cPickle.load(open("/tmp/human.pickle", 'rb'))
  

  
# When called as executable, writes all human redactions to a pickle file.
if __name__ == "__main__":  
    import sys
    import cPickle
    import alignment.data.passwd as passwd
    db = passwd.get_db()
    c = passwd.get_cursor(db)
    all = HumanPair.get_all(c)
    cPickle.dump(all, open("/tmp/human.pickle", 'wb'))


# def get_all_from_db():
#   import MySQLdb as mysql
#   import alignment.passwd as passwd
#   db = passwd.get_db()
#   c = db.cursor(mysql.cursors.DictCursor)

#   pages = set()
#   for l in open("/tmp/eval_list"):
#     t = l.split()
#     if len(t) != 8: continue
#     f, pair, id1, id2, y1, y2, p1, p2= t
#     if f != "PAGE": continue
#     pages.add((id1, id2, y1, y2, p1, p2))
#   pages = list(pages)

#   for p in pages:
#     (id1, id2, y1, y2, p1, p2) = p
#     d1 = Document.from_id(c, id1)
#     d2 = Document.from_id(c, id2)
#     yield HumanPair(d1, d2, int(p1), int(p2), [])
