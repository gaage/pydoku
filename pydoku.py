#!/usr/local/bin/python
from copy import deepcopy
import numpy as np

class Pydoku(object):

    blank_symbol = '.'

    def __init__(self, puzzle_1d=[]):

        self.puzzle_1d = puzzle_1d
        self.used_symbols = set(self.puzzle_1d)
        self.puzzle_length = len(self.puzzle_1d)
        self.symbol_table = {0 : ''}

        symbol_key = 1
        for symbol in self.used_symbols:
            if symbol == Pydoku.blank_symbol:
                self.symbol_table[0] = symbol
            else:
                self.symbol_table[symbol_key] = symbol
                symbol_key += 1

        "Do checks"
        self.test_ok = True
        self.check_size()
        self.check_blank()
        self.check_symbols()

        "Create inverse dictionary for translation"
        self.inverse_symbol_table = {v: k for k, v in self.symbol_table.items()}

        "Translate puzzle to numbers to solve it with pydoku"
        num_puzzle = []

        for symbol in self.puzzle_1d:
            num_puzzle.append(self.inverse_symbol_table[symbol])

        # Generate structured puzzle as np array from vector
        self.puzzle_np = self.set_reshaped_np(num_puzzle)

        "Define some useful global constants"
        # Generate a separator string for pretty printing.
        self.separator = Separator(self).list
        # Generate an iterator array of 4-tuples for traversing board.
        self.iterator = Iterator(self).list
        # Generete the universal set for the given puzzle size
        self.universal = set(range(1, self.innersize + 1))

    def check_size(self):
        """
        Only certain sizes of board are defined and auto-detected
        Sets rows and columns of inner boxes
        """
        if self.puzzle_length == 256:
            self.rows = 4; self.cols = 4
        elif self.puzzle_length == 144:
            self.rows = 3; self.cols = 4
        elif self.puzzle_length == 81:
            self.rows = 3; self.cols = 3
        elif self.puzzle_length == 32:
            self.rows = 2; self.cols = 3
        elif self.puzzle_length == 16:
            self.rows = 2; self.cols = 2
        else:
            self.rows = 0; self.cols = 0
            print 'Size {} is not supported'.format(self.puzzle_length)
            self.test_ok = False
        self.innersize = self.rows * self.cols

    def check_blank(self):
        """
        Check if puzzle contains at least one blank symbol
        """
        if self.test_ok and not self.symbol_table[0]:
            print 'Puzzle must contain at least one blank symbol "{}"'.format(Pydoku.blank_symbol)
            self.test_ok = False

    def check_symbols(self):
        """
        Check if number of symbols matches puzzle length
        """
        found_no_of_symbols = len(self.symbol_table)-1
        if self.test_ok and (found_no_of_symbols != self.innersize):
            print 'Puzzle with size {} must contain {} symbols. Found {}'.format(puzzle_length, rows * cols, found_no_of_symbols)
            self.test_ok = False

    def set_reshaped_np(self, puzzle_num):
        """
        Convert the numerical puzzle to an np array, for convenient slicing in the solver algorithm
        :param puzzle_num: list of tokens, problem read line by line
        :return: 4D numpy array giving problem with logical coordinates (or, oc, ir, ic)
        """
        rows = self.rows
        cols = self.cols

        input_np = np.array(puzzle_num, dtype=np.int8).reshape(rows, cols, cols, rows)
        output_np = np.array(np.zeros((self.innersize) ** 2, dtype=np.int8)).reshape(rows, cols, cols, rows)
        for R in range(rows):
            for C in range(cols):
                for r in range(cols):
                    output_np[R, C, r] = input_np[R, r, C]
        return output_np

    def print_board(self, board):
        result = '\n'
        for index, itr in enumerate(self.iterator):
            value = self.symbol_table[int(board[itr])]
            if value == 0:
                value = '.'
            result += "{:2s}".format(str(value)) + self.separator[index]
        print result

    def get_solutions_at_square(self, R, C, r, c, puzzle):

        # Use slicing in the np array to conveniently construct the
        # sets of tokens already in use in a line, column or box
        row_set = set(puzzle[R, :, r, :].reshape(self.innersize))
        col_set = set(puzzle[:, C, :, c].reshape(self.innersize))
        box_set = set(puzzle[R, C, :, :].reshape(self.innersize))

        # Take the Union of the row, col and box set, remove the zero,
        union = row_set | col_set | box_set
        union.remove(0)

        # and subtract the union from the universal token set. This gives the
        # possible solutions for a square with the standard sudoku rules.
        copy_univ = deepcopy(self.universal)
        copy_univ.difference_update(union)
        return list(copy_univ)

    def solve(self):
        # List to be populated with solutions by recursive call
        self.solutions = []
        self.solve_recurse(self.puzzle_np)

    def solve_recurse(self, puzzle):
        """
        """
        all_assigned = True

        min_no_of_solutions = 999
        fewest_solutions = set([])

        # Loop through all squares of the puzzle argument, and determine the remaining one
        # with the least number of solutions. This will speed up the execution.
        for itr in self.iterator:
            if puzzle[itr] == 0:
                all_assigned = False
                solutions_at_this_square = self.get_solutions_at_square(*itr, puzzle=puzzle)
                no_of_solutions = len(solutions_at_this_square)

                if no_of_solutions < min_no_of_solutions:
                    min_no_of_solutions = no_of_solutions
                    fewest_solutions_square = itr
                    fewest_solutions = solutions_at_this_square

        if all_assigned:
            self.solutions.append(puzzle)
        else:
            # Test all the solutions at the square with fewest solutions
            for hypothesis in fewest_solutions:
                # Create a new board with the hypotesis included
                try_it_out = deepcopy(puzzle)
                try_it_out[fewest_solutions_square] = hypothesis

                # Run algorithm on this board
                self.solve_recurse(try_it_out)


class Separator(object):

    def __init__(self, pydoku):
        """
        Separator for pretty-print
        :return: list of characters, length is number of elements in the problem
        """
        self.list = []
        for R in range(pydoku.cols):
            for r in range(pydoku.rows):
                for C in range(pydoku.rows):
                    for c in range(pydoku.cols):
                        self.list.append(' ')
                    # The following 3 statements adds to the contents field
                    # of the latest contents array that were appended
                    self.list[-1] += ' '
                self.list[-1] += '\n'
            self.list[-1] += '\n'


class Iterator(object):

    def __init__(self, pydoku):
        """
        Standard iterator for traversing the array linearly
        :return: list of 4-element tuples, length is number of elements in the problem
        """
        self.list = []
        for R in range(pydoku.cols):
            for r in range(pydoku.rows):
                for C in range(pydoku.rows):
                    for c in range(pydoku.cols):
                        self.list += [(R, C, r, c)]

