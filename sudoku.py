from numpy import array, zeros_like
import random
from collections import deque
from copy import deepcopy


class Coord:
    def __init__(self, r, c):
        self.row = r
        self.col = c


NB_OPS = 60
SQUARE_SIZE = 3
SUDOKU_SIZE = 9
EMPTY_TILES = 45

grid = array([
        [1, 2, 3, 4, 5, 6, 7, 8, 9],
        [4, 5, 6, 7, 8, 9, 1, 2, 3],
        [7, 8, 9, 1, 2, 3, 4, 5, 6],
        [2, 3, 4, 5, 6, 7, 8, 9, 1],
        [5, 6, 7, 8, 9, 1, 2, 3, 4],
        [8, 9, 1, 2, 3, 4, 5, 6, 7],
        [3, 4, 5, 6, 7, 8, 9, 1, 2],
        [6, 7, 8, 9, 1, 2, 3, 4, 5],
        [9, 1, 2, 3, 4, 5, 6, 7, 8]
    ])


def swap(c1, c2):
    temp = grid[c1.row][c1.col]
    grid[c1.row][c1.col] = grid[c2.row][c2.col]
    grid[c2.row][c2.col] = temp


def swapRows(r1, r2):
    for i in range(SUDOKU_SIZE):
        swap(Coord(r1, i), Coord(r2, i))


def swapCols(c1, c2):
    for i in range(SUDOKU_SIZE):
        swap(Coord(i, c1), Coord(i, c2))


def flipHorizontally():
    nb_flip = int(SUDOKU_SIZE / 2)
    for i in range(nb_flip):
        swapRows(i, SUDOKU_SIZE - i - 1)


def flipVertically():
    nb_flip = int(SUDOKU_SIZE / 2)
    for i in range(nb_flip):
        swapCols(i, SUDOKU_SIZE - i - 1)


def flipBackwardDiagonal():
    for row in range(SUDOKU_SIZE):
        col = row + 1
        while col < SUDOKU_SIZE:
            swap(Coord(row, col), Coord(col, row))
            col = col + 1


def flipForwardDiagonal():
    for col in range(SUDOKU_SIZE):
        for row in range(SUDOKU_SIZE - 1 - col):
            swap(Coord(row, col), Coord(SUDOKU_SIZE - 1 - col, SUDOKU_SIZE - 1 - row))


FLIP_OPS = [flipForwardDiagonal, flipBackwardDiagonal, flipHorizontally, flipVertically]
SWAP_OPS = [swapRows, swapCols]
OP_COUNT = len(FLIP_OPS) + len(SWAP_OPS)


def rowsAndColsAreValid(grid):
    rowSet = set()
    colSet = set()

    for i in range(9):
        for j in range(9):
            rowSet.add(grid[i][j])
            colSet.add(grid[j][i])

        if len(rowSet) != SUDOKU_SIZE or len(colSet) != SUDOKU_SIZE:
            return False
        else:
            rowSet.clear()
            colSet.clear()

    return True


def squaresAreValid(grid):
    squareSet = set()

    # For each square
    for squareRow in range(0, 7, 3):
        for squareColumn in range(0, 7, 3):

            # For each 9 numbers in small square
            for row in range(squareRow, squareRow + 3):
                for column in range(squareColumn, squareColumn + 3):
                    squareSet.add(grid[row][column])

            if len(squareSet) != 9:
                #                 print("Square ({},{}) is wrong!".format(squareRow, squareColumn))
                #                 print(squareSet)
                return False
            else:
                squareSet.clear()

    return True


def isValid(grid):
    return rowsAndColsAreValid(grid) and squaresAreValid(grid)


def generateRandomIndexes():
    # generate indexes (row, col) between 0 to 8
    square_index = random.randint(0, 2)
    first_index = SQUARE_SIZE * square_index + random.randint(0, 2)
    second_index = (SQUARE_SIZE * square_index + (first_index + random.randint(0, 2))) % SUDOKU_SIZE
    return first_index, second_index


