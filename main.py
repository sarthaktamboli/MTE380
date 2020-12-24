from typing import List
from multiprocessing import Process, Queue
from camera import Camera
from main_controller import MainController
from simulator import Simulator
from travel_time import TravelTime
import numpy as np
from util import *

def emptyQueue(queue: Queue) -> None:
	while not queue.empty():
		queue.get()

def main():
    # Initialize floormap
	grid = [[-1,  0,  1, -1, -1, -1, -1,  0,  0, -1, -1, -1, -1, -1, -1,  1, -1, -1, -1,  1],
			[-1,  0,  1,  1,  1, -1, -1, -1,  0,  2,  2,  2,  2,  2,  4,  4, -1, -1, -1,  1],
			[-1,  0,  0,  0,  1,  4,  2,  2,  4,  2,  3,  3,  3,  3,  4,  2,  2,  4,  1,  1],
			[-1, -1, -1,  0,  0,  4, -1, -1,  4,  3,  3, -1, -1, -1,  3,  3,  4,  4,  2, -1],
			[-1, -1, -1, -1, -1,  2, -1, -1,  3, -1, -1, -1, -1, -1, -1, -1,  3,  3,  2,  2],
			[-1, -1, -1, -1, -1,  4,  4,  3,  3, -1, -1, -1, -1, -1, -1, -1, -1,  3,  3,  2],
			[-1, -1, -1, -1, -1,  2,  3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  3,  2],
			[-1, -1, -1, -1,  2,  2,  3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  3,  2],
			[-1, -1, -1, -1,  2,  3,  3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  4,  4],
			[-1, -1, -1, -1,  2,  3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  3,  2],
			[-1, -1, -1, -1,  2,  3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  3,  2],
			[ 1,  1,  1,  1,  4,  4, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  3,  2],
			[-1, -1,  0,  0,  4,  4, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  3,  2],
			[ 0,  0,  0, -1,  2,  3,  3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  3,  2],
			[-1, -1, -1, -1,  2,  4,  4,  3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  3,  2],
			[-1, -1, -1, -1,  1,  4,  2,  3,  3, -1, -1, -1, -1, -1, -1, -1, -1,  3,  3,  2],
			[-1, -1, -1, -1,  1,  0,  2,  2,  4,  3,  3,  3,  4,  3, -1, -1,  3,  3,  2,  2],
			[-1, -1, -1,  1,  1,  0, -1,  4,  4,  2,  2,  2,  4,  3,  3,  4,  3,  2,  2, -1],
			[-1,  1,  1,  1,  0,  0, -1,  1, -1, -1, -1, -1,  2,  2,  2,  4,  2,  2, -1, -1],
			[-1,  1,  0,  0,  0, -1, -1,  1, -1, -1, -1, -1, -1, -1, -1,  0, -1, -1, -1, -1],
			[-1,  1,  0, -1, -1, -1, -1,  1, -1, -1, -1, -1, -1, -1, -1,  0, -1, -1, -1, -1]]

	floormap = np.array(grid).transpose(1,0)

	# Set up queues for interprocess data
	cameraData = Queue()
	mainControllerData = Queue()
	simulatorData = Queue()
	travelTimeData = Queue()

	# Initialize processes
	cameraProcess = Camera(floormap, simulatorData, cameraData)
	mainControllerProcess = MainController(cameraData, mainControllerData)
	simulator = Simulator(floormap, mainControllerData, simulatorData, travelTimeData, debug=False)
	travelTime = TravelTime(travelTimeData)

	cameraProcess.start()
	mainControllerProcess.start()
	travelTime.start()

	numOfPeople = [1, 5, 10, 25, 40, 50, 100]

	simulator.run(40)
	# emptyQueue(cameraData)
	# emptyQueue(mainControllerData)
	# emptyQueue(simulatorData)
	# emptyQueue(travelTimeData)

	# cameraProcess.terminate()
	# mainControllerProcess.terminate()
	# travelTime.terminate()


if __name__ == "__main__":
	main()
