from __future__ import print_function

import dimod
import math
import sys

from dimod.generators.constraints import combinations
from hybrid.reference import KerberosSampler



def get_label(row, col, digit):
    """Returns a string of the cell coordinates and the cell value in a
    standard format.
    """
    return "{row},{col}_{digit}".format(**locals())


def get_matrix(filename):
    """Return a list of lists containing the content of the input text file.
    Note: each line of the text file corresponds to a list. Each item in
    the list is from splitting the line of text by the whitespace ' '.
    """
    with open(filename, "r") as f:
        content = f.readlines()

    lines = []
    for line in content:
        new_line = line.rstrip()    # Strip any whitespace after last value

        if new_line:
            new_line = list(map(int, new_line.split(' ')))
            lines.append(new_line)

    return lines


def is_correct(matrix):
    """Verify that the matrix satisfies the Sudoku constraints.
    Args:
      matrix(list of lists): list contains 'n' lists, where each of the 'n'
        lists contains 'n' digits. 
    """
    n = len(matrix)        # Number of rows/columns
    m = int(math.sqrt(n))  # Number of subsquare rows/columns
    unique_digits = set(range(1, n+1))  # Digits in a solution

    # Verifying rows
    for row in matrix:
        if set(row) != unique_digits:
            print("Error in row: ", row)
            return False

    # Verifying columns
    for j in range(n):
        col = [matrix[i][j] for i in range(n)]
        if set(col) != unique_digits:
            print("Error in col: ", col)
            return False

    # Verifying subsquares
    subsquare_coords = [(i, j) for i in range(m) for j in range(m)]
    for r_scalar in range(m):
        for c_scalar in range(m):
            subsquare = [matrix[i + r_scalar * m][j + c_scalar * m] for i, j
                         in subsquare_coords]
            if set(subsquare) != unique_digits:
                print("Error in sub-square: ", subsquare)
                return False

    return True


def main():
    iterasyon=1
    while 1:
        # Note: for the purposes of a code example, main() is written as a script 

        # Read user input
        if len(sys.argv) > 1:
            filename = sys.argv[1]
        else:
            filename = "problem.txt"
            print("Warning: using default problem file, '{}'. Usage: python "
                "{} <sudoku filepath>".format(filename, sys.argv[0]))

        # Read sudoku problem
        matrix = get_matrix(filename)

        # Set up
        n = len(matrix)          # Number of rows/columns in sudoku
        m = int(math.sqrt(n))    # Number of rows/columns in sudoku subsquare
        digits = range(1, n+1)

        bqm = dimod.BinaryQuadraticModel({}, {}, 0.0, dimod.SPIN)

        # Constraint: Each node can only select one digit
        for row in range(n):
            for col in range(n):
                node_digits = [get_label(row, col, digit) for digit in digits]
                one_digit_bqm = combinations(node_digits, 1)
                bqm.update(one_digit_bqm)

        # Constraint: Each row of nodes cannot have duplicate digits
        for row in range(n):
            for digit in digits:
                row_nodes = [get_label(row, col, digit) for col in range(n)]
                row_bqm = combinations(row_nodes, 1)
                bqm.update(row_bqm)

        # Constraint: Each column of nodes cannot have duplicate digits
        for col in range(n):
            for digit in digits:
                col_nodes = [get_label(row, col, digit) for row in range(n)]
                col_bqm = combinations(col_nodes, 1)
                bqm.update(col_bqm)

        # Constraint: Each sub-square cannot have duplicates
        # Build indices of a basic subsquare
        subsquare_indices = [(row, col) for row in range(3) for col in range(3)]

        # Build full sudoku array
        for r_scalar in range(m):
            for c_scalar in range(m):
                for digit in digits:
                    # Shifts for moving subsquare inside sudoku matrix
                    row_shift = r_scalar * m
                    col_shift = c_scalar * m

                    # Build the labels for a subsquare
                    subsquare = [get_label(row + row_shift, col + col_shift, digit)
                                for row, col in subsquare_indices]
                    subsquare_bqm = combinations(subsquare, 1)
                    bqm.update(subsquare_bqm)
                    

        # Constraint: Fix known values
        for row, line in enumerate(matrix):
            for col, value in enumerate(line):
                if value > 0:
                    # Recall that in the "Each node can only select one digit"
                    # constraint, for a given cell at row r and column c, we
                    # produced 'n' labels. Namely,
                    # ["r,c_1", "r,c_2", ..., "r,c_(n-1)", "r,c_n"]
                    #
                    # Due to this same constraint, we can only select one of these
                    # 'n' labels (achieved by 'generators.combinations(..)').
                    #
                    # The 1 below indicates that we are selecting the label
                    # produced by 'get_label(row, col, value)'. All other labels
                    # with the same 'row' and 'col' will be discouraged from being
                    # selected.
                    bqm.fix_variable(get_label(row, col, value), 1)

        # Solve BQM
        solution = KerberosSampler().sample(bqm, max_iter=10, convergence=3)

        best_solution = solution.first.sample

        # Print solution
        solution_list = [k for k, v in best_solution.items() if v == 1]
        
        for label in solution_list:
            coord, digit = label.split('_')
            row, col = map(int, coord.split(','))
            matrix[row][col] = int(digit)

        for line in matrix:
            print(*line, sep=" ")   # Print list without commas or brackets

        # Verify
        if is_correct(matrix):
            print("The solution is correct iterasyon= ",iterasyon)            
            f = open("correctFile.txt", "a")
            for line in matrix:
                xiter=matrix
            if iterasyon==1:
                f.write('Yeni Döngü\n')
                
            f.write('iterasyon=%d'%iterasyon)    
            f.write('->%s\n' %xiter)
            iterasyon=iterasyon+1
            if iterasyon==50:
                break
        else:
            print("The solution is incorrect iterasyon= ",iterasyon)
            f = open("falseFile.txt", "a")
            for line in matrix:
                xiter2=matrix
            if iterasyon==1:
                f.write('Yeni Döngü\n')
            f.write('iterasyon=%d'%iterasyon)
            f.write('->%s\n' %xiter2)
            iterasyon=iterasyon+1
            if iterasyon==50:
                break
            else:
                continue
        
    


if __name__ == "__main__":
    main()