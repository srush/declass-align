"""
Some baseline methods for document alignment. 
"""
import re
from itertools import takewhile, dropwhile
import redact.text_utils 
from redact.text_utils  import Range
from redact.experiments  import Prediction
import cv2

class Page:
    """
    A representation of a page in a document.

    Attributes
    ----------
    x : List
            The text of the document in lines. 
    
    y : List 
        The layout of the image in x,y coordinates.

    z :  
        The image as a numpy array.
    """
    def __init__(self, text, layout, image):
        self.x = text
        self.y = layout
        self.z = image

    def __str__(self):
        return "\n".join([ 
                "%d: %s"%(i,l)
                for i, l in enumerate(self.x)])

class TextAligner:
    """
    Simple aligner based on the line text of the document. 
    """

    def align(self, p1, p2, index):
        """
        Yields predictions of alignments.
      
        Parameters
        ----------
        p1, p2 : A pair of Page's
        The two pages to be aligned
        
        index :
          An identifiers of the pair.
        """
        # align = dp.AlignAlgorithm(p1, p2)
        # t1, i1 = p1.x, p1.y
        # t2, i2 = p2.x, p2.y
        ops = redact.text_utils.fuzzy_text_align(p1.x, p2.x)
        t = [p1.x, p2.x]
        for op in ops:
            if op[0] != "equal":
                r = Range.from_op(op)
                side = 0 if r[0].num_lines() > r[1].num_lines() else 1
                yield Prediction(index, side,
                                 r[side].text_from_range(t[side]), 
                                 0, r[side])
        # for side in [0,1]:
        #     for range in ret[side]:
        #         yield Prediction(index, side, 
        #                          text_from_range(t[side], range), 0, range)

IMAGE_PATH = "/home/srush/data/declass/Img/"
def make_docs(human_pair):
    """
    Construct potential documents to align.

    Parameters
    -----------
    human_pair : HumanPair
    
    Returns
    ---------
    p1, p2 : A pair of Pages  
    
    """
    page1_text = human_pair.page_text(1)
    page2_text = human_pair.page_text(2)
    
    t1 = process_text(page1_text)
    t2 = process_text(page2_text)

    im1 = "%s.png"%(human_pair.d1.img(human_pair.page1))
    im2 = "%s.png"%(human_pair.d2.img(human_pair.page2))
    im1, im2 = cv2.imread(IMAGE_PATH + im1), cv2.imread(IMAGE_PATH + im2)

    # Run image processing.
    #(b1, b2), (image1, image2), (nr1, nr2) = process_images(r, d1, d2)

    image1 = im1
    image2 = im2
    layout1 = None #make_layout(b1)
    layout2 = None#make_layout(b2)
    page1 = Page(t1, layout1, image1)
    page2 = Page(t2, layout2, image2)
    return page1, page2


def rdropwhile(lambd, ls):
    "Helper reverse dropwhile."
    return list(reversed(list(dropwhile(lambd, reversed(list(ls))))))

def process_text(page_text, min_length = 5):
    c = re.compile(r"\\n\\n|<\?BR\?>|<PARA>")

    l1 =  re.split(c, page_text.replace("</PARA>", ""))
    
    # Drop everything after <?HR?> footer. 
    l1 = takewhile(lambda a: "<?HR?>" not in a, l1)

    def bad_lines(line):
      return len(line.split()) <= 3 or \
          (sum(c.isupper() for c in line) / float(len(line)) >= 0.5 and \
             len(line.split()) <= min_length)

    # Dropping only lines at the beginning and end of the 
    # page that are bade. 
    l1 = dropwhile(bad_lines, l1)
    l1 = rdropwhile(bad_lines, l1)
    l1 = [l for l in l1 if len(l) > min_length]

    # Add a start and end symbol to the text.
    return ["B"] + l1 + ["T", "T"]

    # differ = difflib.SequenceMatcher(
    #   None,
    #   [TextAligner.M(t.to_text()) for t in t1.lines], 
    #   [TextAligner.M(t.to_text()) for t in t2.lines], 
    #   autojunk=None)
    # ops = differ.get_opcodes()

        # else:
        #   text1 = t1.get_range(Range(op[1], 0, op[2], 0))
        #   text2 = t2.get_range(Range(op[3], 0, op[4], 0))
        #   print len(text2), text2
        #   differ2 = difflib.SequenceMatcher(
        #     None, 
        #     [W(t.word) for t in text1], 
        #     [W(t.word) for t in text2], 
        #     autojunk=None)
        #   ops2 = differ2.get_opcodes()
        #   for op2 in ops2:
        #     print op2
        #     if op2[0] != "equal":
        #       diff = (op2[2] - op2[1]) - (op2[4] - op2[3])
        #       print diff
        #       if diff > 0:
        #         range = Range.from_corner(text1[op2[1]].index, text1[op2[2] - 1].index)
        #         print t1.text_from_range(range)
        #         if len(ret[0]) > 0 and ret[0][-1].adjacent(range):
        #           ret[0][-1].merge(range)
        #         else:
        #           ret[0].append(range)

        #       elif diff < 0:
        #         range = Range.from_corner(text2[op2[3]].index, text2[op2[4] - 1].index)
        #         print t2.text_from_range(range)
        #         if len(ret[1]) > 0 and ret[1][-1].adjacent(range):
        #           ret[1][-1].merge(range)
        #         else:
        #           ret[1].append(range)


    # t = [t1, t2]
    # for side in [0,1]:
    #   for range in ret[side]:
    #     yield Prediction(index, side, t[side].text_from_range(range), 0, range)
