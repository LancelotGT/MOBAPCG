import sys, pygame, math, numpy, random, time, copy
from pygame.locals import * 

from constants import *
from utils import *
from core import *

### Returns true if the agent can get from p1 to p2 directly without running into an obstacle.
### p1: the current location of the agent
### p2: the destination of the agent
### worldLines: all the lines in the world
### agent: the Agent object
def clearShot(p1, p2, worldLines, worldPoints, agent):
	### YOUR CODE GOES BELOW HERE ###
	clearShot = True

	if not(rayTraceWorld(p1, p2, worldLines) == None) :
		clearShot = False

	else :
		for point in worldPoints :
			line = (p1, p2)
			if (minimumDistance(line, point) < 2.3*agent.getRadius()) :
				clearShot = False
				break

	### YOUR CODE GOES ABOVE HERE ###
	return clearShot


### This function optimizes the given path and returns a new path
### source: the current position of the agent
### dest: the desired destination of the agent
### path: the path previously computed by the Floyd-Warshall algorithm
### world: pointer to the world
def shortcutPath(source, dest, path, world, agent):
	### YOUR CODE GOES BELOW HERE ###

	i = 0

	while (i < len(path)) :

		if i != 0 :
			previousNode = path[i-1]
		else :
			previousNode = source
		if i != len(path)-1 :
			nextNode = path[i+1]
		else :
			nextNode = dest

		if clearShot(previousNode, nextNode, world.getLines(), world.getPoints(), agent) :
			path.remove(path[i])
		else :
			i += 1

	### YOUR CODE GOES BELOW HERE ###
	return path



### This function changes the move target of the agent if there is an opportunity to walk a shorter path.
### This function should call nav.agent.moveToTarget() if an opportunity exists and may also need to modify nav.path.
### nav: the navigator object
### This function returns True if the moveTarget and/or path is modified and False otherwise
def mySmooth(nav):
	### YOUR CODE GOES BELOW HERE ###

	pathModif = False

	if not(nav.path == None)  :

		if clearShot(nav.agent.getLocation(), nav.destination, nav.world.getLines(), nav.world.getPoints(), nav.agent) :
			nav.agent.moveToTarget(nav.destination)
			nav.path = []
			pathModif = True

		if (len(nav.path)>0) :
			dest = nav.path[0]
			for i in range(0, 4) :
				subDest = ((i*nav.agent.moveTarget[0] + (4-i)*dest[0])/4 , (i*nav.agent.moveTarget[1] + (4-i)*dest[1])/4 )
				if clearShot(nav.agent.getLocation(), subDest, nav.world.getLines(), nav.world.getPoints(), nav.agent) :
					nav.agent.moveToTarget(subDest)
					pathModif = True
					if i == 0 :
						nav.path.pop(0)
					break

	### YOUR CODE GOES ABOVE HERE ###
	return pathModif



