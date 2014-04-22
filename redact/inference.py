from collections import namedtuple, defaultdict
from text_utils import fuzzy_text_align

def enum(*sequential, **named):
    """
    Helper class for making enum's in python.
    """
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    enums['keys'] = reverse.keys()
    return type('Enum', (), enums)

def to_text(x):
    return x

def char_len(x):
    return len(x)

def word_len(x):
    return len(x.split())

Doc = namedtuple('Doc', ['x', 'y', 'z'])
class AlignProblem:
    def __init__(self, d1, d2):
        self.d1 = d1
        self.d2 = d2
        self._fuzzy_cache = {}
        self._partial_cache = {}

    def in_footer(self, t1, t2):
        return (t1 >= len(self.d1.x) - 5 and t2 >= len(self.d2.x) - 5)

    def in_header(self, t1, t2):
        return (t1 < 5 and t2 < 5)

    def all_matches(self):
        return ([(i, j) for i in range(len(self.d1.x))
                 for j in range(len(self.d2.x)) ],
                [(i, j) for i in range(len(self.d1.y))
                 for j in range(len(self.d2.y)) ])

    def current(self, index):
        """
        Gets the current text and line positions.

        Parameters
        ----------
        d1, d2 : Documents

        Returns
        -------
        info : tuple (t1, l1, t2, l2)
        """
        return self.d1.x[index.t1], self.d1.y[index.l1], \
            self.d2.x[index.t2], self.d2.y[index.l2]

    def fuzzy_cache(self, cur):
        if (cur.t1, cur.t2) not in self._fuzzy_cache:
            self._fuzzy_cache[cur.t1, cur.t2] = \
                fuzzy_text_align(to_text(self.d1.x[cur.t1]),
                      to_text(self.d2.x[cur.t2]))
        return self._fuzzy_cache[cur.t1, cur.t2]

    def partial_cache(self, cur):
        if (cur.t1, cur.t2) not in self._partial_cache:
            self._partial_cache[cur.t1, cur.t2] = \
                partial(to_text(self.d1.x[cur.t1]),
                        to_text(self.d2.x[cur.t2]))
        return self._partial_cache[cur.t1, cur.t2]


    def close_line(self, cur, dist=10):
        x1, y1, x2, y2 = self.current(cur)
        return abs(y1.y - y2.y) < dist

    def wide_line(self, cur, side, dist=200):
        x1, y1, x2, y2 = self.current(cur)
        if side == 0:
            return y1.w > dist
        if side == 1:
            return y2.w > dist

    def short_text(self, cur, side, l = 5):
        x1, y1, x2, y2 = self.current(cur)
        if side == 0:
            return word_len(x1) < l
        if side == 1:
            return word_len(x2) < l


class ChartIndex(namedtuple('ChartIndex', ['h1', 'h2', 't1', 't2', 'l1', 'l2'])):
    """
    """
    def have_match(self):
        return (self.h1, self.h2) == (HS.NONE, HS.NONE)

    def have_redaction(self):
        return self.h1 == HS.REDACT or self.h2 == HS.REDACT

    def header_or_footer(self):
        return (self.h1 == HS.HEADER or self.h1 == HS.FOOTER or
                self.h2 == HS.HEADER or self.h2 == HS.FOOTER)


    def apply_operation(self, op):
        if op.text_op == TextOp.MATCH:
            c2 = self._replace(t1 = self.t1 - 1,
                               t2 = self.t2 - 1,
                               l1 = self.l1 - 1,
                               l2 = self.l2 - 1)

        elif op.text_op == TextOp.SKIP_LINE:
            c2 = self._replace(l1 = self.l1 - 1,
                               l2 = self.l2 - 1)

        elif op.text_op == TextOp.SKIP_LINE_LEFT:
            c2 = self._replace(l1 = self.l1 - 1)

        elif op.text_op == TextOp.SKIP_LINE_RIGHT:
            c2 = self._replace(l2 = self.l2 - 1)

        elif op.text_op == TextOp.SKIP_TEXT:
            c2 = self._replace(t1 = self.t1 - 1,
                               t2 = self.t2 - 1)

        elif op.text_op == TextOp.SKIP_TEXT_LEFT:
            c2 = self._replace(t1 = self.t1 - 1)

        elif op.text_op == TextOp.SKIP_TEXT_RIGHT:
            c2 = self._replace(t2 = self.t2 - 1)

        elif op.text_op == TextOp.REDACT_LEFT:
            c2 = self._replace(t2 = self.t2 - 1,
                               l2 = self.l2 - 1)

        elif op.text_op == TextOp.REDACT_RIGHT:
            c2 = self._replace(t1 = self.t1 - 1,
                               l1 = self.l1 - 1)
        else:
            assert False

        return c2._replace(h1 = op.last_left,
                           h2 = op.last_right)


    @staticmethod
    def initial_index():
        """
        Return the start index.
        """
        return ChartIndex(HS.HEADER, HS.HEADER, -1, -1, -1, -1)


    @staticmethod
    def last_index(d1, d2):
        return ChartIndex(HS.FOOTER, HS.FOOTER,
                          len(d1.x) - 1, len(d2.x) - 1,
                          len(d1.y) - 1, len(d2.y) - 1)


