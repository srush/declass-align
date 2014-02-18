import difflib

def fuzzy_text_align(text1, text2):
    differ = difflib.SequenceMatcher(
        None,
        [FuzzyLine(t) for t in text1], 
        [FuzzyLine(t) for t in text2], 
        autojunk=None)
    return differ.get_opcodes()

class FuzzyLine:
    """
    Wrapper for fuzzy line/word matching. 
    """
    def __init__(self, w):
        """
        w : string
           The line to wrap.
        """
        self.w = w

    def __eq__(self, o):
        return fuzzy(self.w, o.w)

    def __hash__(self):
        return hash(self.w)

def fuzzy(l1, l2, thres = 0.8):
    """
    Returns true if two lines are close matches.

    l1, l2 : strings
       The lines to match.

    thres : 
       The threshold to check.
    """
    ratio = difflib.SequenceMatcher(None, l1, l2).ratio() 
    return ratio > thres

class Index:
  """
  An index is a position inside of the text.
  
  Attributes:
  -------------
  line : 
      The line index from the top.

  word :
      The word index from the start of the line
  """

  def __init__(self, line, word):
      self.line = line
      self.word = word

  def to_dict(self):
    return {"line": self.line_index, 
            "word": self.word_index}


class Range:
  """
  A range within a text, specified by a start and end index.
  
  Attributes:
  -------------
  start, end : Index
      The start and end borders
  
  """
  def __init__(self, start_line, start_word, end_line, end_word):
      self.start = Index(start_line, start_word)
      self.end = Index(end_line, end_word)

  def num_lines(self):
      return abs(self.start.line - self.end.line)


  @staticmethod
  def from_op(op):
      return Range(op[1], 0, op[2], 0), Range(op[3], 0, op[4], 0)

  def is_one_line(self):
      """
      Is the redaction one line or more.
      """
      return abs(self.start.line - self.end.line) <= 1

  def line_indices(self):
      """
      Gives a pair start line and end line
      """
      return self.start.line, self.end.line

  def word_indices(self):
      return self.start.word, self.end.word

  def to_dict(self):
      return [self.start_index.to_dict(), self.end_index.to_dict()]

  # def diff(self, start_line, end_line):
  #     """
  #     Compares two ranges by taking L1 distance betwen line indices.
  #     """
  #     return abs(self.start.line - start_line) + \
  #         abs(self.end.line - end_line) 
    
  # def matches(self, start_line_index, end_line_index, max_dist = 2):
  #     "Checks that end boundaries are close to the range end."
  #     return abs(self.start_index.line_index - start_line_index) <= max_dist or \
  #         abs(self.end_index.line_index - end_line_index) <= max_dist
 

  # def adjacent(self, range, max_line_dist = 3, max_word_end = 10):
  #     "Checks whether as range is nearly adjacent."
  #     if self.end_index.line_index == range.start_index.line_index and \
  #             abs(self.end_index.word_index - 
  #                 range.start_index.word_index) <= max_line_dist:
  #         return True

  #     if self.end_index.line_index == range.start_index.line_index - 1 and \
  #             (range.start_index.word_index) <= max_line_dist and \
  #             self.end_index.word_index > max_word_end:
  #         return True
  #     return False

  # def merge(self, range):
  #   "Change the range to cover given adjacent range."
  #   self.end_index = range.end_index

  # @staticmethod
  # def from_corner(start, end):
  #   "Returns a range from a start and end index."
  #   return Range(start.line_index, start.word_index, 
  #                end.line_index, end.word_index)

# class Text:
#     """
#     Page text. Represented by x on a page.
#     """

#     def __init__(self, t):
#         """
#         Parameters:
#         ------------
#         t : 
#             Lines in a document.
#         """

#         self.t = t
#         self._label()

#   def _label(self):
#       "Index the text into Lines"
#       self.lines = []
#       for line_num, line in enumerate(self.t):
#           words = []
#           for word_num, word in enumerate(line.split()):
#               words.append(IndexedWord(Index(line_num, word_num), word))
#           self.lines.append(Line(line_num, words))
  
#   def __len__(self):
#       return len(self.lines)

#   def __getitem__(self, i):
#       return self.lines[i]

  # def get_range(self, range):
  #   "Return the IndexedWords in a range."
  #   s, e = range.line_indices()
  #   sw, ew = range.word_indices()
  #   if s == e:
  #     return self.lines[s].words[sw:ew]
  #   return self.lines[s].after_text(sw) + \
  #       sum([line.words for line in self.lines[s + 1: e]], []) + \
  #       self.lines[e].before_text(ew)
  
  # def text_from_range(self, range):
  #   "Returns the text corresponding to a range."
  #   return " ".join([word.word for word in self.get_range(range)])

  # def average_length(self):
  #   "Mean line length."
  #   return sum([line.word_len() for line in self.lines]) / float(len(self.lines))

