from __future__ import generators
from scipy.spatial import ConvexHull, convex_hull_plot_2d

import math
import time

from which_pyqt import PYQT_VER

if PYQT_VER == 'PYQT5':
    from PyQt5.QtCore import QLineF, QPointF, QObject
else:
    raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

# Some global color constants that might be useful
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 0.25


#
# This is the class you have to complete.
#


class ConvexHullSolver(QObject):

    # Class constructor
    def __init__(self):
        super().__init__()
        self.pause = False

    # Some helper methods that make calls to the GUI, allowing us to send updates
    # to be displayed.

    def showTangent(self, line, color):
        self.view.addLines(line, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseTangent(self, line):
        self.view.clearLines(line)

    def blinkTangent(self, line, color):
        self.showTangent(line, color)
        self.eraseTangent(line)

    def showHull(self, polygon, color):
        self.view.addLines(polygon, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseHull(self, polygon):
        self.view.clearLines(polygon)

    def showText(self, text):
        self.view.displayStatusText(text)

    # This is the method that gets called by the GUI and actually executes
    # the finding of the hull
    def compute_hull(self, points, pause, view):
        self.pause = pause
        self.view = view
        assert (type(points) == list and type(points[0]) == QPointF)

        t1 = time.time()
        # TODO: SORT THE POINTS BY INCREASING X-VALUE
        points = sorted(points, key=lambda point: point.x(), reverse=False)
        t2 = time.time()

        t3 = time.time()
        # this is a dummy polygon of the first 3 unsorted points
        polygon = make_poly(self.solve_hull(points))
        # TODO: REPLACE THE LINE ABOVE WITH A CALL TO YOUR DIVIDE-AND-CONQUER CONVEX HULL SOLVER
        t4 = time.time()

        # when passing lines to the display, pass a list of QLineF objects.  Each QLineF
        # object can be created with two QPointF objects corresponding to the endpoints
        self.showHull(polygon, RED)
        self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4 - t3))

    def solve_hull(self, points):  # n log n time and space complexity

        if len(points) > 3:
            m = math.floor(len(points) / 2)
            leftHalf = points[:m]
            rightHalf = points[m:]
            leftHull = self.solve_hull(leftHalf)
            rightHull = self.solve_hull(rightHalf)
            upperTan = find_upper_tangent(leftHull, rightHull)  # n time
            lowerTan = find_lower_tangent(leftHull, rightHull)  # n time
            hull = merge(leftHull, rightHull, upperTan, lowerTan)  # n time
            return hull
        else:
            hull = make_hull(points)
            return hull


def find_slope(point1, point2):
    slope = (point2.y() - point1.y()) / (point2.x() - point1.x())
    return slope


def make_poly(hull):
    polygon = [QLineF(hull[i], hull[(i + 1) % len(hull)]) for i in range(len(hull))]
    return polygon


def make_hull(points):
    if len(points) == 3:
        hull = [0, 0, 0]
        hull[0] = points[0]
        slopeA = find_slope(points[0], points[1])
        slopeB = find_slope(points[0], points[2])
        if slopeA > slopeB:
            hull[1] = points[1]
            hull[2] = points[2]
        else:
            hull[1] = points[2]
            hull[2] = points[1]
        return hull

    return points


def find_upper_tangent(leftHull, rightHull):
    rightMostIndex = find_right_most(leftHull)
    leftMostIndex = find_left_most(rightHull)
    currentIndexLeft = rightMostIndex
    currentIndexRight = leftMostIndex
    previousLeftHullIndex = rightMostIndex
    previousRightHullIndex = leftMostIndex
    isTopForLeft = False
    isTopForRight = False
    currentSlope = find_slope(leftHull[rightMostIndex], rightHull[leftMostIndex])
    while not isTopForLeft or not isTopForRight:  # n time
        while not isTopForLeft:
            if currentIndexLeft == 0:
                currentIndexLeft = len(leftHull) - 1
            else:
                currentIndexLeft = currentIndexLeft - 1

            tempSlope = find_slope(leftHull[currentIndexLeft], rightHull[currentIndexRight])
            if tempSlope < currentSlope:
                currentSlope = tempSlope
                previousLeftHullIndex = currentIndexLeft
                isTopForLeft = False
                isTopForRight = False
            else:
                currentIndexLeft = previousLeftHullIndex
                isTopForLeft = True

        while not isTopForRight:
            if currentIndexRight == len(rightHull) - 1:
                currentIndexRight = 0
            else:
                currentIndexRight = currentIndexRight + 1

            tempSlope = find_slope(leftHull[currentIndexLeft], rightHull[currentIndexRight])

            if tempSlope > currentSlope:
                previousRightHullIndex = currentIndexRight
                currentSlope = tempSlope
                isTopForLeft = False
                isTopForRight = False
            else:
                currentIndexRight = previousRightHullIndex
                isTopForRight = True

    return [leftHull[currentIndexLeft], rightHull[currentIndexRight]]