class ChartOp(namedtuple('ChartOp', ['last_left', 'last_right', 'text_op'])):

    @staticmethod
    def all_ops(t1, t2):
        """
        """
        yield ChartOp(HS.NONE, HS.NONE, TextOp.MATCH)

        ops = []
        if t1 <= 5 and t2 <= 5:
            ops = [HS.HEADER]

        for s in [HS.FOOTER, HS.NONE, HS] + ops:
            for s2 in [TextOp.SKIP_TEXT_LEFT, TextOp.SKIP_TEXT_RIGHT, TextOp.SKIP_TEXT] + \
                    [TextOp.SKIP_LINE_LEFT, TextOp.SKIP_LINE_RIGHT, TextOp.SKIP_LINE]:
                yield ChartOp(s, s, s2)

        yield ChartOp(HS.REDACT, HS.NONE, TextOp.REDACT_LEFT)
        yield ChartOp(HS.NONE, HS.REDACT, TextOp.REDACT_RIGHT)
        yield ChartOp(HS.HEADER, HS.HEADER, TextOp.MATCH)
        yield ChartOp(HS.FOOTER, HS.FOOTER, TextOp.MATCH)

TextOp = enum("MATCH",
              "REDACT_LEFT",
              "REDACT_RIGHT",
              "SKIP_LINE_LEFT",
              "SKIP_LINE_RIGHT",
              "SKIP_LINE",
              "SKIP_TEXT_LEFT",
              "SKIP_TEXT_RIGHT",
              "SKIP_TEXT")

HS = enum("NONE", "REDACT", "HEADER", "FOOTER")

ChartCell = namedtuple('ChartCell', ['score', 'op'])


class Path(namedtuple('Path', ['index', 'op'])):
    @staticmethod
    def display_path(align, path):
        """
        Prints the full alignment.

        Parameters
        -----------
        path : list of Path
           The path through the alignment.
        """
        for p in path: Path.show(align, p)

    @staticmethod
    def show(align, path, SIZE=50):
        """
        Prints a piece of the alignment.

        Parameters
        -----------
        path : Path
           The path through the alignment.
        """
        i = path.index
        text1 = to_text(align.d1.x[i.t1])[:SIZE] if i.h1 != HS.REDACT else "-"*SIZE
        text2 = to_text(align.d2.x[i.t2])[:SIZE] if i.h2 != HS.REDACT else "-"*SIZE
        back_index = i.apply_operation(path.op)
        #print align.score(back_index, path.op, i, noisy = True)
        def bs(box):
            return "(%02d,%02d,%02d,%02d)"%box
        print "%2d %10s %50s %d %d %50s %10s %f %2d %2d %2d %2d "%(
            path.op.text_op,
            bs(align.d1.y[i.l1]),
            text1,
            i.h1, i.h2,
            text2,
            bs(align.d2.y[i.l2]),
            0.0,#align.score(back_index, path.op, i),
            i.t1, i.l1, i.t2, i.l2)


    @staticmethod
    def redactions(path):
        r1, r2, l1, l2 = ([], [], [], [])
        for p in path:
            i = p.index
            if i.h2 == HS.REDACT:
                r1.append(i.t1)
                l1.append(i.l1)
            if i.h1 == HS.REDACT:
                r2.append(i.t2)
                l2.append(i.l2)
        return r1, r2, l1, l2

    @staticmethod
    def matches(path):
        r1 = {}
        r2 = {}

        for p in path:
            i = p.index
            if i.h1 != HS.REDACT and i.h2 != HS.REDACT:
                r1.setdefault(i.t1, [])
                r1[i.t1].append(i.t2)
                r2.setdefault(i.t2, [])
                r2[i.t2].append(i.t1)
        return r1, r2

    # @staticmethod
    # def off_matches(path):
    #     off = []
    #     for p in path:
    #         i = p.index
    #         if i.h1 != HS.REDACT and i.h2 != HS.REDACT:
    #             if not self.fuzzy_cache(i):
    #                 x1, y1, x2, y2 = i.current()
    #                 if abs(y1.w - y2.w) > 100:
    #                     off.append(i)
    #     return off


