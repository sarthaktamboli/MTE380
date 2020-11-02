from typing import List
from util import *
from multiprocessing import Process, Queue
import numpy as np
import random
import pygame

class Simulator:
	def __init__(self, floormap: np.ndarray, mainControllerData: Queue, simulatorData: Queue):
		self.emptyFloormap = floormap.copy()
		self.mainControllerData = mainControllerData
		self.simulatorData = simulatorData
		self.people = []

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
		screenHeight = (self.blockMargin + self.blockHeight) * self.emptyFloormap.shape[1] + self.blockMargin
		self.screen = pygame.display.set_mode([screenWidth, screenHeight])

	def __del__(self):
		# Exit pygame
		pygame.quit()

	def getPygameCoords(self, x: int, y: int) -> "Coord":
		return Coord((self.blockMargin + self.blockWidth) * x + self.blockMargin + (self.blockWidth / 2),
			    	 (self.blockMargin + self.blockHeight) * y + self.blockMargin + (self.blockHeight / 2))

	def drawBlock(self, color: Tuple[int], x: int, y: int):
		pygameCoords = self.getPygameCoords(x, y)
		blockLocation = (pygameCoords.x - (self.blockWidth / 2),
    					 pygameCoords.y - (self.blockHeight / 2),
    					 self.blockWidth,
    					 self.blockHeight)
		pygame.draw.rect(self.screen, color, blockLocation)

	def drawPerson(self, color: Tuple[int], x: int, y: int, dstLocID):
		personLocation = self.getPygameCoords(x, y)
		pygame.draw.circle(self.screen, color, personLocation, self.pointRadius)
		text = pygame.font.SysFont('arial', 10).render('%d' % dstLocID, True, self.white)
		rect = text.get_rect()
		rect.center = self.getPygameCoords(x, y)
		self.screen.blit(text, rect)

	def drawLED(self, color: Tuple[int], coordBounds: Tuple["Coords"], is_vertical: bool):
		pygameCoords1 = self.getPygameCoords(coordBounds[0].x, coordBounds[0].y)
		pygameCoords2 = self.getPygameCoords(coordBounds[1].x, coordBounds[1].y)
		midpoint = Coord((pygameCoords1.x + pygameCoords2.x) / 2, (pygameCoords1.y + pygameCoords2.y) / 2)
		LEDLocation = [(midpoint.x, midpoint.y - (self.blockHeight / 2)), (midpoint.x, midpoint.y + (self.blockHeight / 2))] if is_vertical else \
					  [(midpoint.x - (self.blockWidth / 2), midpoint.y), (midpoint.x + (self.blockWidth / 2), midpoint.y)]
		pygame.draw.lines(self.screen, color, False, LEDLocation, self.blockMargin)


	def run(self):
		while True:
			# Enqueue simulator data (list of coordinates)
			self.simulatorData.put([person.coord for person in self.people])

			# Get LEDs from main controller data
			LEDs = self.mainControllerData.get()

			# Set the screen background to black
			self.screen.fill(self.black)

			# Draw the empty floormap
			for x, y in np.ndindex(self.emptyFloormap.shape):
				color = self.floormapColors[self.emptyFloormap[x, y] + 1]
				self.drawBlock(color, x, y)

			# Draw the people
			for person in self.people:
				self.drawPerson(self.grey, person.coord.x, person.coord.y, person.dstLoc.locID)

			# Draw the LEDs
			blockedPaths = []
			for LED in LEDs:
				color = self.red if LED.is_on else self.green
				self.drawLED(color, LED.coordBounds, LED.is_vertical())

				# Append blocked paths if LED was turned on
				if color == self.red:
					blockedPaths.append(LED.coordBounds)

		    # Update display
			self.clock.tick(3)
			pygame.display.flip()

			# Each person gets a chance to advance if possible
			for person in reversed(self.people):	# Note: Iteration is in reverse since a person can be removed during an iteration
				currCoord = person.coord
				nextCoord = person.nextCoord()

				# Remove person if they have reached their destination, otherwise the person may advance
				if currCoord == person.dstLoc.dstCoord:
					self.people.remove(person)
					del person
				elif (currCoord, nextCoord) not in blockedPaths and (nextCoord, currCoord) not in blockedPaths:
					if not any([person.coord == nextCoord for person in self.people]):
						# 80% chance to advance if possible
						if np.random.rand() < 0.8:
							person.advance()

			# TODO: only do this if there is less than a certain number of people?
			# 20% chance to add a new person
			if np.random.rand() < 0.2:
				# Generate random srcLoc and dstLoc, making sure that there is currently nobody at that srcLoc
				srcLocID = random.choice([1, 2, 3, 4, 5, 6, 8])
				dstLocID = random.choice([1, 2, 3, 4, 5, 6, 7, 8]) if srcLocID != 8 else random.choice([1, 2, 3, 4, 5, 6, 7])
				if not any([person.coord == Location.getCoords(srcLocID)[0] for person in self.people]):
					if srcLocID != 8 or not any ([person.coord == Coord(18, 8) for person in self.people]):
						if srcLocID != 6 or not any([person.coord == Coord(12, 7) for person in self.people]):
							newPerson = Person(Location(srcLocID), Location(dstLocID))
							self.people.append(newPerson)

			# Shuffle list of people to change order of iteration
			random.shuffle(self.people)




'''
# Create a 2 dimensional array. A two dimensional
# array is simply a list of lists.
grid = []
for row in range(10):
    # Add an empty array that will hold each cell
    # in this row
    grid.append([])
    for column in range(10):
        grid[row].append(0)  # Append a cell
 
# Set row 1, cell 5 to one. (Remember rows and
# column numbers start at zero.)
grid[1][5] = 1
 
# Initialize pygame
pygame.init()
 
# Set the HEIGHT and WIDTH of the screen
WINDOW_SIZE = [255, 255]
screen = pygame.display.set_mode(WINDOW_SIZE)
 
# Set title of screen
pygame.display.set_caption("Array Backed Grid")
 
# Loop until the user clicks the close button.
done = False
 
# Used to manage how fast the screen updates
clock = pygame.time.Clock()
 
# -------- Main Program Loop -----------
while not done:
    for event in pygame.event.get():  # User did something
        if event.type == pygame.QUIT:  # If user clicked close
            done = True  # Flag that we are done so we exit this loop
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # User clicks the mouse. Get the position
            pos = pygame.mouse.get_pos()
            # Change the x/y screen coordinates to grid coordinates
            column = pos[0] // (WIDTH + MARGIN)
            row = pos[1] // (HEIGHT + MARGIN)
            # Set that location to one
            grid[row][column] = 1
            print("Click ", pos, "Grid coordinates: ", row, column)
 
    # Set the screen background
    screen.fill(BLACK)
 
    # Draw the grid
    for row in range(10):
        for column in range(10):
            color = WHITE
            if grid[row][column] == 1:
                color = GREEN
            pygame.draw.rect(screen,
                             color,
                             [(MARGIN + WIDTH) * column + MARGIN,
                              (MARGIN + HEIGHT) * row + MARGIN,
                              WIDTH,
                              HEIGHT])
 
    # Limit to 60 frames per second
    clock.tick(60)
 
    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
 
# Be IDLE friendly. If you forget this line, the program will 'hang'
# on exit.
pygame.quit()
'''