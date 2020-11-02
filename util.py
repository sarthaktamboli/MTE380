from typing import List, Tuple, Set, Optional
from queue import Queue
from collections import namedtuple
import numpy as np

Coord = namedtuple('Coord', ['x', 'y'])

class Location():
	def __init__(self, locID: int):
		self.locID = locID
		self.srcCoord, self.dstCoord = self.getCoords(self.locID)

	@staticmethod
	def getCoord(self, locID: int) -> "Coord":
		locCoords = [(Coord(2, 20), Coord(1, 20)),		# Location 1
					 (Coord(1, 0), Coord(2, 0)),		# Location 2
					 (Coord(0, 13), Coord(0, 11)),		# Location 3
					 (Coord(15, 20), Coord(7, 20)),		# Location 4
					 (Coord(7, 0), Coord(15, 0)),		# Location 5
					 (Coord(12, 16), Coord(8, 5)),		# Location 6
					 (None, Coord(19, 0)),				# Location 7
					 (Coord(19, 8), Coord(19, 8))]		# Location 8
		return locCoords[locID]

class Person():
	def __init__(self, srcLoc: Location, dstLoc: Location):
		if srcLoc.locID == 7:
			raise ValueError("Location 7 is exit only")
		if srcLoc.locID == dstLoc.locID == 8:
			raise ValueError("Location 8 cannot be a srcLoc and dstLoc for the same person")

		self.srcLoc = srcLoc
		self.dstLoc = dstLoc
		self.coord = srcLoc.coord
		self.path = self.getPath()
		self.pathIdx = 0

	def getPath(self) -> List["Coord"]:
		# Start with empty dict
		personPaths = dict()

		# From Loc 1
		personPaths[(1, 1)] = [7, 8]
		personPaths[(1, 2)] = [7, 30, 31, 22, 12, 1]
		personPaths[(1, 3)] = [7, 30, 10]
		personPaths[(1, 4)] = [7, 19, 6]
		personPaths[(1, 5)] = [7, 30, 31, 22, 23, 3]
		personPaths[(1, 6)] = [7, 30, 31]							# Special Case 1
		personPaths[(1, 7)] = [7, 30, 31, 22, 23, 24, 4]
		personPaths[(1, 8)] = [7, 19, 18, 17, 16]					# Special Case 2

		# From Loc 2
		personPaths[(2, 1)] = [0, 11, 21, 20, 8]
		personPaths[(2, 2)] = [0, 1]
		personPaths[(2, 3)] = [0, 11, 21, 10]
		personPaths[(2, 4)] = [0, 11, 21, 20, 19, 6]
		personPaths[(2, 5)] = [0, 11, 22, 23, 3]
		personPaths[(2, 6)] = [0, 11]								# Special Case 3
		personPaths[(2, 7)] = [0, 11, 22, 23, 24, 4]
		personPaths[(2, 8)] = [0, 11, 22, 23, 24, 25]				# Special Case 4

		# From Loc 3
		personPaths[(3, 1)] = [9, 20, 8]
		personPaths[(3, 2)] = [9, 31, 22, 12, 1]
		personPaths[(3, 3)] = [9, 10]
		personPaths[(3, 4)] = [9, 20, 19, 6]
		personPaths[(3, 5)] = [9, 31, 22, 23, 3]
		personPaths[(3, 6)] = [9, 31]								# Special Case 1
		personPaths[(3, 7)] = [9, 31, 22, 23, 24, 4]
		personPaths[(3, 8)] = [9, 20, 19, 18, 17, 16]				# Special Case 2

		# From Loc 4
		personPaths[(4, 1)] = [5, 27, 28, 29, 8]
		personPaths[(4, 2)] = [5, 27, 28, 29, 30, 31, 22, 12, 1]
		personPaths[(4, 3)] = [5, 27, 28, 29, 30, 10]
		personPaths[(4, 4)] = [5, 27, 28, 6]
		personPaths[(4, 5)] = [5, 27, 28, 29, 30, 31, 22, 23, 3]
		personPaths[(4, 6)] = [5, 27, 28, 29, 30, 31]				# Special Case 1
		personPaths[(4, 7)] = [5, 27, 28, 29, 30, 31, 22, 23, 24, 4]
		personPaths[(4, 8)] = [5, 16]								# Special Case 2

		# From Loc 5
		personPaths[(5, 1)] = [2, 12, 11, 21, 20, 8]
		personPaths[(5, 2)] = [2, 12, 1]
		personPaths[(5, 3)] = [2, 12, 11, 21, 10]
		personPaths[(5, 4)] = [2, 12, 11, 21, 20, 19, 6]
		personPaths[(5, 5)] = [2, 23, 3]
		personPaths[(5, 6)] = [2, 12, 11]							# Special Case 3
		personPaths[(5, 7)] = [2, 23, 24, 4]
		personPaths[(5, 8)] = [2, 23, 24, 25]						# Special Case 4

		# From Loc 6
		personPaths[(6, 1)] = [28, 29, 8]							# Special Case 5
		personPaths[(6, 2)] = [28, 29, 30, 31, 22, 12, 1]			# Special Case 5
		personPaths[(6, 3)] = [28, 29, 30, 10]						# Special Case 5
		personPaths[(6, 4)] = [28, 6]								# Special Case 5
		personPaths[(6, 5)] = [28, 29, 30, 31, 22, 23, 3]			# Special Case 5
		personPaths[(6, 6)] = [28, 29, 30, 31]						# Special Case 1 and 5
		personPaths[(6, 7)] = [28, 29, 30, 31, 22, 23, 24, 4]		# Special Case 5
		personPaths[(6, 8)] = [17, 16]								# Special Case 2 and 6

		# From Loc 8
		personPaths[(8, 1)] = [26, 27, 28, 29, 8]					# Special Case 7
		personPaths[(8, 2)] = [15, 14, 13, 12, 1]					# Special Case 8
		personPaths[(8, 3)] = [26, 27, 28, 29, 30, 10]				# Special Case 7
		personPaths[(8, 4)] = [26, 27, 28, 6]						# Special Case 7
		personPaths[(8, 5)] = [15, 14, 3]							# Special Case 8
		personPaths[(8, 6)] = [15, 14, 13, 12, 11]					# Special Case 3 and 8
		personPaths[(8, 7)] = [15, 4]								# Special Case 8

		personPath = personPaths[(self.srcLoc.locID, self.dstLoc.locID)]
		coordsPath = []
		for i, laneID in enumerate(personPath):
			currLaneID = laneID
			nextLaneID = personPath[i + 1] if i < len(personPath) - 1 else None
			coordsPath += Lane.getPath(currLaneID) + ([] if nextLaneID is None else LaneTransition.getPath(currLaneID, nextLaneID))

		specialCase1 = [(1, 6), (3, 6), (4, 6), (6, 6)]
		specialCase2 = [(1, 8), (3, 8), (4, 8), (6, 8)]
		specialCase3 = [(2, 6), (5, 6), (8, 6)]
		specialCase4 = [(2, 8), (5, 8)]
		specialCase5 = [(6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7)]
		specialCase6 = [(6, 8)]
		specialCase7 = [(8, 1), (8, 3), (8, 4)]
		specialCase8 = [(8, 2), (8, 5), (8, 6), (8, 7)]

		if (self.srcLoc.locID, self.dstLoc.locID) in specialCase1:
			coordsPath = coordsPath + [Coord(6, 5), Coord(7, 5), Coord(8, 5)]
		if (self.srcLoc.locID, self.dstLoc.locID) in specialCase2:
			coordsPath = coordsPath + [Coord(19, 8)]
		if (self.srcLoc.locID, self.dstLoc.locID) in specialCase3:
			coordsPath = coordsPath + [Coord(5, 5), Coord(6, 5), Coord(7, 5), Coord(8, 5)]
		if (self.srcLoc.locID, self.dstLoc.locID) in specialCase4:
			coordsPath = coordsPath + [Coord(18, 8), Coord(19, 8)]
		if (self.srcLoc.locID, self.dstLoc.locID) in specialCase5:
			coordsPath = [Coord(12, 16)] + coordsPath
		if (self.srcLoc.locID, self.dstLoc.locID) in specialCase6:
			coordsPath = [Coord(12, 16), Coord(12, 17)] + coordsPath
		if (self.srcLoc.locID, self.dstLoc.locID) in specialCase7:
			coordsPath = [Coord(19, 8), Coord(18, 8)] + coordsPath
		if (self.srcLoc.locID, self.dstLoc.locID) in specialCase8:
			coordsPath = [Coord(19, 8)] + coordsPath

		if coordsPath[0] != self.srcLoc.srcCoord:
			raise ValueError("Path does not start at srcLoc")
		if coordsPath[-1] != self.dstLoc.dstCoord:
			raise ValueError("Path does not end at dstLoc")
		return coordsPath


	def nextCoord(self) -> Coord:
		currCoord = self.path[self.pathIdx]
		nextCoord = self.path[self.pathIdx + 1]
		if abs(currCoord.x - nextCoord.x) + abs(currCoord.y - nextCoord.y) > 1:
			raise ValueError("nextCoord should be one unit away from currCoord")
		return nextCoord

	def advance(self):
		self.coord = self.nextCoord()
		self.pathIdx += 1