class AlignAlgorithm:
    params = {
        "match": 0.8,
        "partial_match": 0.5,
        "no_match": 0.001,
        "no_im_match": 0.1,
        "bad_match": 0.001,
        }

    hmm = {
        HS.NONE:
            {HS.NONE: 0.8,
             HS.REDACT: 0.1,
             HS.HEADER: 0.0,
             HS.FOOTER: 0.1},
        HS.HEADER:
            {HS.NONE: 0.1,
             HS.REDACT: 0.1,
             HS.HEADER: 0.8,
             HS.FOOTER: 0.001},
        HS.REDACT:
            {HS.NONE: 0.4,
             HS.REDACT: 0.5,
             HS.HEADER: 0.0,
             HS.FOOTER: 0.1},
        HS.FOOTER:
            {HS.NONE: 0.0,
             HS.REDACT: 0.0,
             HS.HEADER: 0.0,
             HS.FOOTER: 1.0}
        }

    def __init__(self, align):
        """
        Initialize the dynamic programming algorithm.

        Parameters
        ----------
        d1, d2 : Documents
          The documents to align.

        """
        self.align = align


    def score(self, cur, op, next):
        score = 1.0
        x1, y1, x2, y2 = self.align.current(cur)

        # Case 1: The previous lines match.
        if cur.have_match() and op.text_op == TextOp.MATCH:
            # The score of the text match.
            if self.align.fuzzy_cache(cur):
                score *= AlignAlgorithm.params["match"]
            elif self.partial_cache(cur):
                score *= AlignAlgorithm.params["partial_match"]
            else:
                score *= AlignAlgorithm.params["no_match"]


            # The score of the layout match.
            if self.align.close_line(cur, 5):
                score *= AlignAlgorithm.params["match"]
            elif self.align.close_line(cur):
                score *= AlignAlgorithm.params["partial_match"]
            else:
                score *= AlignAlgorithm.params["no_im_match"]

        # Case 2: The previous lines have a redaction.
        elif cur.have_redaction():
            if self.align.close_line(cur):
                score *= 0.01
            elif self.align.fuzzy_cache(cur):
                score *= 0.01
            else:
                score *= 0.9

        # Case 3: We are in the header or footer.
        elif cur.header_or_footer():
            if char_len(x1) < 20 and char_len(x2) < 20:
                score *= AlignAlgorithm.params["match"]
            else:
                score *= AlignAlgorithm.params["bad_match"]

            if self.align.fuzzy_cache(cur):
                score *= AlignAlgorithm.params["match"]
            else:
                score *= AlignAlgorithm.params["bad_match"]

        # p(h_i | h_{i-1}, x_i)
        # Transition score.
        def score_trans(a, b):
            return AlignAlgorithm.hmm[a][b]

        if op.text_op in [TextOp.SKIP_LINE_LEFT, TextOp.SKIP_LINE]:
            if self.align.wide_line(cur, 0):
                score *= AlignAlgorithm.params["bad_match"]

        if op.text_op in [TextOp.SKIP_LINE_RIGHT, TextOp.SKIP_LINE]:
            if self.align.wide_line(cur, 1):
                score *= AlignAlgorithm.params["bad_match"]

        if op.text_op in [TextOp.SKIP_TEXT_LEFT, TextOp.SKIP_TEXT]:
            if self.align.short_text(cur, 0):
                score *= AlignAlgorithm.params["match"]
            elif self.align.close_line(cur):
                score *= AlignAlgorithm.params["partial_match"]
            else:
                score *= AlignAlgorithm.params["bad_match"]

        if op.text_op in [TextOp.SKIP_TEXT_RIGHT, TextOp.SKIP_TEXT]:
            if self.align.short_text(cur, 1):
                score *= AlignAlgorithm.params["match"]
            elif self.align.close_line(cur):
                score *= AlignAlgorithm.params["partial_match"]
            else:
                score *= AlignAlgorithm.params["bad_match"]

        # Layout width.
        if op.text_op in [TextOp.MATCH, TextOp.REDACT_RIGHT]:
            if char_len(x1) * 4 < y1.w < char_len(x1) * 15:
                score *= AlignAlgorithm.params["match"]
            else:
                score *= AlignAlgorithm.params["no_im_match"]

        if op.text_op in [TextOp.MATCH, TextOp.REDACT_LEFT]:
            if char_len(x2) * 4 < y2.w < char_len(x2) * 15:
                score *= AlignAlgorithm.params["match"]
            else:
                score *= AlignAlgorithm.params["no_im_match"]

        score *= score_trans(cur.h1, next.h1)
        score *= score_trans(cur.h2, next.h2)
        return score


    def align_docs(self, textmatch, linematch, o1match=[], o2match=[]):
        """

        Parameters
        ----------
        textmatch :
           The text matches that are allowed.

        linematch :
           The alignment matches that are allowed.
        """
        pi = {}
        pi[ChartIndex.initial_index()] = ChartCell(1.0, None)

        prev = [(-1, 0), (0, -1), (-1, -1)]
        seen = set([(-1, -1)])
        # seen2 = set([(-1, -1)])
        # seen3 = set([(-1, -1)])
        # seen4 = set([(-1, -1)])

        for t1, t2 in textmatch:
            hidden_pairs = [(HS.NONE, HS.NONE),
                            (HS.NONE, HS.REDACT),
                            (HS.REDACT, HS.NONE)]

            if not any(((t1 + a, t2 + b) in seen for a,b in prev)):
                continue

            if self.align.in_header(t1, t2):
                hidden_pairs += [(HS.HEADER, HS.HEADER)]

            if self.align.in_footer(t1, t2):
                hidden_pairs += [(HS.FOOTER, HS.FOOTER)]

            for l1, l2 in linematch:
                # if (t1, l1) not in o1match or (t2, l2) not in o2match: continue
                # if (l1 - 1, l2) not in seen2 and (l1, l2 - 1) not in seen2 and (l1 - 1, l2 - 1) not in seen2 and (l1, l2) not in seen2: continue
                # if (t1 - 1, l1) not in seen3 and (t1, l1 - 1) not in seen3 and (t1 - 1, l1 - 1) not in seen3: continue
                # if (t2 - 1, l2) not in seen4 and (t2, l2 - 1) not in seen4 and (t2 - 1, l2 - 1) not in seen4: continue

                for h1, h2 in hidden_pairs:
                    i = ChartIndex(h1, h2, t1, t2, l1, l2)
                    ls = []
                    for op in ChartOp.all_ops(t1, t2):
                        back_index = i.apply_operation(op)
                        if back_index not in pi: continue
                        score = pi[back_index].score * self.score(back_index, op, i)
                        ls.append(ChartCell(score, op))

                    if ls:
                        r = max(ls)
                        if r.score > 0.0:
                            pi[i] = max(ls)
                            seen.add((t1, t2))
                            # seen2.add((l1, l2))
                            # seen3.add((t1, l1))
                            # seen4.add((t2, l2))

        last_index = ChartIndex.last_index(self.align.d1, self.align.d2)
        score = pi[last_index]


        # Collect final path using back pointers.

        def walk_back(index, path):
            if pi[index].op == None: return
            path.append(Path(index, pi[index].op))
            back_index = index.apply_operation(pi[index].op)
            walk_back(back_index, path)

        path = []
        walk_back(last_index, path)
        path.reverse()
        print "FINAL SCORE", score
        return score, path






def main():
  # t1 = ["hello", "goodbye", "finally"]
  # t2 = ["hello", "goodbye", "george"]
  # prob = AlignProblem(t1, t2)
  # matches = match(t1, t2)
  # print >>sys.stderr, matches
  # assert((0, 0) in matches)
  # assert((1, 2) in matches)
  # assert((2, 2) in matches)

    from baselines import Box
    t1 = ["hello", "goodbye", "hello", "george"]
    t2 = ["hello", "goodbye", "george"]
    i1 = [Box(y, 0,0,0) for y in [1, 2, 3, 4]]
    i2 = [Box(y, 0,0,0) for y in [1, 2, 4]]
    d1 = Doc(t1, i1, None)
    d2 = Doc(t2, i2, None)

    align = AlignProblem(d1, d2)
    text_matches, image_matches = align.all_matches()
    alg = AlignAlgorithm(align)
    score, path = alg.align_docs(text_matches, image_matches)
    Path.display_path(align, path)
    # r1, r2 = align.get_redactions(path)
    # assert r2 == [2]
    # assert r1 == []
    # print score

if __name__ == "__main__":
    main()
