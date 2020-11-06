from typing import List
from util import *
from multiprocessing import Process, Queue
import numpy as np
import random
import pygame
import os

class Simulator:
	def __init__(self, floormap: np.ndarray, mainControllerData: Queue, simulatorData: Queue, debug: Optional[bool] = False):
		self.emptyFloormap = floormap.copy()
		self.mainControllerData = mainControllerData
		self.simulatorData = simulatorData
		self.debug = debug

		self.people = []
		self.peopleEntered = 0
		self.peopleExited = 0

		# Initialize pygame
		pygame.init()
		self.clock = pygame.time.Clock()

		# Define colors
		self.black  = (0x00, 0x00, 0x00)
		self.white  = (0xDD, 0xDD, 0xDD)
		self.grey   = (0x33, 0x33, 0x33)
		self.red    = (0xFF, 0x00, 0x00)
		self.green  = (0x00, 0xFF, 0x00)
		self.pink   = (0xFF, 0x77, 0x77)
		self.purple = (0xDD, 0xAF, 0xFF)
		self.blue   = (0x77, 0x77, 0xFF)
		self.cyan   = (0x77, 0xFF, 0xFF)
		self.yellow = (0xFF, 0xF8, 0x60)
		self.floormapColors = [self.white, self.pink, self.purple, self.cyan, self.blue, self.yellow]

		# Define block dimensions and margins
		self.blockWidth = 20
		self.blockHeight = 20
		self.blockMargin = 3

		# Define point dimensions
		self.pointRadius = 7

		# Set the dimensions of the screen
		screenWidth = (self.blockMargin + self.blockWidth) * self.emptyFloormap.shape[0] + self.blockMargin
		screenHeight = (self.blockMargin + self.blockHeight) * (self.emptyFloormap.shape[1] + 1) + self.blockMargin
		self.screen = pygame.display.set_mode([screenWidth, screenHeight])

	def __del__(self):
		# Exit pygame
		pygame.quit()

	def getPygameCoords(self, x: int, y: int) -> "Coord":
		return Coord((self.blockMargin + self.blockWidth) * x + self.blockMargin + (self.blockWidth / 2),
			    	 (self.blockMargin + self.blockHeight) * (y + 1) + self.blockMargin + (self.blockHeight / 2))

	def drawBlock(self, color: Tuple[int], x: int, y: int):
		pygameCoords = self.getPygameCoords(x, y)
		blockLocation = (pygameCoords.x - (self.blockWidth / 2),
    					 pygameCoords.y - (self.blockHeight / 2),
    					 self.blockWidth,
    					 self.blockHeight)
		pygame.draw.rect(self.screen, color, blockLocation)

	def drawPerson(self, color: Tuple[int], x: int, y: int, dstLocID: int):
		personLocation = self.getPygameCoords(x, y)
		pygame.draw.circle(self.screen, color, personLocation, self.pointRadius)
		self.drawText("%d" % dstLocID, 10, self.white, x, y)

	def drawLED(self, color: Tuple[int], coordBounds: Tuple["Coords"], is_vertical: bool):
		pygameCoords1 = self.getPygameCoords(coordBounds[0].x, coordBounds[0].y)
		pygameCoords2 = self.getPygameCoords(coordBounds[1].x, coordBounds[1].y)
		midpoint = Coord((pygameCoords1.x + pygameCoords2.x) / 2, (pygameCoords1.y + pygameCoords2.y) / 2)
		LEDLocation = [(midpoint.x, midpoint.y - (self.blockHeight / 2)), (midpoint.x, midpoint.y + (self.blockHeight / 2))] if is_vertical else \
					  [(midpoint.x - (self.blockWidth / 2), midpoint.y), (midpoint.x + (self.blockWidth / 2), midpoint.y)]
		pygame.draw.lines(self.screen, color, False, LEDLocation, self.blockMargin)

	def drawText(self, text: str, size: int, color: Tuple[int], x: int, y: int, bold: bool=False, anchor: str='center'):
		text = pygame.font.SysFont('arial', size, bold=bold).render(text, True, color)
		rect = text.get_rect()
		center = self.getPygameCoords(x, y)
		if anchor == 'center':
			rect.center = center
		elif anchor == 'left':
			rect.center = (center.x + (rect.width / 2), center.y)
		elif anchor == 'right':
			rect.center = (center.x - (rect.width / 2), center.y)
		self.screen.blit(text, rect)

	def run(self):
		while True:
			skipLoop = True
			for event in pygame.event.get():  # User did something
				if event.type == pygame.QUIT:  # If user clicked close
					pygame.quit()
					os._exit(1)
				if event.type == pygame.MOUSEBUTTONDOWN:
					skipLoop = False
			if self.debug and skipLoop:
				continue


			# Backend
			# Enqueue simulator data (list of coordinates)
			self.simulatorData.put([person.coord for person in self.people])

			# Get LEDs from main controller data
			LEDs = self.mainControllerData.get()

			blockedPaths = []
			for LED in LEDs:
				# Append blocked paths if LED was turned on
				if LED.is_on:
					blockedPaths.append(LED.coordBounds)

			# Each person advances if possible
			advancedPeople = []
			for person in reversed(self.people):	# Note: Iteration is in reverse since a person can be removed during an iteration
				currCoord = person.coord
				nextCoord = person.nextCoord()

				# Remove person if they have reached their destination, otherwise the person may advance
				if currCoord == person.dstLoc.dstCoord:
					self.people.remove(person)
					del person
					self.peopleExited += 1
				else:
					intoIntersection = self.emptyFloormap[currCoord.x, currCoord.y] != 4 and self.emptyFloormap[nextCoord.x, nextCoord.y] == 4
					outOfIntersection = self.emptyFloormap[currCoord.x, currCoord.y] == 4 and self.emptyFloormap[nextCoord.x, nextCoord.y] != 4
					if intoIntersection:
						if (currCoord, nextCoord) not in blockedPaths:
							person.advance()
							advancedPeople.append(person)
					elif outOfIntersection:
						if (nextCoord, currCoord) not in blockedPaths:
							person.advance()
							advancedPeople.append(person)
						else:
							person.wait(blockedPaths)
					else:
						if not any([person.coord == nextCoord for person in self.people]):
							person.advance()
							advancedPeople.append(person)

			# TODO: only do this if there is less than a certain number of people?
			newPeople = []
			x = len(self.people)
			# quadratic probability, 1 when x = 0, 0 when x = 40
			probability = ((x ** 2) / 1600) - (x / 20) + 1
			if x < 40: #np.random.rand() < probability:
				# Generate random srcLoc and dstLoc, making sure that there is currently nobody at that srcLoc
				srcLocID = random.choice([1, 2, 3, 4, 5, 6, 8])
				dstLocID = random.choice([1, 2, 3, 4, 5, 6, 7, 8]) if srcLocID != 8 else random.choice([1, 2, 3, 4, 5, 6, 7])
				if not any([person.coord == Location.getCoords(srcLocID)[0] for person in (self.people + newPeople)]):
					if srcLocID != 8 or not any ([person.coord == Coord(18, 8) for person in (self.people + newPeople)]):
						if srcLocID != 6 or not any([person.coord == Coord(12, 17) for person in (self.people + newPeople)]):
							newPerson = SmartPerson(Location(srcLocID), Location(dstLocID), self.emptyFloormap, blockedPaths)
							newPeople.append(newPerson)
							self.peopleEntered += 1

			if len(advancedPeople) == 0:
				# Add new people to list of people
				self.people += newPeople

				# Shuffle list of people to change order of iteration
				random.shuffle(self.people)

				continue

			# Frontend
			for animationLoop in range(1, 21):
				# Set the screen background to black
				self.screen.fill(self.black)

				# Draw the empty floormap
				for x, y in np.ndindex(self.emptyFloormap.shape):
					color = self.floormapColors[self.emptyFloormap[x, y] + 1]
					self.drawBlock(color, x, y)

				# Draw dstLoc texts
				for i in range(1, 9):
					dstCoord = Location.getCoords(i)[1]
					self.drawText("%d" % i, 15, self.grey, dstCoord.x, dstCoord.y, bold=True)

				# Display people statistics
				if len(self.people) + len(newPeople) != self.peopleEntered - self.peopleExited:
					raise ValueError("Inconsistency in people statistics")
				self.drawText("People Count: %d" % (len(self.people) + len(newPeople)), 17, self.white, 0, -1, bold=True, anchor='left')
				self.drawText("People Entered: %d" % self.peopleEntered, 17, self.white, 9.5, -1, bold=True, anchor='center')
				self.drawText("People Exited: %d" % self.peopleExited, 17, self.white, 19, -1, bold=True, anchor='right')

				# Draw the LEDs
				for LED in LEDs:
					color = self.red if LED.is_on else self.green
					self.drawLED(color, LED.coordBounds, LED.is_vertical())

				# Draw all previously existing people
				for person in self.people:
					if person not in advancedPeople:
						self.drawPerson(self.grey, person.coord.x, person.coord.y, person.dstLoc.locID)
					else:
						oldCoordX, oldCoordY = person.prevCoord()
						newCoordX, newCoordY = person.coord
						currCoordX = oldCoordX + ((newCoordX - oldCoordX) * animationLoop / 20)
						currCoordY = oldCoordY + ((newCoordY - oldCoordY) * animationLoop / 20)
						self.drawPerson(self.grey, currCoordX, currCoordY, person.dstLoc.locID)

				# Draw new people in last iteration
				if animationLoop == 20:
					for person in newPeople:
						self.drawPerson(self.grey, person.coord.x, person.coord.y, person.dstLoc.locID)

				self.clock.tick(40)
				pygame.display.flip()

			# Add new people to list of people
			self.people += newPeople

			# Shuffle list of people to change order of iteration
			random.shuffle(self.people)
