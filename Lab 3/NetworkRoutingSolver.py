#!/usr/bin/python3


from CS312Graph import *
import time
import math


class NetworkRoutingSolver:
    def __init__(self):
        self.distances = None
        self.previous = None
        pass

    def initializeNetwork(self, network):
        assert (type(network) == CS312Graph)
        self.network = network

    def getShortestPath(self, destIndex):
        self.dest = destIndex
        # TODO: RETURN THE SHORTEST PATH FOR destIndex
        #       INSTEAD OF THE DUMMY SET OF EDGES BELOW
        #       IT'S JUST AN EXAMPLE OF THE FORMAT YOU'LL 
        #       NEED TO USE
        path_edges = []

        if self.distances[destIndex] == math.inf:
            return {'cost': 0, 'path': []}

        total_length = self.distances[destIndex]

        current = destIndex
        while self.previous[current] is not None:
            edge = self.getNeighbor(current, self.network.nodes[self.previous[current]])
            path_edges.append((edge.src.loc, edge.dest.loc, '{:.0f}'.format(edge.length)))
            current = self.previous[current]
        return {'cost': total_length, 'path': path_edges}

    def getNeighbor(self, currentID, neighborNode):
        for i in range(len(neighborNode.neighbors)):
            if neighborNode.neighbors[i].dest.node_id == currentID:
                return neighborNode.neighbors[i]
        else:
            return None

    def computeShortestPaths(self, srcIndex, use_heap=False):
        self.source = srcIndex
        t1 = time.time()
        # TODO: RUN DIJKSTRA'S TO DETERMINE SHORTEST PATHS.
        #       ALSO, STORE THE RESULTS FOR THE SUBSEQUENT
        #       CALL TO getShortestPath(dest_index)

        H = ArrayQueue()
        allNodes = self.network.nodes

        # SETTING EACH DISTANCE TO INFINITY EXCEPT SOURCE
        for i in range(len(allNodes)):
            H.distances.append(math.inf)
            H.previousNodes.append(None)
        H.distances[srcIndex] = 0

        # MAKING QUEUE
        for i in range(len(allNodes)):
            H.insert(allNodes[i])

        # WHILE LOOP THROUGH THE QUEUE
        while len(H.ArrayOfNodes) != 0:
            u = H.deleteMin()

            # FOR LOOP THROUGH EDGES OF NODE U
            for i in range(len(u.neighbors)):
                currentFriend = u.neighbors[i]
                if H.distances[currentFriend.dest.node_id] > H.distances[u.node_id] + currentFriend.length:
                    H.distances[currentFriend.dest.node_id] = H.distances[u.node_id] + currentFriend.length
                    H.previousNodes[currentFriend.dest.node_id] = u.node_id
                    H.decreaseKey(currentFriend.dest.node_id)

        self.distances = H.distances
        self.previous = H.previousNodes
        t2 = time.time()
        return (t2 - t1)


class ArrayQueue:
    ArrayOfNodes = []
    distances = []
    previousNodes = []

    def insert(self, node):
        self.ArrayOfNodes.append(node)

    def deleteMin(self):

        min = 10000
        minIndex = 0
        minNode = self.ArrayOfNodes[0]

        for i in range(len(self.ArrayOfNodes)):
            if self.distances[self.ArrayOfNodes[i].node_id] < min:
                min = self.distances[self.ArrayOfNodes[i].node_id]
                minNode = self.ArrayOfNodes[i]
                minIndex = i

        self.ArrayOfNodes.pop(minIndex)

        return minNode

    def decreaseKey(self, v):
        pass


class HeapQueue:
    ArrayOfNodes = []
    helper = []
    distances = []
    previousNodes = []

    def insert(self, node):
        self.ArrayOfNodes.append(node)
        self.helper.append(len(self.ArrayOfNodes) - 1)
        self.bubbleUp(len(self.ArrayOfNodes) - 1)

    def deleteMin(self):

        ret_val = self.ArrayOfNodes[0]
        self.ArrayOfNodes[0] = self.ArrayOfNodes[len(self.ArrayOfNodes) - 1]
        self.ArrayOfNodes.pop()
        self.helper[ret_val.node_id] = 0
        self.settle(0)
        return ret_val

    def decreaseKey(self, node_id):
        self.bubbleUp(self.helper[node_id])

    def settle(self, index):
        l = self.getLeft(index)
        r = self.getRight(index)

        smallest = index

        if l < len(self.ArrayOfNodes) and self.distances[self.helper[l]] < self.distances[self.helper[index]]:
            smallest = l
        if r < len(self.ArrayOfNodes) and self.distances[self.helper[r]] < self.distances[self.helper[smallest]]:
            smallest = r
        if smallest != index:
            self.swap(index, smallest)
            self.settle(smallest)

    def bubbleUp(self, index):
        while index//2 > 0 and self.distances[self.helper[self.getParent(index)]] > self.distances[self.helper[index]]:
            self.swap(index, self.getParent(index))
            index = self.getParent(index)

    def swap(self, index, parentIndex):
        temp = self.ArrayOfNodes[parentIndex]
        self.ArrayOfNodes[parentIndex] = self.ArrayOfNodes[index]
        self.ArrayOfNodes[index] = temp

        self.helper[self.ArrayOfNodes[parentIndex].node_id] = parentIndex
        self.helper[self.ArrayOfNodes[index].node_id] = index

    def getLeft(self, index):
        return math.ceil(2 * index + 1)

    def getRight(self, index):
        return math.ceil(2 * index + 2)

    def getParent(self, index):
        return math.floor((index - 1) / 2)