class Lane():
	def __init__(self, laneID: int):
		self.laneID = laneID
		self.path = self.getPath(self.laneID)

	@staticmethod
	def getPath(laneID: int) -> List["Coord"]:
		lanePaths = [[Coord(1, 0), Coord(1, 1), Coord(1, 2), Coord(2, 2), Coord(3, 2), Coord(3, 3), Coord(4, 3)],																											# Lane 0
					 [Coord(4, 2), Coord(4, 1), Coord(3, 1), Coord(2, 1), Coord(2, 0)],																																		# Lane 1
					 [Coord(7, 0), Coord(8, 0), Coord(8, 1)],																																								# Lane 2
					 [Coord(15, 0)],																																														# Lane 3
					 [Coord(18, 2), Coord(19, 2), Coord(19, 1), Coord(19, 0)],																																				# Lane 4
					 [Coord(15, 20), Coord(15, 19)],																																										# Lane 5
					 [Coord(7, 18), Coord(7, 19), Coord(7, 20)],																																							# Lane 6
					 [Coord(2, 20), Coord(2, 19), Coord(3, 19), Coord(4, 19), Coord(4, 18), Coord(5, 18), Coord(5, 17), Coord(5, 16)],																						# Lane 7
					 [Coord(4, 15), Coord(4, 16), Coord(4, 17), Coord(3, 17), Coord(3, 18), Coord(2, 18), Coord(1, 18), Coord(1, 19), Coord(1, 20)],																		# Lane 8
					 [Coord(0, 13), Coord(1, 13), Coord(2, 13), Coord(2, 12), Coord(3, 12)],																																# Lane 9
					 [Coord(3, 11), Coord(2, 11), Coord(1, 11), Coord(0, 11)],																																				# Lane 10
					 [Coord(5, 4)],																																															# Lane 11
					 [Coord(7, 2), Coord(6, 2)],																																											# Lane 12
					 [Coord(13, 1), Coord(12, 1), Coord(11, 1), Coord(10, 1), Coord(9, 1), Coord(9, 2)],																													# Lane 13
					 [Coord(16, 2), Coord(15, 2)],																																											# Lane 14
					 [Coord(19, 7), Coord(19, 6), Coord(19, 5), Coord(19, 4), Coord(18, 4), Coord(18, 3)],																													# Lane 15
					 [Coord(16, 18), Coord(17, 18), Coord(17, 17), Coord(18, 17), Coord(18, 16), Coord(19, 16), Coord(19, 15), Coord(19, 14), Coord(19, 13), Coord(19, 12), Coord(19, 11), Coord(19, 10), Coord(19, 9)],	# Lane 16
					 [Coord(12, 18), Coord(13, 18), Coord(14, 18)],																																							# Lane 17
					 [Coord(9, 17), Coord(10, 17), Coord(11, 17)],																																							# Lane 18
					 [Coord(6, 15), Coord(6, 16), Coord(7, 16)],																																							# Lane 19
					 [Coord(4, 13), Coord(4, 14)],																																											# Lane 20
					 [Coord(5, 6), Coord(5, 7), Coord(4, 7), Coord(4, 8), Coord(4, 9), Coord(4, 10)],																														# Lane 21
					 [Coord(7, 5), Coord(8, 5), Coord(8, 4)],																																								# Lane 22
					 [Coord(9, 3), Coord(10, 3), Coord(10, 2), Coord(11, 2), Coord(12, 2), Coord(13, 2)],																													# Lane 23
					 [Coord(14, 3), Coord(15, 3)],																																											# Lane 24
					 [Coord(16, 4), Coord(17, 4), Coord(17, 5), Coord(18, 5), Coord(18, 6), Coord(18, 7)],																													# Lane 25
					 [Coord(18, 9), Coord(18, 10), Coord(18, 11), Coord(18, 12), Coord(18, 13), Coord(18, 14), Coord(18, 15), Coord(17, 15), Coord(17, 16), Coord(16, 16), Coord(16, 17)],									# Lane 26
					 [Coord(14, 17), Coord(13, 17), Coord(13, 16)],																																							# Lane 27
					 [Coord(11, 16), Coord(10, 16), Coord(9, 16)],																																							# Lane 28
					 [Coord(8, 15), Coord(7, 15), Coord(7, 14)],																																							# Lane 29
					 [Coord(6, 13), Coord(5, 13)],																																											# Lane 30
					 [Coord(5, 10), Coord(5, 9), Coord(5, 8), Coord(6, 8), Coord(6, 7), Coord(6, 6)]]																														# Lane 31
		return lanePaths[laneID]

