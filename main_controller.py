from typing import List, Tuple
from threading import Thread
from multiprocessing import Process
from queue import Queue, PriorityQueue
from enum import Enum
import logging 
import time
import sys 

class Lane():
	NUM_LANES = 14
	ROUNDABOUT_INNER = 0
	ROUNDABOUT_OUTER = 1

	def __init__(self, num: int):
		if 0 <= num or num >= Person.NUM_LANES:
			raise ValueError("Lane num {} is out of range".format(num))
		self.num = num
		self.is_inner_roundabout = num == ROUNDABOUT_INNER
		self.is_outer_roundabout = num == ROUNDABOUT_OUTER
		self.is_roundabout = self.is_inner_roundabout or self.is_outer_roundabout
		self.is_to_dest = num % 2 == 0
		self.is_from_dest = num % 2 == 1
		self.is_dest = self.is_to_dest or self.is_from_dest


class Person():
	NUM_LANES = 15
	ROUNDABOUT_LANES = [1, 2]

	def __init__(self, x: int, y:int, lane: Lane):
		self.x = x
		self.y = y
		self.lane = lane


class LED():
	def __init__(self, x: int, y: int):
		self.x = x
		self.y = y
		self.is_on = False

	def light_on():
		time.sleep(0.0001)
		self.is_on = True

	def light_off():
		time.sleep(0.0001)
		self.is_on = False


class LaneIntersection():
	def __init__(self, x: int, y: int, LED: LED, lane: Lane, is_entry: bool):
		self.x = x
		self.y = y
		self.LED = LED
		self.lane = lane
		self.is_entry = is_entry
		self.is_exit = not is_entry


class Intersection():
	def __init__(self, num: int, lane_intersections: List["LaneIntersection"]):
		self.num = num
		self.lane_intersections = lane_intersections
		self.is_free = True


class IntersectionEvent():
	def __init__(self, person: Person, is_entry: bool, detection_time: float):
		self.person = person
		self.is_entry = is_entry
		self.is_exit = not is_entry
		self.detection_time = detection_time


class IntersectionQueueItem():
	def __init__(self, is_roundabout: bool, detection_time: float, lane_intersection_coord: Tuple[int, int]):
		self.is_roundabout = is_roundabout
		self.detection_time = detection_time
		self.lane_intersection_coord = lane_intersection_coord

		# priproity queue returns smallest element first, and tuple is compared by element
		# # int(True) = 1, int(False) = 0
		self.tuple_repr = (int(not is_roundabout), detection_time, lane_intersection_coord)

	def __lt__(self, other: "IntersectionQueueItem") -> bool:
		return self.tuple_repr < other.tuple_repr

	def __eq__(self, other: "IntersectionQueueItem") -> bool:
		return self.tuple_repr == other.tuple_repr

	def __gt__(self, other: "IntersectionQueueItem") -> bool:
		return self.tuple_repr > other.tuple_repr


