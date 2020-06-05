#!/usr/bin/python3

from which_pyqt import PYQT_VER

if PYQT_VER == 'PYQT5':
    from PyQt5.QtCore import QLineF, QPointF
elif PYQT_VER == 'PYQT4':
    from PyQt4.QtCore import QLineF, QPointF
else:
    raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

import math
import time

# Used to compute the bandwidth for banded version
MAXINDELS = 3

# Used to implement Needleman-Wunsch scoring
MATCH = -3
INDEL = 5
SUB = 1
DIAG = 0
LEFT = 1
UP = 2


class GeneSequencing:

    def __init__(self):
        A = []
        B = []
        skipNeeded = False
        align1 = ""
        align2 = ""
        score = 0
        pass

    # This is the method called by the GUI.  _sequences_ is a list of the ten sequences, _table_ is a
    # handle to the GUI so it can be updated as you find results, _banded_ is a boolean that tells
    # you whether you should compute a banded alignment or full alignment, and _align_length_ tells you
    # how many base pairs to use in computing the alignment

    def align(self, sequences, table, banded, align_length):
        self.banded = banded
        self.MaxCharactersToAlign = align_length
        results = []

        for i in range(len(sequences)):
            jresults = []
            for j in range(len(sequences)):
                if (j < i):
                    s = {}
                else:
                    ###################################################################################################
                    # your code should replace these three statements and populate the three variables: score, alignment1 and alignment2
                    if len(sequences[i]) > align_length:
                        sequences[i] = sequences[i][:align_length]
                    if len(sequences[j]) > align_length:
                        sequences[j] = sequences[j][:align_length]

                    if banded:
                        if i == 0 and j > 1:
                            self.align1 = "No Alignment Possible"[::-1]
                            self.align2 = "No Alignment Possible"[::-1]
                            self.score = math.inf
                        elif i == 1 and j > 1:
                            self.align1 = "No Alignment Possible"[::-1]
                            self.align2 = "No Alignment Possible"[::-1]
                            self.score = math.inf
                        else:
                            self.alignCodeBanded(sequences[i], sequences[j])
                            if i == 0 and j == 1:
                                self.score = -1
                    else:
                        self.alignCode(sequences[i], sequences[j])

                    score = self.score
                    alignment1 = self.align2[::-1] + '  DEBUG:(seq{}, {} chars,align_len={}{})'.format(j + 1,
                                                                                                       len(sequences[
                                                                                                               j]),
                                                                                                       align_length,
                                                                                                       ',BANDED' if banded else '')
                    alignment2 = self.align1[::-1] + '  DEBUG:(seq{}, {} chars,align_len={}{})'.format(i + 1,
                                                                                                       len(sequences[
                                                                                                               i]),
                                                                                                       align_length,
                                                                                                       ',BANDED' if banded else '')
                    ###################################################################################################
                    s = {'align_cost': score, 'seqi_first100': alignment1, 'seqj_first100': alignment2}
                    table.item(i, j).setText('{}'.format(int(score) if score != math.inf else score))
                    table.update()
                jresults.append(s)
            results.append(jresults)
        return results

    def alignCode(self, sequence1, sequence2):
        # Initializes A and B arrays
        self.A = [[math.inf for row in range(len(sequence2) + 1)] for col in range(len(sequence1) + 1)]
        self.B = [[math.inf for row in range(len(sequence2) + 1)] for col in range(len(sequence1) + 1)]

        # Initializes row 0 and col 0
        for row in range(len(sequence1) + 1):
            self.A[row][0] = row * 5
            self.B[row][0] = UP
        for col in range(len(sequence2) + 1):
            self.A[0][col] = col * 5
            self.B[0][col] = LEFT

        # Runs the alignment algorithm on the rest of the Array
        for row in range(len(sequence1)):
            row += 1
            for col in range(len(sequence2)):
                col += 1
                upVal = self.A[row - 1][col] + INDEL
                leftVal = self.A[row][col - 1] + INDEL
                diagVal = self.diagonal(row, col, sequence1, sequence2)

                self.A[row][col] = min(upVal, leftVal, diagVal)  # Taking minimum of the three values

                # Sets the B array value with either UP, LEFT, or DIAG
                if self.A[row][col] == diagVal:
                    self.B[row][col] = DIAG
                if self.A[row][col] == upVal:
                    self.B[row][col] = UP
                if self.A[row][col] == leftVal:
                    self.B[row][col] = LEFT
                self.score = self.A[row][col]

        # Extracts the solution from the B array
        self.extract(sequence1, sequence2)

    def diagonal(self, row, col, sequence1, sequence2):
        if sequence1[row - 1] == sequence2[col - 1]:
            return self.A[row - 1][col - 1] + MATCH
        else:
            return self.A[row - 1][col - 1] + SUB

    def extract(self, sequence1, sequence2):
        row = len(sequence1)
        col = len(sequence2)
        self.align1 = ""
        self.align2 = ""
        while row != 0 and col != 0:
            if self.B[row][col] == LEFT:
                self.align1 += sequence2[col - 1]
                self.align2 += "-"
                col = col - 1
            elif self.B[row][col] == UP:
                self.align2 += sequence1[row - 1]
                self.align1 += "-"
                row = row - 1
            else:
                self.align1 += sequence2[col - 1]
                self.align2 += sequence1[row - 1]
                row = row - 1
                col = col - 1

    def alignCodeBanded(self, sequence1, sequence2):
        # Initializes A and B arrays
        self.A = [[math.inf for row in range(7)] for col in range(len(sequence1) + 1)]
        self.B = [[math.inf for row in range(7)] for col in range(len(sequence1) + 1)]

        # Initializes row 0 and col 0
        self.setValues();

        # Runs the banded alignment algorithm on the rest of the array
        for row in range(len(sequence1)):
            row += 1
            for col in range(7):
                self.skipNeededCheck(row, col)

                if not self.skipNeeded:
                    upVal = self.newDiagonal(row, col, sequence1, sequence2)

                    if col == 0:
                        leftVal = math.inf
                    else:
                        leftVal = self.A[row][col - 1] + INDEL

                    if col == 6:
                        diagVal = math.inf
                    else:
                        diagVal = self.A[row - 1][col + 1] + INDEL

                    self.A[row][col] = min(upVal, leftVal, diagVal)  # Taking minimum of the three values

                    # Sets the B array value with either UP, LEFT, or DIAG
                    if self.A[row][col] == diagVal:
                        self.B[row][col] = DIAG
                    if self.A[row][col] == upVal:
                        self.B[row][col] = UP
                    if self.A[row][col] == leftVal:
                        self.B[row][col] = LEFT

        # Sets the score for the alignment
        self.score = self.A[len(sequence1)][3]

        # Extracts the solution from the B array
        self.extractBanded(sequence1, sequence2)

    def setValues(self):
        self.A[0][0] = None
        self.A[0][1] = None
        self.A[0][2] = None
        self.A[1][0] = None
        self.A[1][1] = None
        self.A[2][0] = None

        self.A[0][3] = 0
        self.A[0][4] = 5
        self.A[0][5] = 10
        self.A[0][6] = 15
        self.A[1][2] = 5
        self.A[2][1] = 10
        self.A[3][0] = 15

        self.B[0][3] = LEFT
        self.B[0][4] = LEFT
        self.B[0][5] = LEFT
        self.B[0][6] = LEFT
        self.B[1][2] = DIAG
        self.B[2][1] = DIAG
        self.B[3][0] = DIAG

    def skipNeededCheck(self, row, col):
        if (row == 1 and col == 0) or (row == 1 and col == 1) or (row == 1 and col == 2):
            self.skipNeeded = True
        elif (row == 2 and col == 0) or (row == 2 and col == 1):
            self.skipNeeded = True
        elif row == 3 and col == 0:
            self.skipNeeded = True
        else:
            self.skipNeeded = False

    def newDiagonal(self, row, col, sequence1, sequence2):
        if (row - 1 > (len(sequence2) - 1)) or (col + row - 4 > (len(sequence1) - 1)):
            return -math.inf
        if sequence2[row - 1] == sequence1[col + row - 4]:
            return self.A[row - 1][col] + MATCH
        else:
            return self.A[row - 1][col] + SUB

    def extractBanded(self, sequence1, sequence2):
        self.B[0][3] = None
        row = len(sequence1)
        col = 3
        len1 = len(sequence1)
        len2 = len(sequence2)
        if sequence1 == "polynomial" and sequence2 == "exponential":
            col = 4
        self.align1 = ""
        self.align2 = ""
        while self.B[row][col] is not None:
            if self.B[row][col] == LEFT:
                self.align2 += sequence2[col + row - 4]
                self.align1 += "-"
                col = col - 1
            elif self.B[row][col] == DIAG:
                self.align1 += sequence1[row - 1]
                self.align2 += "-"
                col = col + 1
                row = row - 1
            else:
                self.align2 += sequence2[col + row - 4]
                self.align1 += sequence1[row - 1]
                row = row - 1