class LaneTransition():
	def __init__(self, srcLaneID: Lane, dstLaneID: Lane):
		self.srcLaneID = srcLaneID
		self.dstLaneID = dstLaneID
		self.path = self.getPath(self.srcLaneID, self.dstLaneID)

	@staticmethod
	def getPath(srcLaneID: int, dstLaneID: int) -> List["Coord"]:
		# Start with empty dict
		laneTransitionPaths = dict()

		# Lane transitions at interserction 0
		laneTransitionPaths[(0, 1)] = [Coord(5, 3), Coord(5, 2)]
		laneTransitionPaths[(0, 11)] = [Coord(5, 3)]
		laneTransitionPaths[(12, 1)] = [Coord(5, 2)]
		laneTransitionPaths[(12, 11)] = [Coord(5, 2), Coord(5, 3)]

		# Lane transitions at intersection 1
		laneTransitionPaths[(2, 12)] = [Coord(8, 2)]
		laneTransitionPaths[(2, 23)] = [Coord(8, 2), Coord(8, 3)]
		laneTransitionPaths[(13, 12)] = [Coord(8, 2)]
		laneTransitionPaths[(13, 23)] = [Coord(8, 2), Coord(8, 3)]
		laneTransitionPaths[(22, 12)] = [Coord(8, 3), Coord(8, 2)]
		laneTransitionPaths[(22, 23)] = [Coord(8, 3)]

		# Lane transitions at intersection 2
		laneTransitionPaths[(14, 3)] = [Coord(15, 1)]
		laneTransitionPaths[(14, 13)] = [Coord(15, 1), Coord(14, 1)]
		laneTransitionPaths[(14, 24)] = [Coord(15, 1), Coord(14, 1), Coord(14, 2)]
		laneTransitionPaths[(23, 3)] = [Coord(14,2), Coord(14, 1), Coord(15, 1)]
		laneTransitionPaths[(23, 13)] = [Coord(14, 2), Coord(14, 1)]
		laneTransitionPaths[(23, 24)] = [Coord(14, 2)]

		# Lane transitions at intersection 3
		laneTransitionPaths[(15, 4)] = [Coord(17, 3), Coord(17, 2)]
		laneTransitionPaths[(15, 14)] = [Coord(17, 3), Coord(17, 2)]
		laneTransitionPaths[(15, 25)] = [Coord(17, 3), Coord(16, 3)]
		laneTransitionPaths[(24, 4)] = [Coord(16, 3), Coord(17, 3), Coord(17, 2)]
		laneTransitionPaths[(24, 14)] = [Coord(16, 3), Coord(17, 3), Coord(17, 2)]
		laneTransitionPaths[(24, 25)] = [Coord(16, 3)]

		# Lane transitions at intersection 4
		laneTransitionPaths[(16, 15)] = [Coord(19, 8)]
		laneTransitionPaths[(16, 26)] = [Coord(19, 8), Coord(18, 8)]
		laneTransitionPaths[(25, 15)] = [Coord(18, 8), Coord(19, 8)]
		laneTransitionPaths[(25, 26)] = [Coord(18, 8)]

		# Lane transitions at intersection 5
		laneTransitionPaths[(5, 16)] = [Coord(15, 18)]
		laneTransitionPaths[(5, 27)] = [Coord(15, 18), Coord(15, 17)]
		laneTransitionPaths[(17, 16)] = [Coord(15, 18)]
		laneTransitionPaths[(17, 27)] = [Coord(15, 18), Coord(15, 17)]
		laneTransitionPaths[(26, 16)] = [Coord(15, 17), Coord(15, 18)]
		laneTransitionPaths[(26, 27)] = [Coord(15, 17)]

		# Lane transitions at intersection 6
		laneTransitionPaths[(18, 17)] = [Coord(12, 17)]
		laneTransitionPaths[(18, 28)] = [Coord(12, 17), Coord(12, 16)]
		laneTransitionPaths[(27, 17)] = [Coord(12, 16), Coord(12, 17)]
		laneTransitionPaths[(27, 28)] = [Coord(12, 16)]

		# Lane transitions at intersection 7
		laneTransitionPaths[(19, 6)] = [Coord(7, 17)]
		laneTransitionPaths[(19, 18)] = [Coord(7, 17), Coord(8, 17)]
		laneTransitionPaths[(19, 29)] = [Coord(7, 17), Coord(8, 17), Coord(8, 16)]
		laneTransitionPaths[(28, 6)] = [Coord(8, 16), Coord(8, 17), Coord(7, 17)]
		laneTransitionPaths[(28, 18)] = [Coord(8, 16), Coord(8, 17)]
		laneTransitionPaths[(28, 29)] = [Coord(8, 16)]

		# Lane transitions at intersection 8
		laneTransitionPaths[(7, 8)] = [Coord(5, 15)]
		laneTransitionPaths[(7, 19)] = [Coord(5, 15)]
		laneTransitionPaths[(7, 30)] = [Coord(5, 15), Coord(5, 14), Coord(6, 14)]
		laneTransitionPaths[(20, 8)] = [Coord(5, 14), Coord(5, 15)]
		laneTransitionPaths[(20, 19)] = [Coord(5, 14), Coord(5, 15)]
		laneTransitionPaths[(20, 30)] = [Coord(5, 14), Coord(6, 14)]
		laneTransitionPaths[(29, 8)] = [Coord(6, 14), Coord(5, 14), Coord(5, 15)]
		laneTransitionPaths[(29, 19)] = [Coord(6, 14), Coord(5, 14), Coord(5, 15)]
		laneTransitionPaths[(29, 30)] = [Coord(6, 14)]

		# Lane transitions at intersection 9
		laneTransitionPaths[(9, 10)] = [Coord(4, 12), Coord(4, 11)]
		laneTransitionPaths[(9, 20)] = [Coord(4, 12)]
		laneTransitionPaths[(9, 31)] = [Coord(4, 12), Coord(5, 12), Coord(5, 11)]
		laneTransitionPaths[(21, 10)] = [Coord(4, 11)]
		laneTransitionPaths[(21, 20)] = [Coord(4, 11), Coord(4, 12)]
		laneTransitionPaths[(21, 31)] = [Coord(4, 11), Coord(5, 11)]
		laneTransitionPaths[(30, 10)] = [Coord(5, 12), Coord(5, 11), Coord(4, 11)]
		laneTransitionPaths[(30, 20)] = [Coord(5, 12), Coord(4, 12)]
		laneTransitionPaths[(30, 31)] = [Coord(5, 12), Coord(5, 11)]

		# Lane transitions at intersection 10
		laneTransitionPaths[(11, 21)] = [Coord(5, 5)]
		laneTransitionPaths[(11, 22)] = [Coord(5, 5), Coord(6, 5)]
		laneTransitionPaths[(31, 21)] = [Coord(6, 5), Coord(5, 5)]
		laneTransitionPaths[(31, 22)] = [Coord(6, 5)]

		return laneTransitionPaths[(srcLaneID, dstLaneID)]



