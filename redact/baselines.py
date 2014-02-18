"""
Some baseline methods for document alignment. 
"""


class TextAligner:
  """
  Simple aligner based on the line text of the document. 
  """

  def align(self, d1, d2, im1, im2, index):
      # align = dp.AlignAlgorithm(d1, d2)
      # t1, i1 = d1.x, d1.y
      # t2, i2 = d2.x, d2.y
      ops = fuzzy_text_align(d1.x, d2.x)
      for op in ops:
          if op[0] != "equal":
              r1, r2 = Range.from_op(op)
              side = 1 if r1.num_lines() > r2.num_lines() else 0
              yield Prediction(index, 0,
                               t[side].text_from_range(r1), 
                               0, r1)

    t = [t1, t2]
    for side in [0,1]:
      for range in ret[side]:
        yield Prediction(index, side, 
                         t[side].text_from_range(range), 0, range)

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
    t = [t1, t2]
    for side in [0,1]:
      for range in ret[side]:
        yield Prediction(index, side, t[side].text_from_range(range), 0, range)
