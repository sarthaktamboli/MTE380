from typing import List, Tuple, Set, Optional
from queue import Queue
from collections import namedtuple
import numpy as np

Coord = namedtuple('Coord', ['x', 'y'])

class Location():
	def__init__(self, locID: int):
		self.locID = locID
		self.coord = getCoord()

	def getCoord(self) -> "Coord":
		# TODO: hardcode

class Person():
	def __init__(self, srcLoc: Location, dstLoc: Location):
		if srcLoc == dstLoc:
			raise ValueError("Source and destination must be different")
		self.srcLoc = srcLoc
		self.dstLoc = dstLoc
		self.coord = srcLoc.coord
		self.path = getPath()
		self.pathIdx = 0

	def getPath(self) -> List["Coord"]:
		# TODO: hardcode

	def nextCoord(self) -> Coord:
		return self.path[self.pathIdx + 1]

	def advance(self):
		self.coord = self.nextCoord()
		self.pathIdx += 1


class Lane():
	LABELS = {"1in", "1out", "2in", "2out", "3in", "3out", "4in", "4out", "5in", "5out", "6in", "6out", "7in", "innerRing", "outerRing"}
	
	def __init__(self, label: str):
		if label not in Lane.LABELS:
			raise ValueError("Lane label {} is not valid".format(label))
		self.label = label
		self.is_inner_roundabout = label == "innerRing"
		self.is_outer_roundabout = label == "outerRing"
		self.is_roundabout = self.is_inner_roundabout or self.is_outer_roundabout
		self.is_to_dest = label.endswith("in")
		self.is_from_dest = label.endswith("out")
		self.is_dest = self.is_to_dest or self.is_from_dest

	@staticmethod
	def get_allowable_labels() -> Set[str]:
		return Lane.LABELS


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
		self.lane = lane


class Intersection():
	def __init__(self, label: str, entry_lane_intersections: List["LaneIntersection"], 
		exit_lane_intersections: List["LaneIntersection"],
		local_controller: LocalController,
		coords: Set["Coord"]):

		self.label = label
		self.entry_lane_intersections = entry_lane_intersections
		self.exit_lane_intersections = exit_lane_intersections
		self.lane_intersections = entry_lane_intersections + exit_lane_intersections
		self.local_controller = local_controller
		self.coords = set(coords)
		self.queue = Queue()

	def contains_coord(self, coord: Coord) -> bool:
		return coord in self.coords

	def is_occupied(self, grid: np.ndarray) -> bool:
		for coord in self.coords:
			if grid[coord.x, coord.y] == 1:
				return True

		return False

