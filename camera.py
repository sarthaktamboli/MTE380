from util import *
from multiprocessing import Process, Queue

class Camera(Process):
	def __init__(self, floormap: np.ndarray, simulatorData: Queue, cameraData: Queue):
		Process.__init__(self)
		self.emptyFloormap = floormap.copy()
		self.floormap = floormap.copy()
		self.cameraData = cameraData
		self.simulatorData = simulatorData
		self.listOfCoords = None
		self.prevListOfCoords = None

	def run(self):
		while True:
			self.listOfCoords = self.simulatorData.get()

			# TODO: maybe check for social distancing breach?

			if self.prevListOfCoords is not None:
				for coord in self.prevListOfCoords:
					self.floormap[coord.x, coord.y] = self.emptyFloormap[coord.x, coord.y]

			for coord in self.listOfCoords:
				self.floormap[coord.x, coord.y] = 5

			self.prevListOfCoords = self.listOfCoords

			# TODO: maybe insert a delay here?

			self.cameraData.put(self.floormap.copy())
			

