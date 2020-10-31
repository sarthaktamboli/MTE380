from util import *
from multiprocessing import Process, Queue

class Camera(Process):
	def __init__(self, floormap: np.ndarray, simulatorData: Queue, cameraData: Queue):
		Process.__init__(self)
		self.floormap = floormap.copy()
		self.cameraData = cameraData
		self.listOfCoords = None
		self.prevListOfCoords = None

	def run(self):
		while True:
			self.listOfCoords = simulatorData.get()

			# TODO: maybe check for social distancing breach?

			if self.prevListOfCoords is not None:
				for coord in self.prevListOfCoords:
					self.floormap[coord.x, coord.y] = 0

			for coord in self.listOfCoords:
				self.floormap[coord.x, coord.y] = 1

			self.prevListOfCoords = self.listOfCoords

			# TODO: maybe insert a delay here?

			cameraData.put(self.floormap.copy())
			