def find_lower_tangent(leftHull, rightHull):
    rightMostIndex = find_right_most(leftHull)
    leftMostIndex = find_left_most(rightHull)
    currentIndexLeft = rightMostIndex
    currentIndexRight = leftMostIndex
    previousLeftHullIndex = rightMostIndex
    previousRightHullIndex = leftMostIndex
    isBotForLeft = False
    isBotForRight = False
    currentSlope = find_slope(leftHull[rightMostIndex], rightHull[leftMostIndex])
    while not isBotForLeft or not isBotForRight:
        while not isBotForLeft:
            if currentIndexLeft == len(leftHull) - 1:
                currentIndexLeft = 0
            else:
                currentIndexLeft = currentIndexLeft + 1

            tempSlope = find_slope(leftHull[currentIndexLeft], rightHull[currentIndexRight])
            if tempSlope > currentSlope:
                currentSlope = tempSlope
                previousLeftHullIndex = currentIndexLeft
                isBotForLeft = False
                isBotForRight = False
            else:
                currentIndexLeft = previousLeftHullIndex
                isBotForLeft = True

        while not isBotForRight:
            if currentIndexRight == 0:
                currentIndexRight = len(rightHull) - 1
            else:
                currentIndexRight = currentIndexRight - 1

            tempSlope = find_slope(leftHull[currentIndexLeft], rightHull[currentIndexRight])

            if tempSlope < currentSlope:
                previousRightHullIndex = currentIndexRight
                currentSlope = tempSlope
                isBotForRight = False
                isBotForLeft = False
            else:
                currentIndexRight = previousRightHullIndex
                isBotForRight = True

    return [leftHull[currentIndexLeft], rightHull[currentIndexRight]]


def find_right_most(polygon):
    rightMost = -1.5
    rightMostIndex = -1
    for i in range(len(polygon)):
        if polygon[i].x() > rightMost:
            rightMost = polygon[i].x()
            rightMostIndex = i
    return rightMostIndex


def find_left_most(polygon):
    leftMost = 1.5
    leftMostIndex = -1
    for i in range(len(polygon)):
        if polygon[i].x() < leftMost:
            leftMost = polygon[i].x()
            leftMostIndex = i
    return leftMostIndex


def merge(leftHull, rightHull, upperTan, lowerTan):
    mergedHull = []
    foundTopRight = False
    TopRightIndex = 0
    while not foundTopRight:
        if rightHull[TopRightIndex] == upperTan[1]:
            foundTopRight = True
        else:
            TopRightIndex = TopRightIndex + 1

    foundBottomRight = False
    BotRightIndex = 0
    while not foundBottomRight:
        if rightHull[BotRightIndex] == lowerTan[1]:
            foundBottomRight = True
        else:
            BotRightIndex = BotRightIndex + 1

    foundTopLeft = False
    TopLeftIndex = 0
    while not foundTopLeft:
        if leftHull[TopLeftIndex] == upperTan[0]:
            foundTopLeft = True
        else:
            TopLeftIndex = TopLeftIndex + 1

    foundBottomLeft = False
    BotLeftIndex = 0
    while not foundBottomLeft:
        if leftHull[BotLeftIndex] == lowerTan[0]:
            foundBottomLeft = True
        else:
            BotLeftIndex = BotLeftIndex + 1

    while TopRightIndex != BotRightIndex:
        mergedHull.append(rightHull[TopRightIndex])
        if TopRightIndex == len(rightHull) - 1:
            TopRightIndex = 0
        else:
            TopRightIndex = TopRightIndex + 1

    mergedHull.append(rightHull[BotRightIndex])

    while BotLeftIndex != TopLeftIndex:
        mergedHull.append(leftHull[BotLeftIndex])
        if BotLeftIndex == len(leftHull) - 1:
            BotLeftIndex = 0
        else:
            BotLeftIndex = BotLeftIndex + 1

    mergedHull.append(leftHull[TopLeftIndex])
    return mergedHull
