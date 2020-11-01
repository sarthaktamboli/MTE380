from typing import List
from multiprocessing import Process, Queue
from camera import Camera
from main_controller import MainController
from simulator import Simulator
import numpy as np
from util import *

def main():
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
	
	floormap = np.array(grid).transpose(1,0)

	# Initialize intersections
	intersections = []
	people = []


	# Set up queues for interprocess data
	cameraData = Queue()
	mainControllerData = Queue()
	simulatorData = Queue()

	# Initialize processes
	cameraProcess = Camera(floormap, simulatorData, cameraData)
	mainControllerProcess = MainController(intersections, cameraData, mainControllerData)
	simulator = Simulator(floormap, people, mainControllerData, simulatorData)

	cameraProcess.start()
	mainControllerProcess.start()
	simulator.run()


if __name__ == "__main__":
	main()