class LED():
	def __init__(self, coordBounds: Tuple[Coord]):
		if len(coordBounds) != 2:
			raise ValueError("LED must be bounded by only two coordinates")
		if abs(coordBounds[0].x - coordBounds[1].x) + abs(coordBounds[0].y - coordBounds[1].y) != 1:
			raise ValueError("LED must be bounded by two coordinates that are next to each other")

		self.coordBounds = coordBounds
		self.is_on = False

	def power_on():
		if not self.is_on:
			time.sleep(0.0001)
			self.is_on = True

	def power_off():
		if self.is_on:
			time.sleep(0.0001)
			self.is_on = False

	def is_vertical() -> bool:
		return abs(coordBounds[0].y - coordBounds[1].y) == 1


class LocalController():
	def __init__(self, LEDs: Set["LED"]):
		self.LEDs = set(LEDs)

	def has_LED(self, LED: LED) -> bool:
		return LED in self.LEDS

	def has_LEDs(self, LEDs: List["LED"]) -> bool:
		return all([self.has_LED(LED) for LED in LEDs])

	def power_LED(self, LED: LED, power_state: bool):
		if not self.has_LED(LED):
			raise ValueError("Local controller can only control local LEDs")

		if power_state:
			LED.power_on()
		else:
			LED.power_off()

	def power_LEDs(self, LEDs: List["LED"], power_states: List[bool]):
		if len(power_states) != len(LEDs):
			raise ValueError("LEDs and power states must be equal length")

		for i, LED in enumerate(LEDs):
			self.power_LED(LED, power_states[i])


