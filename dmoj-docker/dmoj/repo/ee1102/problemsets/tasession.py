"""TA Session problem set: the 8 "Your Turn" questions from the session slides, in slide order.

Each problem is a function problem. `examples` are the slide examples (visible, first test cases, and
their expected values are asserted against `solution`); `hidden` are extra test cases whose expected
values come from `solution`. Load with: manage.py ee1102_problemset tasession
"""
import random

_rng = random.Random(1102)

JUDGING_NOTE = """## How it's judged
Only write the function: don't read input or print the answer. The judge calls your function with
each test's arguments and checks what it **returns**. `print` inside the function is fine for
debugging; the judge ignores it. The examples above are the first test cases; the rest are hidden."""

PROBLEMS = [
    dict(
        code='splittime', name='Variables & Execution', function='split_time',
        description="""Write a function `split_time(s)`. `s` is a number of seconds. Return a list
`[days, hours, minutes, seconds]` where hours < 24, minutes < 60 and seconds < 60.

Use only arithmetic (`//` and `%`), no loops.""",
        examples=[
            ((100000,), [1, 3, 46, 40], 'split_time(100000)   # [1, 3, 46, 40]'),
            ((59,), [0, 0, 0, 59], 'split_time(59)       # [0, 0, 0, 59]'),
            ((86400,), [1, 0, 0, 0], 'split_time(86400)    # [1, 0, 0, 0]'),
        ],
        hint="Work from the biggest unit down. After taking out the days, what's left over?",
        starter='def split_time(s):\n    # your code here\n    pass\n',
        solution='def split_time(s):\n    return [s // 86400, s % 86400 // 3600, s % 3600 // 60, s % 60]\n',
        hidden=[(0,), (3600,), (3599,), (90061,), (86399,), (172800 + 7322,), (1000000000,)],
    ),
    dict(
        code='nestedget', name='Indexing & Nested Lists', function='get',
        description="""Write a function `get(data, path)`. `data` is any mix of nested lists, dicts and
strings. `path` is a list of indices/keys. Follow the path **one bracket at a time** and return what
you end up at.""",
        examples=[
            (([10, [20, 30], [[40, 50], 60]], [2, 0, 1]), 50,
             'get([10, [20, 30], [[40, 50], 60]], [2, 0, 1])           # 50  (data[2][0][1])'),
            (({'asha': {'marks': [85, 90]}}, ['asha', 'marks', 1]), 90,
             'get({"asha": {"marks": [85, 90]}}, ["asha", "marks", 1])  # 90'),
            (('python', [-1]), 'n', 'get("python", [-1])                                     # "n"'),
            (([1, 2], []), [1, 2], 'get([1, 2], [])                                         # [1, 2]  (empty path)'),
        ],
        hint='`get(data, [2, 0, 1])` should do exactly what `data[2][0][1]` does. What changes after each step?',
        starter='def get(data, path):\n    # your code here\n    pass\n',
        solution='def get(data, path):\n    for p in path:\n        data = data[p]\n    return data\n',
        hidden=[
            ({'a': {'b': {'c': 42}}}, ['a', 'b', 'c']),
            (['abc', ['de', 'fgh']], [1, 1, 2]),
            ([[1, 2], [3, 4]], [-1, -2]),
            ({'x': [1, [2, {'y': 'deep'}]]}, ['x', 1, 1, 'y', 0]),
            ({'k': {'z': 1}}, ['k']),
            ([[[[[5]]]]], [0, 0, 0, 0, 0]),
            ({'students': [{'name': 'ravi', 'marks': [70, 80]}, {'name': 'meera', 'marks': [95, 88]}]},
             ['students', 1, 'marks', -1]),
            ('hello', []),
        ],
    ),
    dict(
        code='longeststreak', name='Loops', function='longest_streak',
        description="""Write a function `longest_streak(marks)`. Return the length of the longest run of
**consecutive** marks that are 50 or more.""",
        examples=[
            (([55, 60, 40, 70, 80, 90, 20],), 3, 'longest_streak([55, 60, 40, 70, 80, 90, 20])   # 3'),
            (([55, 60, 70],), 3, 'longest_streak([55, 60, 70])                   # 3'),
            (([10, 20],), 0, 'longest_streak([10, 20])                       # 0'),
            (([],), 0, 'longest_streak([])                             # 0'),
        ],
        hint='You need two accumulators: the current streak and the best streak so far. When does each one change?',
        starter='def longest_streak(marks):\n    # your code here\n    pass\n',
        solution=('def longest_streak(marks):\n    cur = best = 0\n    for m in marks:\n'
                  '        cur = cur + 1 if m >= 50 else 0\n        best = max(best, cur)\n    return best\n'),
        hidden=[
            ([50],), ([49, 50, 49],), ([10, 60, 70],), ([60, 70, 10, 80, 90],), ([49] * 5,),
            ([51, 20, 52, 53, 20, 54, 55, 56, 57, 20, 58],),
            ([100] * 1000,),
            ([_rng.choice([_rng.randint(0, 49), _rng.randint(50, 100)]) for _ in range(500)],),
        ],
    ),
    dict(
        code='compress', name='Functions', function='compress',
        description="""Write a function `compress(s)`. Return `s` with each run of repeated characters
replaced by the character followed by its count.""",
        examples=[
            (('aaabccdd',), 'a3b1c2d2', 'compress("aaabccdd")   # "a3b1c2d2"'),
            (('abc',), 'a1b1c1', 'compress("abc")        # "a1b1c1"'),
            (('zzzzzz',), 'z6', 'compress("zzzzzz")     # "z6"'),
            (('',), '', 'compress("")           # ""'),
        ],
        hint='`str(3)` gives `"3"`. When does a run end? Don\'t forget the **last** run.',
        starter='def compress(s):\n    # your code here\n    pass\n',
        solution=('def compress(s):\n    out = ""\n    i = 0\n    while i < len(s):\n        j = i\n'
                  '        while j < len(s) and s[j] == s[i]:\n            j += 1\n'
                  '        out += s[i] + str(j - i)\n        i = j\n    return out\n'),
        hidden=[('a',), ('aabbaa',), ('a' * 12,), ('AaA',), ('  xx',), ('1112',), ('ab' * 50,),
                ('x' * 1000 + 'y',)],
    ),
    dict(
        code='rotate', name='Changing Things', function='rotate', must_be_new=True,
        description="""Write a function `rotate(lst, k)`. Return a **new** list: `lst` rotated to the right
by `k` places. The original `lst` must **not** change (the judge checks!). `k` can be larger than
`len(lst)`.""",
        examples=[
            (([1, 2, 3, 4, 5], 2), [4, 5, 1, 2, 3], 'rotate([1, 2, 3, 4, 5], 2)   # [4, 5, 1, 2, 3]'),
            (([1, 2, 3], 4), [3, 1, 2], 'rotate([1, 2, 3], 4)         # [3, 1, 2]   (same as k = 1)'),
            (([1, 2, 3], 3), [1, 2, 3], 'rotate([1, 2, 3], 3)         # [1, 2, 3]'),
            (([], 5), [], 'rotate([], 5)                # []'),
        ],
        hint='Where does the item at index `i` end up? Watch out for `k % 0`.',
        starter='def rotate(lst, k):\n    # your code here\n    pass\n',
        solution=('def rotate(lst, k):\n    if not lst:\n        return []\n    k %= len(lst)\n'
                  '    return lst[-k:] + lst[:-k] if k else lst[:]\n'),
        hidden=[([1, 2, 3, 4, 5], 0), ([1, 2, 3, 4, 5], 1), (['a', 'b', 'c', 'd', 'e', 'f', 'g'], 1000003),
                ([42], 7), ([[1, 2], [3], [4, 5]], 1), ([1, 2, 3, 4], 8), (list(range(1000)), 250)],
    ),
    dict(
        code='classify', name='Conditions', function='classify',
        description="""Write a function `classify(a, b, c)`. `a`, `b`, `c` are side lengths (whole numbers,
in **any order**). Return `"invalid"` if they can't form a triangle (a side ≤ 0, or two sides add up
to ≤ the third), else `"equilateral"`, `"isosceles"`, `"right"` (right-angled), or `"scalene"`,
**in that order of priority**.""",
        examples=[
            ((5, 3, 4), 'right', 'classify(5, 3, 4)   # "right"        (3*3 + 4*4 == 5*5)'),
            ((2, 2, 3), 'isosceles', 'classify(2, 2, 3)   # "isosceles"'),
            ((4, 5, 6), 'scalene', 'classify(4, 5, 6)   # "scalene"'),
            ((1, 2, 3), 'invalid', 'classify(1, 2, 3)   # "invalid"      (1 + 2 is not > 3)'),
            ((1, 1, 5), 'invalid', 'classify(1, 1, 5)   # "invalid"      (not "isosceles"!)'),
        ],
        hint='The order of your checks matters. Which check has to come first? Which side could be the longest?',
        starter='def classify(a, b, c):\n    # your code here\n    pass\n',
        solution=('def classify(a, b, c):\n    if a <= 0 or b <= 0 or c <= 0 or a + b <= c or a + c <= b or b + c <= a:\n'
                  '        return "invalid"\n    if a == b == c:\n        return "equilateral"\n'
                  '    if a == b or b == c or a == c:\n        return "isosceles"\n'
                  '    if a*a + b*b == c*c or a*a + c*c == b*b or b*b + c*c == a*a:\n        return "right"\n'
                  '    return "scalene"\n'),
        hidden=[(3, 3, 3), (0, 0, 0), (-3, 4, 5), (4, 5, 3), (13, 5, 12), (5, 12, 13), (3, 2, 2), (2, 3, 2),
                (7, 8, 10), (2, 3, 5), (1, 1, 2), (300000, 400000, 500000), (10, 1, 1)],
    ),
    dict(
        code='flatten', name='Recursion', function='flatten',
        description="""Write a function `flatten(x)`. `x` is a list that may contain numbers and other
lists, nested to any depth. Return a flat list of all the numbers, in order.""",
        examples=[
            (([1, [2, [3, 4]], [], 5],), [1, 2, 3, 4, 5], 'flatten([1, [2, [3, 4]], [], 5])   # [1, 2, 3, 4, 5]'),
            (([[[7]]],), [7], 'flatten([[[7]]])                   # [7]'),
            (([[[]]],), [], 'flatten([[[]]])                    # []'),
        ],
        hint='Same pattern as `deep_sum`. Number → base case; list → loop over items and trust the recursive call.',
        starter='def flatten(x):\n    # your code here\n    pass\n',
        solution=('def flatten(x):\n    if type(x) == int:\n        return [x]\n    r = []\n'
                  '    for i in x:\n        r = r + flatten(i)\n    return r\n'),
        hidden=[([],), ([1, 2, 3],), ([[1, [2]], 3, [[4, [5, [6]]]]],), ([[], [[]], [[], []]],),
                ([0, [-1, [-2]], 3],), (eval('[' * 50 + '1' + ']' * 50),),
                ([[i, [i + 1]] for i in range(0, 400, 2)],)],
    ),
    dict(
        code='mostcommon', name='Debugging Skills', function='most_common',
        description="""The function below is meant to return the value that appears most often in `lst`,
but running it on `[3, 1, 3, 2, 3, 1]` gives `KeyError: 0` instead of `3`.

There are **three** bugs, and fixing one reveals the next. Submit the fixed function.
If there's a tie, return the value that appears first.

The buggy code is already in the editor below.""",
        examples=[
            (([3, 1, 3, 2, 3, 1],), 3, 'most_common([3, 1, 3, 2, 3, 1])   # expected 3, got KeyError: 0'),
        ],
        hint='Fix one error, run it again, and see what the next wrong answer tells you.',
        starter=('def most_common(lst):\n    # the value that appears most often\n    counts = {}\n'
                 '    for x in range(len(lst)):\n        counts[x] = counts[x] + 1\n    best = None\n'
                 '    best_count = 0\n    for k in counts:\n        if counts[k] > best_count:\n'
                 '            best = k\n    return best\n'),
        solution=('def most_common(lst):\n    counts = {}\n    for x in lst:\n        counts[x] = counts.get(x, 0) + 1\n'
                  '    best = None\n    best_count = 0\n    for k in counts:\n        if counts[k] > best_count:\n'
                  '            best = k\n            best_count = counts[k]\n    return best\n'),
        hidden=[([1, 2, 2, 1],), ([5],), ([2, 1, 1, 2, 3],), ([4, 5, 6],), ([-1, -1, 0],), (['a', 'b', 'b'],),
                ([7, 8, 8, 9, 9, 9, 8],), ([_rng.randint(1, 20) for _ in range(1000)],)],
    ),
    dict(
        code='spiral', name='Putting It Together: Grids', function='spiral',
        description="""Write a function `spiral(grid)`. `grid` is a rectangular grid given as a list of rows
(it may be `[]`, with no rows). Return a list of all its values in **clockwise spiral** order, starting
at the top-left: along the top row, down the right column, back along the bottom row, up the left
column, then the same again on the inside.

`grid` must **not** change (the judge checks!).""",
        examples=[
            (([[1, 2, 3], [4, 5, 6], [7, 8, 9]],), [1, 2, 3, 6, 9, 8, 7, 4, 5],
             'spiral([[1, 2, 3], [4, 5, 6], [7, 8, 9]])   # [1, 2, 3, 6, 9, 8, 7, 4, 5]'),
            (([[1, 2, 3, 4], [5, 6, 7, 8]],), [1, 2, 3, 4, 8, 7, 6, 5],
             'spiral([[1, 2, 3, 4], [5, 6, 7, 8]])        # [1, 2, 3, 4, 8, 7, 6, 5]'),
            (([[1], [2], [3]],), [1, 2, 3], 'spiral([[1], [2], [3]])                    # [1, 2, 3]'),
            (([],), [], 'spiral([])                                 # []'),
        ],
        hint=('Keep four boundaries: `top`, `bottom`, `left`, `right`. After walking one side, move that '
              'boundary inwards. When there is only one row or column left, make sure you don\'t walk back over it.'),
        starter='def spiral(grid):\n    # your code here\n    pass\n',
        solution=('def spiral(grid):\n    out = []\n    if not grid:\n        return out\n'
                  '    top, bottom, left, right = 0, len(grid) - 1, 0, len(grid[0]) - 1\n'
                  '    while top <= bottom and left <= right:\n'
                  '        for j in range(left, right + 1):\n            out.append(grid[top][j])\n        top += 1\n'
                  '        for i in range(top, bottom + 1):\n            out.append(grid[i][right])\n        right -= 1\n'
                  '        if top <= bottom:\n            for j in range(right, left - 1, -1):\n'
                  '                out.append(grid[bottom][j])\n            bottom -= 1\n'
                  '        if left <= right:\n            for i in range(bottom, top - 1, -1):\n'
                  '                out.append(grid[i][left])\n            left += 1\n    return out\n'),
        hidden=[([[7]],), ([[1, 2, 3, 4, 5]],), ([[1, 2], [3, 4]],),
                ([[r * 4 + c for c in range(4)] for r in range(4)],),
                ([[r * 5 + c for c in range(5)] for r in range(3)],),
                ([[r * 3 + c for c in range(3)] for r in range(5)],),
                ([['a', 'b'], ['c', 'd'], ['e', 'f']],),
                ([[r * 10 + c for c in range(10)] for r in range(10)],),
                ([[r * 7 + c for c in range(7)] for r in range(20)],)],
    ),
    dict(
        code='mergeintervals', name='Putting It Together: Intervals', function='merge_intervals',
        description="""Write a function `merge_intervals(intervals)`. `intervals` is a list of `[start, end]`
pairs of whole numbers (`start <= end`), in **any order**. Merge every group of overlapping intervals
into one, and return a **new** list of the merged intervals, sorted by start. Intervals that just touch
(like `[1, 4]` and `[4, 5]`) count as overlapping.

The original `intervals` (including the pairs inside it) must **not** change (the judge checks!).""",
        examples=[
            (([[1, 3], [2, 6], [8, 10], [15, 18]],), [[1, 6], [8, 10], [15, 18]],
             'merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]])   # [[1, 6], [8, 10], [15, 18]]'),
            (([[1, 4], [4, 5]],), [[1, 5]], 'merge_intervals([[1, 4], [4, 5]])                     # [[1, 5]]  (touching)'),
            (([[5, 6], [1, 2]],), [[1, 2], [5, 6]], 'merge_intervals([[5, 6], [1, 2]])                     # [[1, 2], [5, 6]]'),
            (([],), [], 'merge_intervals([])                                   # []'),
        ],
        hint=('Sort first (`sorted(intervals)` sorts by start). Then each interval either extends the last merged '
              'one or starts a new one. Careful: `sorted()` makes a new outer list, but the pairs inside are '
              'the **same** lists as in the input.'),
        starter='def merge_intervals(intervals):\n    # your code here\n    pass\n',
        solution=('def merge_intervals(intervals):\n    out = []\n    for s, e in sorted(intervals):\n'
                  '        if out and s <= out[-1][1]:\n            out[-1][1] = max(out[-1][1], e)\n'
                  '        else:\n            out.append([s, e])\n    return out\n'),
        hidden=[([[1, 10], [2, 3], [4, 5]],), ([[3, 3]],), ([[1, 2], [2, 3], [3, 4]],), ([[8, 9], [1, 5], [4, 8]],),
                ([[1, 2], [1, 2]],), ([[1, 2], [3, 4]],), ([[-5, -1], [-2, 2], [10, 20]],),
                ([[5, 10], [1, 20]],),
                ([[a, a + _rng.randint(0, 30)] for a in (_rng.randint(0, 5000) for _ in range(500))],)],
    ),
]
