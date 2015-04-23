import sys, pygame, math, numpy, random, time, copy
from pygame.locals import * 

from constants import *
from utils import *
from core import *
from mycreatepathnetwork import *
from mynavigatorhelpers import *


###############################
### AStarNavigator
###
### Creates a path node network and implements the FloydWarshall all-pairs shortest-path algorithm to create a path to the given destination.
			
class AStarNavigator(Navigator):

	def __init__(self):
		Navigator.__init__(self)
		

	### Create the pathnode network and pre-compute all shortest paths along the network.
	### self: the navigator object
	### world: the world object
	def createPathNetwork(self, world):
		self.pathnodes, self.pathnetwork, self.navmesh = myCreatePathNetwork(world, self.agent)
		return None
		
	### Finds the shortest path from the source to the destination using A*.
	### self: the navigator object
	### source: the place the agent is starting from (i.e., it's current location)
	### dest: the place the agent is told to go to
	def computePath(self, source, dest):
		### Make sure the next and dist matricies exist
		if self.agent != None and self.world != None: 
			self.source = source
			self.destination = dest
			### Step 1: If the agent has a clear path from the source to dest, then go straight there.
			###   Determine if there are no obstacles between source and destination (hint: cast rays against world.getLines(), check for clearance).
			###   Tell the agent to move to dest
			### Step 2: If there is an obstacle, create the path that will move around the obstacles.
			###   Find the pathnodes closest to source and destination.
			###   Create the path by traversing the self.next matrix until the pathnode closes to the destination is reached
			###   Store the path by calling self.setPath()
			###   Tell the agent to move to the first node in the path (and pop the first node off the path)
			if clearShot(source, dest, self.world.getLines(), self.world.getPoints(), self.agent):
				self.agent.moveToTarget(dest)
			else:
				start = findClosestUnobstructed(source, self.pathnodes, self.world.getLinesWithoutBorders())
				end = findClosestUnobstructed(dest, self.pathnodes, self.world.getLinesWithoutBorders())
				if start != None and end != None:
					newnetwork = unobstructedNetwork(self.pathnetwork, self.world.getGates())
					closedlist = []
					path, closedlist = astar(start, end, newnetwork)
					if path is not None and len(path) > 0:
						path = shortcutPath(source, dest, path, self.world, self.agent)
						self.setPath(path)
						if self.path is not None and len(self.path) > 0:
							first = self.path.pop(0)
							self.agent.moveToTarget(first)
		return None
		
	### Called when the agent gets to a node in the path.
	### self: the navigator object
	def checkpoint(self):
		myCheckpoint(self)
		return None

	### This function gets called by the agent to figure out if some shortcutes can be taken when traversing the path.
	### This function should update the path and return True if the path was updated.
	def smooth(self):
		return mySmooth(self)

	def update(self, delta):
		myUpdate(self, delta)


def unobstructedNetwork(network, worldLines):
	newnetwork = []
	for l in network:
		hit = rayTraceWorld(l[0], l[1], worldLines)
		if hit == None:
			extremity = False
			for gate in worldLines :
				if (minimumDistance(gate, l[0]) == 0) or (minimumDistance(gate, l[1]) == 0) :
					extremity = True
					break
			if not extremity :
				newnetwork.append(l)

	return newnetwork



def astar(init, goal, network):
	path = []
	closed = []


	gValues = dict([(init, 0)])
	fValues = dict([(init, distance(init, goal))])
	came_from = dict()

	current = init

	while (current != goal) :

		closed.append(current)

		if (len(fValues)==0) :
			return path, closed

		current = fValues.keys()[0]
		for node, value in fValues.iteritems() :
			if (value < fValues[current]) :
				current = node

		for theEdge in network :
			if (theEdge[0] == current) :
				if not (theEdge[1] in closed) :
					gValue = gValues[current] + distance(current, theEdge[1])
					if (not (theEdge[1] in gValues)) or (gValue < gValues[theEdge[1]]) :
						gValues[theEdge[1]] = gValue
						fValues[theEdge[1]] = gValue + distance(theEdge[1], goal)
						came_from[theEdge[1]] = current

			elif (theEdge[1] == current) :
				if not (theEdge[0] in closed) :
					gValue = gValues[current] + distance(current, theEdge[0])
					if (not (theEdge[0] in gValues)) or (gValue < gValues[theEdge[0]]) :
						gValues[theEdge[0]] = gValue
						fValues[theEdge[0]] = gValue + distance(theEdge[1], goal)
						came_from[theEdge[0]] = current


		fValues.pop(current)
		gValues.pop(current)

	path.append(current)
	while (current!=init) :
		current = came_from[current]
		path.insert(0, current)	

	return path, closed

	


def myUpdate(nav, delta):

	if nav.path != None :
		for dest in nav.path :
			if not(rayTraceWorld(nav.agent.getLocation(), dest, nav.world.getGates()) == None) :
				nav.agent.stopMoving()
	elif not(rayTraceWorld(nav.agent.getLocation(), nav.destination, nav.world.getGates()) == None) :
		nav.agent.stopMoving()

	return None



def myCheckpoint(nav):

	return None

