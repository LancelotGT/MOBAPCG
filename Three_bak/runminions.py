import sys, pygame, math, numpy, random, time, copy
from pygame.locals import *

from constants import *
from utils import *
from core import *
from astarnavigator import *
from agents import *
from moba import *
from MyMinion import *



############################
### SET UP WORLD

dims = (1200, 1200)

obstacles = [[(400, 100), (1100, 100), (1100, 800), (1010, 900), (990, 900), (900, 750), (900, 500), (700, 300), (450, 300), (300, 210), (300, 190)]
			 ]

mirror = map(lambda poly: map(lambda point: (dims[0]-point[0], dims[1]-point[1]), poly), obstacles)

obstacles = obstacles + mirror

obstacles = obstacles + [[(550, 570), (600, 550), (660, 570), (650, 630), (600, 650), (540, 630)]]

###########################
### Minion Subclasses

class MyHumanMinion(MyMinion):
	
	def __init__(self, position, orientation, world, image = NPC, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = SmallBullet):
		MyMinion.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)

class MyAlienMinion(MyMinion):
	
	def __init__(self, position, orientation, world, image = JACKAL, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = SmallBullet):
		MyMinion.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)

########################

world = MOBAWorld(SEED, dims, dims, 2, 60)
agent = Hero((SCREEN[0]/2, SCREEN[1]/2), 0, world)
agent.team = 0
world.setPlayerAgent(agent)
world.initializeTerrain(obstacles, (0, 0, 0), 4)
agent.setNavigator(Navigator())
world.debugging = True


nav = AStarNavigator()
nav.setWorld(world)


b1 = Base(BASE, (25, 25), world, 1, MyHumanMinion)
b1.setNavigator(nav)
world.addBase(b1)

t11 = Tower(TOWER, (200, 50), world, 1)
world.addTower(t11)
t12 = Tower(TOWER, (50, 200), world, 1)
world.addTower(t12)

b2 = Base(BASE, (1075, 1075), world, 2, MyAlienMinion)
b2.setNavigator(nav)
world.addBase(b2)

t21 = Tower(TOWER, (1100, 950), world, 2)
world.addTower(t21)

t22 = Tower(TOWER, (950, 1100), world, 2)
world.addTower(t22)


'''
b1 = Base(CRATE, (500, 485), world, 1, 10)
b1.setNavigator(nav)
world.addBase(b1)
b1.addBuildProfile(RTSGatherer, tuple([10]))
b1.addBuildProfile(RTSHunter, tuple([25]))

b2 = Base(CRATE, (180, 75), world, 2, 10)
b2.setNavigator(nav)
world.addBase(b2)
b2.addBuildProfile(RTSGatherer, tuple([10]))
b2.addBuildProfile(RTSHunter, tuple([25]))


ai1 = SimpleRTSPlayer(1, world)
ai1.setBase(b1)

ai2 = WeenieHoardRTSPlayer(2, world)
ai2.setBase(b2)

world.addAIPlayer(ai1)
world.addAIPlayer(ai2)
ai1.start()
ai2.start()
'''
world.makePotentialGates()

world.run()
