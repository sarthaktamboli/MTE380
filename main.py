from typing import List
from multiprocessing import Process, Queue
from camera import Camera
from main_controller import MainController
from simulator import Simulator
import numpy as np
from util import *

def initialize() -> List[Process]:
	# TODO: Initialize floormap, intersections and people
    # Initialize floormap
	grid = [[-1,  0,  0, -1, -1, -1, -1,  0,  0, -1, -1, -1, -1, -1, -1,  0, -1, -1, -1,  0],
			[-1,  0,  0,  0,  0, -1, -1, -1,  0,  0,  0,  0,  0,  0,  0,  0, -1, -1, -1,  0],
			[-1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
			[-1, -1, -1,  0,  0,  0, -1, -1,  0,  0,  0, -1, -1, -1,  0,  0,  0,  0,  0, -1],
			[-1, -1, -1, -1, -1,  0, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1,  0,  0,  0,  0],
			[-1, -1, -1, -1, -1,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0,  0],
			[-1, -1, -1, -1, -1,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0],
			[-1, -1, -1, -1,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0],
			[-1, -1, -1, -1,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0],
			[-1, -1, -1, -1,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0],
			[-1, -1, -1, -1,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0],
			[ 0,  0,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0],
			[-1, -1,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0],
			[ 0,  0,  0, -1,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0],
			[-1, -1, -1, -1,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0],
			[-1, -1, -1, -1,  0,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1,  0,  0,  0],
			[-1, -1, -1, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, -1, -1,  0,  0,  0,  0],
			[-1, -1, -1,  0,  0,  0, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, -1],
			[-1,  0,  0,  0,  0,  0, -1,  0, -1, -1, -1, -1,  0,  0,  0,  0,  0,  0, -1, -1],
			[-1,  0,  0,  0,  0, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1,  0, -1, -1, -1, -1],
			[-1,  0,  0, -1, -1, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1,  0, -1, -1, -1, -1]]

	floormap = np.array(grid).transpose(1, 0)

	# Initialize intersections
	intersections = []
	entryLaneInt0 = []
	entryLaneInt0.append(LaneIntersection(Coord(4, 2), LED((Coord(4, 2), Coord(5, 2))), Lane(1)))
	entryLaneInt0.append(LaneIntersection(Coord(6, 2), LED((Coord(6, 2), Coord(5, 2))), Lane(12)))
	exitLaneInt0 = []
	exitLaneInt0.append(LaneIntersection(Coord(4, 3), LED((Coord(4, 3), Coord(5, 3))), Lane(0)))
	exitLaneInt0.append(LaneIntersection(Coord(5, 4), LED((Coord(5, 4), Coord(5, 3))), Lane(11)))

	intersections.append(Intersection(0, entryLaneInt0, exitLaneInt0, LocalController(set(LED((Coord(4, 2), Coord(5, 2))),LED((Coord(6, 2), Coord(5, 2))),LED((Coord(4, 3), Coord(5, 3))),LED((Coord(5, 4), Coord(5, 3)))))))
	people = []


	# Set up queues for interprocess data
	cameraData = Queue()
	mainControllerData = Queue()
	simulatorData = Queue()

	# Initialize processes
	cameraProcess = Camera(floormap, simulatorData, cameraData)
	mainControllerProcess = MainController(intersections, cameraData, mainControllerData)
	simulatorProcess = Simulator(floormap, people, mainControllerData, simulatorData)

	# Return processes
	return [cameraProcess, mainControllerProcess, simulatorProcess]

def run(processes: List[Process]):
	for process in processes:
		process.start()
	for process in processes:
		process.run()


def main():
	processes = initialize()
	run(processes)


if __name__ == "__main__":
	main()
