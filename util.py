from typing import List, Tuple, Set, Optional
from queue import Queue
from collections import namedtuple

Coord = namedtuple('Coord', ['x', 'y'])

class Lane():
	LABELS = {"1in", "1out", "2in", "2out", "3in", "3out", "4in", "4out", "5in", "5out", "6in", "6out", "7in", "innerRing", "outerRing"}
	
	def __init__(self, label: str):
		if label not in Lane.LABELS:
			raise ValueError("Lane label {} is not valid".format(label))
		self.label = label
		self.is_inner_roundabout = label == "innerRing"
		self.is_outer_roundabout = label == "outerRing"
		self.is_roundabout = self.is_inner_roundabout or self.is_outer_roundabout
		self.is_to_dest = "in" in label
		self.is_from_dest = "out" in label
		self.is_dest = self.is_to_dest or self.is_from_dest

	@staticmethod
	def get_allowable_labels() -> Set[str]:
		return Lane.LABELS


class LED():
	def __init__(self, coord: Coord):
		self.coord = coord
		self.is_on = False

	def power_on():
		time.sleep(0.0001)
		self.is_on = True

	def power_off():
		time.sleep(0.0001)
		self.is_on = False


class LocalController():
	def __init__(self, LEDs: List["LED"]):
		self.LEDs = LEDs
		self.LED_coord_map = dict()

		for LED in LEDs:
			self.LED_coord_map[LED.coord] = LED

	def has_LED(self, coord: Coord) -> bool:
		return coord in self.LED_coord_map

	def has_LEDs(self, coords: List["Coord"]) -> bool:
		return all([self.has_LED(coord) for coord in coords])

	def power_LED(self, coord: Coord, power_on: bool):
		if self.has_LED(coord):
			if power_state:
				self.LED_coord_map[coord].power_on()
			else:
				self.LED_coord_map[coord].power_off()

	def power_LEDs(self, coords: List["Coord"], power_states: List[bool]):
		if len(power_states) != len(coords):
			raise ValueError("LED coordinates and power states must be equal length")

		for i, coord in enumerate(coords):
			self.power_LED(coord, power_states[i])


class LaneIntersection():
	def __init__(self, coord: Coord, LED: LED, lane: Lane):
		self.coord = coord
		self.LED = LED
		self.lane = lane


class Intersection():
	def __init__(self, label: str, entry_lane_intersections: List["LaneIntersection"], 
		exit_lane_intersections: List["LaneIntersection"],
		local_controller: LocalController):

		self.label = label
		self.entry_lane_intersections = entry_lane_intersections
		self.exit_lane_intersections = exit_lane_intersections
		self.lane_intersections = entry_lane_intersections + exit_lane_intersections
		self.queue = Queue()
		self.local_controller = LocalController

		self.lane_intersection_coords = [inter.coord for inter in self.lane_intersections]

	# adopted from https://www.geeksforgeeks.org/how-to-check-if-a-given-point-lies-inside-a-polygon/#:~:text=1)%20Draw%20a%20horizontal%20line,true%2C%20then%20point%20lies%20outside.
	def contains_coord(self, coord: Coord) -> bool:

		# Given three colinear points p, q, r, the function checks if point q lies on 
		# line segment 'pr' 
		def _onSegment(p: Coord, q: Coord, r: Coord) -> bool:
			if (q.x <= max(p.x, r.x) and q.x >= min(p.x, r.x) and q.y <= max(p.y, r.y) and q.y >= min(p.y, r.y)):
				return True 
			return False 

		# To find orientation of ordered triplet (p, q, r). 
		# The function returns following values 
		# 0 --> p, q and r are colinear 
		# 1 --> Clockwise 
		# 2 --> Counterclockwise 

		def _orientation(p: Coord, q: Coord, r: Coord) -> int:
			val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)
			if (val == 0):
				return 0
			return 1 if val>0 else 2 

		# The function that returns true if line segment 'p1q1' and 'p2q2' intersect.
		def _doIntersect(p1: Coord, q1: Coord, p2: Coord, q2: Coord) -> bool:
			# Find the four orientations needed for general and special cases 
			o1 = _orientation(p1, q1, p2)
			o2 = _orientation(p1, q1, q2)
			o3 = _orientation(p2, q2, p1)
			o4 = _orientation(p2, q2, q1)

			# General case
			if (o1 != o2 and o3 != o4):
				return True
			
			# Special Cases
			# p1, q1 and p2 are colinear and p2 lies on segment p1q1 
			if (o1 == 0 and _onSegment(p1, p2, q1)):
				return True

			# p1, q1 and p2 are colinear and q2 lies on segment p1q1 
			if (o2 == 0 and _onSegment(p1, q2, q1)):
				return True

			# p2, q2 and p1 are colinear and p1 lies on segment p2q2 
			if (o3 == 0 and _onSegment(p2, p1, q2)):
				return True

			# p2, q2 and q1 are colinear and q1 lies on segment p2q2
			if (o4 == 0 and _onSegment(p2, q1, q2)):
				return True

			return False # Doesn't fall in any of the above cases 

		# Returns true if the point p lies inside the polygon[] with n vertices 
		def _isInside(polygon: List[Coord], p: Coord) -> bool: 
			#There must be at least 3 vertices in polygon
			n = len(polygon)

			if (n < 3):
				return False
			
			# Create a point for line segment from p to infinite 
			extream = Coord(x=float('inf'), y=p.y)
			
			# Count intersections of the above line with sides of polygon 
			count = 0
			i = 0
			while True:
				next = (i + 1) % n; 

				# Check if the line segment from 'p' to 'extreme' intersects 
				# with the line segment from 'polygon[i]' to 'polygon[next]' 
				if _doIntersect(polygon[i], polygon[next], p, extreme):
					# If the point 'p' is colinear with line segment 'i-next', 
					# then check if it lies on segment. If it lies, return true, 
					# otherwise false 
					if _orientation(polygon[i], p, polygon[next]) == 0:
						return _onSegment(polygon[i], p, polygon[next]) 

					count += 1

				i = next
				if i == 0:
					break

			#Return true if count is odd, false otherwise 
			return (count % 2 == 1)

		return _isInside(self.lane_intersection_coords, coord)
