#!/usr/bin/python3

from which_pyqt import PYQT_VER

if PYQT_VER == 'PYQT5':
    from PyQt5.QtCore import QLineF, QPointF
elif PYQT_VER == 'PYQT4':
    from PyQt4.QtCore import QLineF, QPointF
else:
    raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

import time
import numpy as np
from TSPClasses import *
import math
import heapq
import itertools


class TSPSolver:
    def __init__(self, gui_view):
        self._scenario = None

    def setupWithScenario(self, scenario):
        self._scenario = scenario

    ''' <summary>
        This is the entry point for the default solver
        which just finds a valid random tour.  Note this could be used to find your
        initial BSSF.
        </summary>
        <returns>results dictionary for GUI that contains three ints: cost of solution, 
        time spent to find solution, number of permutations tried during search, the 
        solution found, and three null values for fields not used for this 
        algorithm</returns> 
    '''

    def defaultRandomTour(self, time_allowance=60.0):
        results = {}
        cities = self._scenario.getCities()
        ncities = len(cities)
        foundTour = False
        count = 0
        bssf = None
        start_time = time.time()
        while not foundTour and time.time() - start_time < time_allowance:
            # create a random permutation
            perm = np.random.permutation(ncities)
            route = []
            # Now build the route using the random permutation
            for i in range(ncities):
                route.append(cities[perm[i]])
            bssf = TSPSolution(route)
            count += 1
            if bssf.cost < np.inf:
                # Found a valid route
                foundTour = True
        end_time = time.time()
        results['cost'] = bssf.cost if foundTour else math.inf
        results['time'] = end_time - start_time
        results['count'] = count
        results['soln'] = bssf
        results['max'] = None
        results['total'] = None
        results['pruned'] = None
        return results

    ''' <summary>
        This is the entry point for the greedy solver, which you must implement for 
        the group project (but it is probably a good idea to just do it for the branch-and
        bound project as a way to get your feet wet).  Note this could be used to find your
        initial BSSF.
        </summary>
        <returns>results dictionary for GUI that contains three ints: cost of best solution, 
        time spent to find best solution, total number of solutions found, the best
        solution found, and three null values for fields not used for this 
        algorithm</returns> 
    '''

    def greedy(self, time_allowance=60.0):
        pass

    ''' <summary>
        This is the entry point for the branch-and-bound algorithm that you will implement
        </summary>
        <returns>results dictionary for GUI that contains three ints: cost of best solution, 
        time spent to find best solution, total number solutions found during search (does
        not include the initial BSSF), the best solution found, and three more ints: 
        max queue size, total number of states created, and number of pruned states.</returns> 
    '''

    def branchAndBound(self, time_allowance=60.0):
        results = {}
        start_time = time.time()

        BSSF = self.defaultRandomTour(start_time)['cost']
        cities = self._scenario.getCities()
        ncities = len(cities)
        foundTour = False
        count = 0

        initialMatrix = self.initializeMatrix(cities)  # Sets the initial cost matrix
        reducedMatrix = self.reduceMatrix(initialMatrix)  # Reduces the initial cost matrix

        priorityQ = []
        maxStates = 0
        totalStates = 0
        prunedStates = 0

        for i in range(len(cities)):
            startCity = [i]
            firstNode = Node(reducedMatrix[1], reducedMatrix[0], startCity, 1)
            totalStates += 1
            heapq.heappush(priorityQ, (firstNode.getPriority(), i, firstNode))  # Puts the initial node in priorityQ

        maxStates = len(priorityQ)

        while priorityQ:  # While loop until the priorityQ is empty
            if time.time() - start_time > time_allowance:
                break
            keyValue = heapq.heappop(priorityQ)  # Pops the best value tuple in the priorityQ
            parentNode = keyValue[2]  # Takes the node out of the best value tuple
            if parentNode._lowerBound >= BSSF:
                prunedStates += 1
                continue

            citiesToVisit = parentNode.getCitiesToVisit()

            for i in range(len(citiesToVisit)):
                if time.time() - start_time > time_allowance:
                    break
                if citiesToVisit[i] == parentNode.getStartCity():
                    continue

                currentMatrix = np.copy(parentNode.getMatrix())
                currLB = parentNode._lowerBound
                currPath = parentNode._path[:]
                currPath.append(citiesToVisit[i])
                currDepth = parentNode._depth

                childNode = Node(currLB, None, currPath, currDepth + 1)  # Creates the new child node
                totalStates += 1

                childNode.calculateMatrix(currentMatrix, currLB, citiesToVisit[i], BSSF)  # Calculates the matrix

                if childNode._lowerBound <= BSSF:  # Prunes or adds to priorityQ
                    if len(childNode._path) == len(cities) and childNode.connectsCity():
                        foundTour = True
                        count += 1
                        BSSF = childNode._lowerBound
                        BPSF = childNode._path[:]

                    else:
                        heapq.heappush(priorityQ, (childNode.getPriority(), i, childNode))
                        if len(priorityQ) > maxStates:
                            maxStates = len(priorityQ)
                else:
                    prunedStates += 1

        if not foundTour:
            results['cost'] = float("inf")
            results['time'] = time.time() - start_time
            results['count'] = count
            results['soln'] = TSPSolution(cities)

            return results

        route = []

        for i in range(ncities):
            route.append(cities[BPSF[i]])

        finalSolution = TSPSolution(route)

        results['cost'] = finalSolution.cost
        results['time'] = time.time() - start_time
        results['count'] = count
        results['soln'] = finalSolution
        results['max'] = maxStates
        results['total'] = totalStates
        results['pruned'] = prunedStates

        return results

    def initializeMatrix(self, cities):
        a = np.empty((len(cities), len(cities)))
        np.fill_diagonal(a, math.inf)

        for i in range(len(cities)):
            for j in range(len(cities)):
                if i != j:
                    a[i, j] = cities[i].costTo(cities[j])

        return a

    def reduceMatrix(self, initialMatrix):
        length = len(initialMatrix[0])
        cost = 0
        for i in range(0, length):
            minVal = min(initialMatrix[i])
            if minVal > 0 and minVal != math.inf:
                initialMatrix[i, 0:length + 1] -= minVal
                cost += minVal

        for j in range(0, length):  # Reducing the cols
            minVal = min(initialMatrix[:, j])
            if minVal > 0 and minVal != float("inf"):
                initialMatrix[0:length + 1, j] -= minVal
                cost += minVal

        return initialMatrix, cost

    ''' <summary>
        This is the entry point for the algorithm you'll write for your group project.
        </summary>
        <returns>results dictionary for GUI that contains three ints: cost of best solution, 
        time spent to find best solution, total number of solutions found during search, the 
        best solution found.  You may use the other three field however you like.
        algorithm</returns> 
    '''

    def fancy(self, time_allowance=60.0):
        pass

    def alreadyVisited(self, cityToCheck, visitedArray):
        for i in range(len(visitedArray)):
            if cityToCheck.getName() == visitedArray[i].getName():
                return True
        return False
