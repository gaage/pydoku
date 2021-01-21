#!/usr/local/bin/python
"""
This is a command-line input utility for sudoku puzzels
The pydoku solver is based on numpy arrays and expects all
entries given as numbers, using 0 as the blank placeholder.

With this input utility, any symbols can be assigned for the given numbers,
except "." which is used as plaeholder for the blanks.

The utility will also determine the shape of the puzzle, from the
number of elements given, and check that the number of symbols
used matches.
"""
import sys, re
from pydoku import Pydoku

blank_symbol = '.'

print """
*** Solve a sudoku puzzle! ***
Enter puzzle row by row using "{}" for blanks and one or more spaces between symbols.
Single blank lines are allowed also.
Enter two blank lines when all symbols have been entered.
Alternatively, enter command "file <filename>" if the puzzle resides in a text file (using same format).
""".format(blank_symbol)

"Read puzzle from stdin or file in a relatively free format"
"Produces vector of symbols "
puzzle = []
blank_lines = 0

raw = raw_input('> ')
re_match = re.match('^file\s+([\w\.]+).*', raw)
if re_match:
    file_name = re_match.group(1)
    saved_puzzle = open(file_name, "r")
    use_saved = True
else:
    "Save the puzzle for reuse or edit"
    saved_puzzle = open("puzzle.txt", "w")
    use_saved = False

while (True):
    if use_saved:
        raw = saved_puzzle.read()
        print raw
    else:
        raw = raw_input('> ')

    if raw == "":
        if not use_saved:
            saved_puzzle.write(raw + '\n')
        blank_lines += 1
    else:
        if not use_saved:
            saved_puzzle.write(raw + '\n')
        puzzle = puzzle + raw.split()
        blank_lines = 0

    if blank_lines == 2:
        saved_puzzle.close()
        break

pyd = Pydoku(puzzle)
pyd.print_board(pyd.puzzle_np)

"If any of the tests fail, print some diagnostic info and exit"
if pyd.test_ok:
    pyd.solve()
else:
    print "table {:s}".format(str(symbol_table))
    print "symbols used: {}".format(" ".join(used_symbols))
    print "symbols entered: {}".format(" ".join(puzzle))


for idx, soln in enumerate(pyd.solutions):
    print '\nSolution {}:'.format(idx+1)
    pyd.print_board(soln)

print '\n\nFound {} solutions:'.format(len(pyd.solutions))
