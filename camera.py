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
				for i, in np.ndindex(self.prevListOfCoords):
					coord = self.prevListOfCoords[i]
					self.floormap[coord.x, coord.y] = 0

			for i, in np.ndindex(self.listOfCoords):
				coord = self.listOfCoords[i]
				self.floormap[coord.x, coord.y] = 1

			self.prevListOfCoords = self.listOfCoords

			# TODO: maybe insert a delay here?
			