class MainController(Thread):
	def __init__(self, breach_event_queue: Queue, intersection_event_queue: Queue, 
		intersections: List["Intersection"],
		LEDs: List["LED"]):

		Thread.__init__(self)
		self.breach_event_queue = breach_event_queue
		self.intersection_event_queue = intersection_event_queue
		self.LEDs = LEDs

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

		# pre compute some of the necessary stuffs to make thread run faster
		self.intersection_queues = dict()
		self.intersection_id_map = dict()
		self.intersection_lane_map = dict()
		self.lane_intersection_coord_map = dict()
		self.lane_intersection_allowable_map = dict()

		for intersection in intersections:
			# create queues for each intersection
			intersection_queues[intersection.num] = PriorityQueue()

			# create map from id to intersection
			intersection_id_map[intersection.num] = intersection

			# turn on all LEDs to block all lanes at start
			for lane_intersection in intersection.lane_intersections:
				lane_intersection.LED.light_on()

				# create map from lane intersection to intersection id
				lane_intersection_coord = (lane_intersection[0], lane_intersection[1])
				intersection_lane_map[lane_intersection_coord] = intersection.num

				# create map from lane intersection coordinate to lane intersection
				lane_intersection_coord_map[lane_intersection_coord] = lane_intersection

				# create map from lane intersection coord to allowable intersections
				lane_intersection_allowable_map[lane_intersection_coord] = self._get_allowable_lane_intersections(lane_intersection_coord)

	def _get_allowable_lane_intersections(self, lane_intersection_coord: Tuple[int, int]) -> List["LaneIntersection"]:
		this_lane_intersection = self.lane_intersection_coord_map[lane_intersection_coord]
		this_lane = this_lane_intersection.lane

		lane_intersections = self.intersection_id_map[self.intersection_lane_map[this_lane_intersection]].lane_insections

		allowable_lane_intersections = [this_lane_intersection]

		inner_roundabout_filter = lambda inter: not (inter.is_entry and (inter.lane.is_from_dest or inter.lane.is_outer_roundabout))
		outer_roundabout_filter = lambda inter: not (inter.is_entry and (inter.lane.is_from_dest or inter.lane.is_inner_roundabout))
		from_dest_filter = lambda inter: not (inter.is_entry and inter.lane.is_roundabout)
		to_dest_filter = lambda inter: not (inter.is_entry and (inter.lane.is_roundabout or inter.lane.is_from_dest))

		# only entry lane intersection has associated allowable exit lane intersections
		if this_lane_intersection.is_entry:

			if this_lane.is_inner_roundabout:
				allowable_lane_intersections.extend(filter(inner_roundabout_filter, lane_intersections))

			elif this_lane.is_outer_roundabout:
				allowable_lane_intersections.extend(filter(outer_roundabout_filter, lane_intersections))

			elif this_lane.is_from_dest:
				allowable_lane_intersections.extend(filter(from_dest_filter, lane_intersections))

			elif this_lane.is_to_dest:
				allowable_lane_intersections.extend(filter(to_dest_filter, lane_intersections))

		return allowable_lane_intersections

	def _handle_breach_event(self, breach_event):
		self.logger.info("Social distancing breach event: {}".format(str(breach_event)))

	def _handle_intersection_event(self, intersection_event: "IntersectionEvent"):
		# assume the intersection event is generated when the person is at the lane intersection
		lane_intersection_coord = (intersection_event.person.x, intersection_event.person.y)
		intersection_id = self.intersection_lane_map[lane_intersection_coord]

		if intersection_event.is_entry:
			detection_time = intersection_event.detection_time
			is_roundabout = intersection_event.person.lane.is_roundabout

			self.intersection_queues[intersection_id].put(IntersectionQueueItem(is_roundabout, detection_time, lane_intersection_coord))

			if not self.intersection_id_map[intersection_id].is_free:
				self.lane_intersection_coord_map[lane_intersection_coord].LED.light_on()

		else:
			self.intersection_id_map[intersection_id].is_free = True

			# turn on all LEDs at the intersection now that there's no one moving inside the intersection
			for lane_intersection in self.intersection_id_map[intersection_id].lane_intersections:
				if not lane_intersection.LED.is_on:
					lane_intersection.LED.light_on()


	def run(self):
		while True:
			if not self.breach_event_queue.empty():
				breach_event = self.breach_event_queue.get_nowait()
				Thread(target=self._handle_breach_event, args=([breach_event])).start()

			if not self.intersection_event_queue.empty():
				intersection_event = self.intersection_event_queue.get_nowait()
				self._handle_intersection_event(intersection_event)

			for intersection_id, q in self.intersection_queues.items():
				if not q.empty() and self.intersection_id_map[intersection_id].is_free:

					lane_intersection_coord = q.get().lane_intersection_coord
					for lane_intersection in self.lane_intersection_allowable_map[lane_intersection_coord]:
						lane_intersection.LED.light_off()

					self.intersection_id_map[intersection_id].is_free = False


def main():
	pass


if __name__ == "__main__":
	main()