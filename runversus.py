import os, sys, pygame, math, numpy, random, time, copy, compileall
from pygame.locals import *

from constants import *
from utils import *
from core import *
from agents import *
from moba import *
from astarnavigator import *

import imp

def importHero2(classFile):
	if os.path.exists(classFile + "/MyHero.py"):
		sys.path.insert(0, classFile)
		compileall.compile_dir(classFile)
		
	if os.path.exists(classFile + "/MyHero.pyc"):
		hero = imp.load_compiled('hero2_module', classFile + "/MyHero.pyc")
		return hero
	else:
		sys.exit("ERROR: Either no MyHero.py file found at " + classFile + " or MyHero.py compilation failed.")

def importMinion2(classFile):
	if os.path.exists(classFile + "/MyMinion.py"):
		sys.path.insert(0, classFile)
		compileall.compile_dir(classFile)
		
	if os.path.exists(classFile + "/MyMinion.pyc"):
		minion = imp.load_compiled('minion2_module', classFile + "/MyMinion.pyc")
		return minion
	else:
		sys.exit("ERROR: Either no MyMinion.py file found at " + classFile + " or MyMinion.py compilation failed.")

directory1 = ""
directory2 = ""

if len(sys.argv) < 3:
	print "Usage:\t\tpython runversus.py directory_name_1 directory_name_2"
	print "Results in simulation of directory_name_1's Heroes and Minions versus directory_name_2's Heroes and Minions"
	print "example directory names: \"One\", \"Two\", \"Three\", (baseline heroes & minions) and \"Mine\" (custom hero & minions)."
	print "default:\tpython runversus.py \"Mine\" \"Mine\"\n"
	directory1 = "Mine"
	directory2 = "Mine"
else:
	directory1 = sys.argv[1]
	directory2 = sys.argv[2]

# use the given directorys' classfiles
classFile1 = "./" + directory1
classFile2 = "./" + directory2

nav1 = AStarNavigator()
nav2 = AStarNavigator()

# imp.reload(moba)
# mod = reload(sys.modules['moba']) #use imp.reload for Python 3  
# vars().update(mod.__dict__)

# import hero modules
hero2 = importHero2(classFile2)

# import minion modules
minion2 = importMinion2(classFile2)

# get hero classes from hero modules
heroclass2 = getattr(hero2, "MyHero")
# get minion classes from minion modules
minionclass2 = getattr(minion2, "MyMinion")


########################
### Minion Subclasses

class MyAlienMinion(minionclass2):
	
	def __init__(self, position, orientation, world, image = JACKAL, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = SmallBullet):
		minionclass2.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)


########################
### Hero Subclasses

class MyAlienHero(heroclass2):
	def __init__(self, position, orientation, world, image = ELITE, speed = SPEED, viewangle = 360, hitpoints = HEROHITPOINTS, firerate = FIRERATE, bulletclass = BigBullet, dodgerate = DODGERATE, areaeffectrate = AREAEFFECTRATE, areaeffectdamage = AREAEFFECTDAMAGE):
		heroclass2.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass, dodgerate, areaeffectrate, areaeffectdamage)

########################


############################
### SET UP WORLD

dims = (1200, 1200)

#obstacles = [[(250, 150), (600, 160), (590, 400), (260, 390)],
#			 [(800, 170), (1040, 140), (1050, 160), (1040, 500), (810, 310)]]
obstacles = [[(400, 150), (850, 150), (900, 300), (1050, 350), (1050, 800), (1010, 900), (990, 900), (900, 750), (900, 500), (700, 300), (450, 300), (350, 210), (350, 190)]
			 ]


mirror = map(lambda poly: map(lambda point: (dims[0]-point[0], dims[1]-point[1]), poly), obstacles)

obstacles = obstacles + mirror



world = MOBAWorld(SEED, dims, dims, 1, 60)
agent = Hero((600, 500), 0, world, ELITE)
world.setPlayerAgent(agent)
world.initializeTerrain(obstacles, (0, 0, 0), 4)
agent.setNavigator(Navigator())
agent.team = 2
world.debugging = True

# create AStarNavigator using student's astar module
nav1.setWorld(world)

b1 = TDBase(BASE, (25, 25), world, 1, BUILDRATE)
b1.setNavigator(nav1)
world.addBase(b1)

t11 = Tower(TOWER, (200, 50), world, 1)
world.addTower(t11)
t12 = Tower(TOWER, (50, 200), world, 1)
world.addTower(t12)
t13 = Tower(TOWER, (125, 125), world, 1)
world.addTower(t13)
t14 = Tower(TOWER, (300, 50), world, 1)
world.addTower(t14)
t15 = Tower(TOWER, (50, 300), world, 1)
world.addTower(t15)
# t16 = Tower(TOWER, (200, 200), world, 1)
# world.addTower(t16)
# t162 = Tower(TOWER, (250, 250), world, 1)
# world.addTower(t162)
# t17 = Tower(TOWER, (300, 300), world, 1)
# world.addTower(t17)

# create AStarNavigator using student's astar module
nav2.setWorld(world)

b2 = Base(BASE, (1075, 1075), world, 2, MyAlienMinion, MyAlienHero, BUILDRATE)
b2.setNavigator(nav2)
world.addBase(b2)

# t21 = Tower(TOWER, (1100, 950), world, 2)
# world.addTower(t21)
# t22 = Tower(TOWER, (950, 1100), world, 2)
# world.addTower(t22)


#hero1 = MyHumanHero((125, 125), 0, world)
#hero1.setNavigator(cloneDynamicAStarNavigator(astar1, nav1))
#hero1.team = 1
#world.addNPC(hero1)
# hero2 = MyAlienHero((1025, 1025), 0, world)
# hero2.setNavigator(AStarNavigator())
# hero2.team = 2
# world.addNPC(hero2)

world.makePotentialGates()

# hero2.start()

world.run()
