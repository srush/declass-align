"""
Helper classes for managing human-annotated files. 
"""

from redact.data.docs import Document 

class HumanRedact:
    "A specific instance of a redaction identified by a person."

    def __init__(self, start, end, textBound, text, side):
        """
        
        Attributes
        -----------

        start : 
           Image start position (X, Y) position.

        end :
           Image end position (X, Y) position.

        textBound : 
           Text-range character (start, end) 

        text : string
           The text itself.

        side : bool
           Which side the redaction is on.
        """
    
        self.start = start
        self.end = end
        self.textBound = textBound
        self.text = text
        self.side = side

    @staticmethod
    def for_pair(cursor, pair_id):
        """
        Get all of the human-annotated redactions for a doc pair_id.

        Parameters
        -----------
        
        cursor: 
            A DB cursor.

        pair_id: 
            The document pair_id to search.

        """
        q = "select * from DocumentPairHumanRedact where pairId = %s"
        cursor.execute(q, pair_id)
        keep = []
        for row in cursor:
            hr = HumanRedact((row["startX"], row["startY"]), 
                             (row["endX"], row["endY"]), 
                             (row["startText"], row["endText"]), 
                             row["text"], row["side"])
            keep.append(hr)
        return keep

class HumanPair:
    """
    A pair of pages that may or may not have redactions. 

    
    Attributes:
    -----------
    
    d1, d2: Documents
       The documents that are matched. 

    page1, page2 : ints
       The page number of the two documents.

    redactions : List of HumanRedacts
       The human redacts for this pair.

    id : int
       The pair_id in the database for this pair.

    """

    def __init__(self, d1, d2, page1, page2, redactions, pair_id):
        self.d1 = d1
        self.d2 = d2
        self.page1 = page1
        self.page2 = page2
        self.redactions = redactions
        self.id = pair_id

    def page_text(side):
        """
        Returns the text of the page matched on side.
        """
        if side == 1:
            return self.d1.get_page_text(self.page1)
        else:
            return self.d2.get_page_text(self.page2)

    @staticmethod
    def get_all(cursor):
        """
        Get all of the human-labeled pair redactions in the database.

        """
        q = "select * from DocumentPairHuman where badmatch=0"
        cursor.execute(q)
        pairs = []
        for row in cursor:
            redacts = HumanRedact.for_pair(cursor, row["id"])
            d1 = Document.from_id(cursor, row["docId1"])
            d2 = Document.from_id(cursor, row["docId2"])
            pairs.append(HumanPair(d1, d2, 
                                   row["page1"], 
                                   row["page2"], 
                                   redacts, 
                                   row["id"]))
        return pairs
  
  
# When called as executable, writes all human redactions to a pickle file.
if __name__ == "__main__":  
    import sys
    import redact.data.passwd as passwd
    db = passwd.get_db()
    cursor = passwd.get_cursor(db)
    all = HumanPair.get_all(cursor)
    

