import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from multiprocessing import Process, Queue
from util import Coord, Location
from heapq import heappop, heappush

# DC shortest pathfinder class
class Pathfinder():
    # initialization of layout
    def __init__(self, grid: np.ndarray):
        self.grid = grid
        self.xLim, self.yLim = np.shape(grid)
        self.illegalMoves = {Coord(2,  0): Coord(3,  0), Coord(3,  0): Coord(2,  0),
                             Coord(0,  2): Coord(0,  3), Coord(0,  3): Coord(0,  2),
                             Coord(1,  2): Coord(1,  3), Coord(1,  3): Coord(1,  2),
                             Coord(2,  2): Coord(2,  3), Coord(2,  3): Coord(2,  2),
                             Coord(0, 17): Coord(0, 18), Coord(0, 18): Coord(0, 17),
                             Coord(1, 17): Coord(1, 18), Coord(1, 18): Coord(1, 17),
                             Coord(2, 17): Coord(2, 18), Coord(2, 18): Coord(2, 17)}

    # checks validity of desired move
    def isMoveValid(self, visited: set, cell: Coord, neighbour: Coord) -> bool:
        if cell in self.illegalMoves:
            return (self.xLim > neighbour.x >= 0 and self.yLim > neighbour.y >= 0 and
                    self.grid[neighbour.x][neighbour.y] == 0 and
                    self.illegalMoves[cell] != neighbour and neighbour not in visited)
        else:
            return (self.xLim > neighbour.x >= 0 and self.yLim > neighbour.y >= 0 and
                    self.grid[neighbour.x][neighbour.y] == 0 and neighbour not in visited)

    # heuristic calculator
    def heuristic(self, cell: Coord, goal: Coord) -> int:
        # Diagonal distance
        # scale factors of 1 = minimum cost to move to adjacent cells
        D = 1
        D2 = 1
        dx = abs(cell.x - goal.x)
        dy = abs(cell.y - goal.y)
        return D * (dx + dy) + (D2 - 2 * D) * min(dx, dy)

    # shortest path search
    # a star implementation
    def search(self, start: Coord, goal: Coord) -> int:
        # possible moves
        xTranslation = [-1,  0,  1,  1,  1,  0, -1, -1]
        yTranslation = [-1, -1, -1,  0,  1,  1,  1,  0]

        # initial cost of move
        cost = 0

        # fringe priority queue
        fringe = []
        heappush(fringe, (cost + self.heuristic(start, goal), cost, start))

        # stores visited positions
        visited = set()

        # loop until fringe is empty
        while fringe:
            # pop item from priority queue fringe
            _, currCost, cell = heappop(fringe)
            # goal state; goal node reached, search terminated
            if cell == goal:
                return currCost
            # if cell already visited, skip
            if cell in visited:
                continue
            # add current position to visited set
            visited.add(cell)
            # check for potential neighbours
            for i in range(8):
                neighbour = Coord(cell.x + xTranslation[i], cell.y + yTranslation[i])
                # check validity of each neighbour
                if self.isMoveValid(visited, cell, neighbour):
                    # append neighbour to fringe
                    heappush(fringe, (currCost + self.heuristic(neighbour, goal),
                                      currCost + 1, neighbour))

class TravelTime(Process):
    def __init__(self, travelTimeData: Queue):
        Process.__init__(self)
        self.travelTimeData = travelTimeData
        self.idealTravelTimes = dict()

        # initialization of ideal grid, with original unrestricted travel space
        grid = [[ 0,  0,  0,  0, -1, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, -1, -1,  0],
    			[ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    			[ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    			[ 0,  0,  0,  0,  0,  0, -1, -1,  0,  0,  0, -1, -1, -1,  0,  0,  0,  0,  0,  0],
    			[ 0,  0,  0,  0,  0,  0, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1,  0,  0,  0,  0],
    			[ 0,  0,  0,  0,  0,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0,  0],
    			[ 0,  0,  0,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0],
    			[ 0,  0,  0,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0],
    			[ 0,  0,  0,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0],
    			[ 0,  0,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0],
    			[ 0,  0,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0],
    			[ 0,  0,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0],
    			[ 0,  0,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0],
    			[ 0,  0,  0,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0],
    			[ 0,  0,  0,  0,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0],
    			[ 0,  0,  0,  0,  0,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0,  0],
    			[ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, -1, -1,  0,  0,  0,  0],
    			[ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    			[ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    			[ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    			[ 0,  0,  0,  0, -1, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, -1, -1,  0]]

        floormap = np.array(grid).transpose(1, 0)
        shortestPathfinder = Pathfinder(floormap)
        exitPoints = [Location.getCoords(i)[0] for i in range(1, 9)]
        entryPoints = [Location.getCoords(i)[1] for i in range(1, 9)]

        for exitPoint in exitPoints:
            if exitPoint == None:
                continue
            else:
                for entryPoint in entryPoints:
                    self.idealTravelTimes[(exitPoint, entryPoint)] = shortestPathfinder.search(exitPoint, entryPoint)
        del self.idealTravelTimes[(Coord(19, 8), Coord(19, 8))]

        for path, time in self.idealTravelTimes.items():
            print(f"{path}: {time}")

    def autolabel(self, rects, ax):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')

    def run(self):
        while True:
            simulatedTravelTimes = self.travelTimeData.get()
            idealTimes = []
            labels, simTimes = simulatedTravelTimes.keys(), simulatedTravelTimes.values()
            for state in labels:
                idealTimes.append(self.idealTravelTimes[state])

            # finding percentage difference btwn sim and ideal times
            idealTimeAvg = sum(idealTimes) / len(idealTimes)
            simTimeAvg = sum(simTimes) / len(simTimes)
            print("Response time: ", simTimeAvg / idealTimeAvg * 100)

            x = np.arange(len(labels))
            width = 0.35  # the width of the bars

            fig, ax = plt.subplots()
            rects1 = ax.bar(x - width/2, idealTimes, width, label='Normal')
            rects2 = ax.bar(x + width/2, simTimes, width, label='COVID')

            # Add some text for labels, title and custom x-axis tick labels, etc.
            ax.set_ylabel('Num of iterations')
            ax.set_title('Normal vs COVID Travel Time')
            ax.set_xticks(x)
            # ax.set_xticklabels(labels)
            ax.legend()

            self.autolabel(rects1, ax)
            self.autolabel(rects2, ax)

            fig.tight_layout()

            plt.show()
