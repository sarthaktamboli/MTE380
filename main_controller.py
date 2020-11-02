from util import *
from multiprocessing import Process, Queue

class MainController(Process):
	def __init__(self, intersections: List["Intersection"], cameraData: Queue, mainControllerData: Queue):
		Process.__init__(self)
		self.intersections = intersections.copy()
		self.cameraData = cameraData
		self.mainControllerData = mainControllerData

		'''
		logger = logging.getLogger('main_controller_logger')
		logger.setLevel(logging.DEBUG)
		# create file handler which logs even debug messages
		fh = logging.FileHandler('event.log')
		fh.setLevel(logging.DEBUG)
		# create formatter and add it to the handlers
		formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		fh.setFormatter(formatter)
		# add the handlers to logger
		logger.addHandler(fh)

		self.logger = logger
		'''

	def run(self):
		while True:
			# Get floormap from camera data
			floormap = self.cameraData.get()

			# Set up dictionary to store LEDs and their new power states for each local controller
			controllersLEDs = dict()

			# Look at all intersections
			for intersection in self.intersections:
				# Start with an empty list
				controllersLEDs[intersection.local_controller] = []

				# Enqueue people waiting at entry lane intersections to get into the intersection if not already in queue
				for entryLaneIntersection in intersection.entry_lane_intersections:
					if floormap[entryLaneIntersection.coord.x, entryLaneIntersection.coord.y] == 5:
						if entryLaneIntersection not in intersection.queue.queue:
							intersection.queue.put(entryLaneIntersection)
 
				# Check if there is anyone in the intersection and deal with it accordingly
				if intersection.is_occupied(floormap):
					# Turn on all LEDs of entry lane intersections to prevent exit
					for entryLaneIntersection in intersection.entry_lane_intersections:
						controllersLEDs[intersection.local_controller].append((entryLaneIntersection.LED, True))

					# Turn on all LEDs of exit lane intersections that are blocked, turn off otherwise
					for exitLaneIntersection in intersection.exit_lane_intersections:
						powerState = floormap[exitLaneIntersection.coord.x, exitLaneIntersection.coord.y] == 5
						controllersLEDs[intersection.local_controller].append((exitLaneIntersection.LED, powerState))
				else:
					# Turn on all LEDs of exit lane intersections to prevent entry
					for exitLaneIntersection in intersection.exit_lane_intersections:
						controllersLEDs[intersection.local_controller].append((exitLaneIntersection.LED, True))

					# Dequeue intersection queue to determine which person can enter the intersection, if any
					if intersection.queue.empty():
						# Turn off all LEDs of entry lane intersections if the queue is empty
						for entryLaneIntersection in intersection.entry_lane_intersections:
							controllersLEDs[intersection.local_controller].append((entryLaneIntersection.LED, False))
					else:
						# Turn off LED of entry lane intersection for dequeued person, turn on LED for other entry lane intersections
						dequeuedEntryLaneIntersection = intersection.queue.get()
						for entryLaneIntersection in intersection.entry_lane_intersections:
							powerState = entryLaneIntersection != dequeuedEntryLaneIntersection
							controllersLEDs[intersection.local_controller].append((entryLaneIntersection.LED, powerState))

			# List of all LEDs, initialize as empty
			LEDs = []

			# Local controller turns on or off LEDs accordingly
			for localController in controllersLEDs:
				localLEDs = [i[0] for i in controllersLEDs[localController]]
				localPowerStates = [i[1] for i in controllersLEDs[localController]]
				localController.power_LEDs(localLEDs, localPowerStates)

				# Add list of local LEDs to list of all LEDs after their states have been updated
				LEDs += localLEDs

			# Enqueue mainControllerData, which consists of the new LEDs
			self.mainControllerData.put(LEDs.copy())