def randomizeOneStep():
    index = random.randint(0, OP_COUNT - 1)
    if index <= 3:
        FLIP_OPS[index]()
    else:  # index >= 4
        random_index = generateRandomIndexes()
        SWAP_OPS[index - 4](random_index[0], random_index[1])


def randomizeSudoku():
    for i in range(NB_OPS):
        randomizeOneStep()

    while not isValid(grid):
        randomizeOneStep()

    return grid

# SOLVER

def validateRow(sudoku, entry, row):
    for i in sudoku[row]:
        if i == entry:
            return False

    return True


def validateColumn(sudoku, entry, col):
    for i in sudoku[:, col]:
        if i == entry:
            return False

    return True


def validateSquare(sudoku, entry, row, col):
    squareRow = int(row / SQUARE_SIZE) * SQUARE_SIZE
    squareColumn = int(col / SQUARE_SIZE) * SQUARE_SIZE

    # For 9 numbers in small square
    for row in range(squareRow, squareRow + 3):
        for column in range(squareColumn, squareColumn + 3):
            if sudoku[row][column] == entry:
                return False
    return True


def valueIsLegal(sudoku, entry, row, column):
    return validateRow(sudoku, entry, row) and validateColumn(sudoku, entry, column) and validateSquare(sudoku, entry, row, column)


def getZeroIndexes(sudoku):
    zeroIndexes = []
    for row in range(SUDOKU_SIZE):
        for column in range(SUDOKU_SIZE):
            if sudoku[row][column] == 0:
                zeroIndexes.append((row, column))
    return deque(zeroIndexes)




def solveSudoku(sudoku, zeroIndexes, grid):
    if len(zeroIndexes) == 0:
        return isValid(sudoku)

    currentIndex = zeroIndexes.popleft()
    row = currentIndex[0]
    col = currentIndex[1]

    for entry in range(1, SUDOKU_SIZE + 1):
        if valueIsLegal(sudoku, entry, row, col):
            sudoku[row][col] = entry
            grid[row][col] = entry
            indexCopy = deepcopy(zeroIndexes)

            if solveSudoku(sudoku, indexCopy, grid):
                return True

    sudoku[row][col] = 0
    return False


def isSolvable(sudoku):
    zeros = getZeroIndexes(sudoku)
    input_grid = zeros_like(sudoku)
    return solveSudoku(sudoku, zeros, input_grid)


def tileCanBeRemoved(sudoku, row, col):
    oldValue = sudoku[row][col]
    for i in range(1, SUDOKU_SIZE + 1):
        if i != oldValue:
            copy = deepcopy(sudoku)
            copy[row][col] = i

            if isSolvable(copy):
                return False

    return True


def generateSudoku(sudoku_grid):
    grid = deepcopy(sudoku_grid)
    # (0, 0) => (8, 8)
    possibleIndexes = []
    for i in range(SUDOKU_SIZE):
        for j in range(SUDOKU_SIZE):
            possibleIndexes.append((i, j))

    tilesToRemove = EMPTY_TILES

    while (tilesToRemove > 0):
        # 1. Get a random index in possibleIndexes
        index = random.randint(0, len(possibleIndexes) - 1)
        indexes = possibleIndexes[index]
        row = indexes[0]
        col = indexes[1]
        # oldValue = grid[row][col]

        if grid[row][col] != 0 and tileCanBeRemoved(grid, row, col):
            grid[row][col] = 0
            tilesToRemove -= 1
            possibleIndexes.remove(indexes)
            # print("Removed ({}, {}) = {}, remaining tiles: {}".format(row, col, oldValue, tilesToRemove))

    return grid


# if __name__ == '__main__':
#     sudoku = randomizeSudoku()
#     print(sudoku, '\n')
#     print(generateSudoku(sudoku))
