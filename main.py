from typing import List
from multiprocessing import Process, Queue
from camera import Camera
from main_controller import MainController
from simulator import Simulator
import numpy as np
from util import *

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

	# Initialize processes
	cameraProcess = Camera(floormap, simulatorData, cameraData)
	mainControllerProcess = MainController(cameraData, mainControllerData)
	simulator = Simulator(floormap, mainControllerData, simulatorData, debug=False)

	cameraProcess.start()
	mainControllerProcess.start()
	simulator.run()


if __name__ == "__main__":
	main()
