from util import *
from multiprocessing import Process, Queue

class MainController(Process):
	def __init__(self, intersections: List["Intersection"]):

		Process.__init__(self)
		self.intersections = intersections

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

	def run(self):
		while True:
			pass
	
