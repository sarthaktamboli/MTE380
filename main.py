from typing import List
from multiprocessing import Process, Queue
from camera import Camera
from main_controller import MainController
from simulator import Simulator

def initialize() -> List[Process]:
	# TODO: Initialize floormap, intersections and people

	# Set up queues for interprocess data
	simulatorData = Queue()
	cameraData = Queue()
	mainControllerData = Queue()

	# Initialize processes
	cameraProcess = Camera(floormap, simulatorData, cameraData)
	mainControllerProcess = MainController(intersections, cameraData, mainControllerData)
	simulatorProcess = Simulator(floormap, people, mainControllerData, simulatorData)

	# Return processes
	return (cameraProcess, mainControllerProcess, simulatorProcess)

def run(processes: List[Process]):
	for process in processes:
		process.start()


def main():
	processes = initialize()
	run(processes)


if __name__ == "__main__":
	main()