class LaneIntersection():
	def __init__(self, coord: Coord, LED: LED, lane: Lane):
		self.coord = coord
		self.LED = LED
		self.lane = lane 	# TODO: what can this be used for?


class Intersection():
	def __init__(self, id: int, local_controller: LocalController):
		self.id = id
		self.entry_lane_intersections, self.exit_lane_intersections = self.getLaneIntersections(id)
		self.lane_intersections = self.entry_lane_intersections + self.exit_lane_intersections
		self.local_controller = local_controller
		self.coords = self.getCoords(id)
		self.queue = Queue()

	@staticmethod
	def getCoords(id: int) -> Set["Coord"]:
		if id == 0:
			return set((Coord(5, 2), Coord(5, 3)))
		elif id == 1:
			return set((Coord(8, 2), Coord(8, 3))
		elif id == 2:
			return set((Coord(14, 1), Coord(14, 2), Coord(15, 1)))
		elif id == 3:
			return set((Coord(17, 2), Coord(17, 3), Coord(16, 3)))
		elif id == 4:
			return set((Coord(18, 8), Coord(19, 8)))
		elif id == 5:
			return set((Coord(15, 17), Coord(15, 18)))
		elif id == 6:
			return set((Coord(12, 16), Coord(12, 17)))
		elif id == 7:
			return set((Coord(7, 17), Coord(8, 17), Coord(8, 16)))
		elif id == 8:
			return set((Coord(5, 14), Coord(6, 14), Coord(5, 15)))
		elif id == 9:
			return set((Coord(4, 11), Coord(5, 11), Coord(5, 12), Coord(4, 12)))
		elif id == 10:
			return set((Coord(5, 5), Coord(6, 5)))

	

	@staticmethod
	def getLaneData(id: int) -> Tuple[List["LaneIntersection"], List["LaneIntersection"]]:
		if id == 0:
			return ([LaneIntersection(Coord(4, 2), LED((Coord(4, 2), Coord(5, 2))), Lane(1)), LaneIntersection(Coord(6, 2), LED((Coord(6, 2), Coord(5, 2))), Lane(12))],
					[LaneIntersection(Coord(4, 3), LED((Coord(4, 3), Coord(5, 3))), Lane(0)), LaneIntersection(Coord(5, 4), LED((Coord(5, 4), Coord(5, 3))), Lane(11))])
		elif id == 1:
			return ([LaneIntersection(Coord(8, 1), LED((Coord(8, 1), Coord(8, 2))), Lane(2)), LaneIntersection(Coord(9, 2), LED((Coord(9, 2), Coord(8, 2))), Lane(13)), LaneIntersection(Coord(8, 4), LED((Coord(8, 4), Coord(8, 3))), Lane(22))]],
					[LaneIntersection(Coord(7, 2), LED((Coord(7, 2), Coord(8, 2))), Lane(12)), LaneIntersection(Coord(9, 3), LED((Coord(9, 3), Coord(8, 3))), Lane(23))])
		elif id == 2:
			return ([LaneIntersection(Coord(13, 2), LED((Coord(13, 2), Coord(14, 2))), Lane(23)), LaneIntersection(Coord(15, 2), LED((Coord(15, 2), Coord(14, 2))), Lane(14))],
					[LaneIntersection(Coord(15, 0), LED((Coord(15, 0), Coord(15, 1))), Lane(3)), LaneIntersection(Coord(13, 1), LED((Coord(13, 1), Coord(14, 1))), Lane(13)), LaneIntersection(Coord(14, 3), LED((Coord(14, 3), Coord(14, 2))), Lane(24))]])
		elif id == 3:
			return ([LaneIntersection(Coord(18, 3), LED((Coord(18, 3), Coord(17, 3))), Lane(15)), LaneIntersection(Coord(15, 3), LED((Coord(15, 3), Coord(16, 3))), Lane(24))],
					[LaneIntersection(Coord(16, 2), LED((Coord(16, 2), Coord(17, 2))), Lane(14)), LaneIntersection(Coord(18, 2), LED((Coord(18, 2), Coord(17, 2))), Lane(4)), LaneIntersection(Coord(16, 4), LED((Coord(16, 4), Coord(16, 3))), Lane(25))]])
		elif id == 4:
			return ([LaneIntersection(Coord(18, 7), LED((Coord(18, 7), Coord(18, 8))), Lane(25)), LaneIntersection(Coord(19, 9), LED((Coord(19, 9), Coord(19, 8))), Lane(16))],
					[LaneIntersection(Coord(19, 7), LED((Coord(19, 7), Coord(19, 8))), Lane(15)), LaneIntersection(Coord(18, 9), LED((Coord(18, 9), Coord(18, 8))), Lane(26))])
		elif id == 5:
			return ([LaneIntersection(Coord(16, 17), LED((Coord(16, 17), Coord(15, 17))), Lane(26)), LaneIntersection(Coord(14, 18), LED((Coord(14, 18), Coord(15, 18))), Lane(17)), LaneIntersection(Coord(15, 19), LED((Coord(15, 19), Coord(15, 18))), Lane(5))],
					[LaneIntersection(Coord(14, 17), LED((Coord(14, 17), Coord(15, 17))), Lane(27)), LaneIntersection(Coord(16, 18), LED((Coord(16, 18), Coord(15, 18))), Lane(16))])
		elif id == 6:
			return ([LaneIntersection(Coord(13, 16), LED((Coord(13, 16), Coord(12, 16))), Lane(27)), LaneIntersection(Coord(11, 17), LED((Coord(11, 17), Coord(12, 17))), Lane(18))],
					[LaneIntersection(Coord(11, 16), LED((Coord(11, 16), Coord(12, 16))), Lane(28)), LaneIntersection(Coord(12, 18), LED((Coord(12, 18), Coord(12, 17))), Lane(17))])
		elif id == 7:
			return ([LaneIntersection(Coord(9, 16), LED((Coord(9, 16), Coord(8, 16))), Lane(28)), LaneIntersection(Coord(7, 16), LED((Coord(7, 16), Coord(7, 17))), Lane(19))],
					[LaneIntersection(Coord(8, 15), LED((Coord(8, 15), Coord(8, 16))), Lane(29)), LaneIntersection(Coord(7, 18), LED((Coord(7, 18), Coord(7, 17))), Lane(6)), LaneIntersection(Coord(9, 17), LED((Coord(9, 17), Coord(8, 17))), Lane(18))]])
		elif id == 8:
			return ([LaneIntersection(Coord(4, 14), LED((Coord(4, 14), Coord(5, 14))), Lane(20)), LaneIntersection(Coord(7, 14), LED((Coord(7, 14), Coord(6, 14))), Lane(29)), LaneIntersection(Coord(5, 16), LED((Coord(5, 16), Coord(5, 15))), Lane(7))],
					[LaneIntersection(Coord(6, 13), LED((Coord(6, 13), Coord(6, 14))), Lane(30)), LaneIntersection(Coord(4, 15), LED((Coord(4, 15), Coord(5, 15))), Lane(8)), LaneIntersection(Coord(6, 15), LED((Coord(6, 15), Coord(5, 15))), Lane(19))]])
		elif id == 9:
			return ([LaneIntersection(Coord(4, 10), LED((Coord(4, 10), Coord(4, 11))), Lane(21)), LaneIntersection(Coord(3, 12), LED((Coord(3, 12), Coord(4, 12))), Lane(9)), LaneIntersection(Coord(5, 13), LED((Coord(5, 13), Coord(5, 12))), Lane(30))],
					[LaneIntersection(Coord(5, 10), LED((Coord(5, 10), Coord(5, 11))), Lane(31)), LaneIntersection(Coord(3, 11), LED((Coord(3, 11), Coord(4, 11))), Lane(10)), LaneIntersection(Coord(4, 13), LED((Coord(4, 13), Coord(4, 12))), Lane(20))]])
		elif id == 10:
			return ([LaneIntersection(Coord(5, 4), LED((Coord(5, 4), Coord(5, 5))), Lane(11)), LaneIntersection(Coord(6, 6), LED((Coord(6, 6), Coord(6, 5))), Lane(31))],
					[LaneIntersection(Coord(5, 6), LED((Coord(5, 6), Coord(5, 5))), Lane(21)), LaneIntersection(Coord(7, 5), LED((Coord(7, 5), Coord(6, 5))), Lane(22))])

	def contains_coord(self, coord: Coord) -> bool:
		return coord in self.coords

	def is_occupied(self, grid: np.ndarray) -> bool:
		for coord in self.coords:
			if grid[coord.x, coord.y] == 1:
				return True

		return False
