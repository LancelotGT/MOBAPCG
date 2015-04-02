import os, sys, pygame, math, numpy, random, time, copy, compileall
from pygame.locals import *

from constants import *
from utils import *
from core import *
from agents import *

import imp

def importAStar1(classFile):
	if os.path.exists(classFile + "/astarnavigator.pyc"):
		print "Custom AStarNavigator1"
		sys.path.insert(0, classFile)
		compileall.compile_dir(classFile)
		astar = imp.load_compiled('astar1_module', classFile + "/astarnavigator.pyc")
	else:
		print "Default AStarNavigator1"
		compileall.compile_dir("./One/")
		sys.path.insert(0, "./One/")
		astar = imp.load_compiled('astar1_module', "./One/astarnavigator.pyc")
	return astar

def importAStar2(classFile):
	if os.path.exists(classFile + "/astarnavigator.pyc"):
		print "Custom AStarNavigator2"
		sys.path.insert(0, classFile)
		compileall.compile_dir(classFile)
		astar = imp.load_compiled('astar2_module', classFile + "/astarnavigator.pyc")
	else:
		print "Default AStarNavigator2"
		compileall.compile_dir("./One/")
		sys.path.insert(0, "./One/")
		astar = imp.load_compiled('astar2_module', "./One/astarnavigator.pyc")
	return astar

def getNav1(astar_module):
	#print "ClassFile: " + str(classFile)
	nav = astar_module.AStarNavigator()
	return nav

def getNav2(astar_module):
	#print "ClassFile: " + str(classFile)
	nav = astar_module.AStarNavigator()
	return nav

def cloneDynamicAStarNavigator(astar_module, nav):
	newnav = astar_module.AStarNavigator()
	newnav.world = nav.world
	newnav.pathnodes = nav.pathnodes
	newnav.pathnetwork = nav.pathnetwork
	return newnav

def importHero1(classFile):
	if os.path.exists(classFile + "/MyHero.py"):
		sys.path.insert(0, classFile)
		compileall.compile_dir(classFile)
		
	if os.path.exists(classFile + "/MyHero.pyc"):
		hero = imp.load_compiled('hero1_module', classFile + "/MyHero.pyc")
		return hero
	else:
		sys.exit("ERROR: Either no MyHero.py file found at " + classFile + " or MyHero.py compilation failed.")

def importMinion1(classFile):
	if os.path.exists(classFile + "/MyMinion.py"):
		sys.path.insert(0, classFile)
		compileall.compile_dir(classFile)
		
	if os.path.exists(classFile + "/MyMinion.pyc"):
		minion = imp.load_compiled('minion1_module', classFile + "/MyMinion.pyc")
		return minion
	else:
		sys.exit("ERROR: Either no MyMinion.py file found at " + classFile + " or MyMinion.py compilation failed.")

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

# import custom astar modules (if necessary) and create navigators for each student
astar1 = importAStar1(classFile1)
astar2 = importAStar2(classFile2)

nav1 = getNav1(astar1)
nav2 = getNav2(astar2)

from moba import *

# import hero modules
hero1 = importHero1(classFile1)
hero2 = importHero2(classFile2)

# import minion modules
minion1 = importMinion1(classFile1)
minion2 = importMinion2(classFile2)

# get hero classes from hero modules
heroclass1 = getattr(hero1, "MyHero")
heroclass2 = getattr(hero2, "MyHero")
# get minion classes from minion modules
minionclass1 = getattr(minion1, "MyMinion")
minionclass2 = getattr(minion2, "MyMinion")


########################
### Minion Subclasses

class MyHumanMinion(minionclass1):
	
	def __init__(self, position, orientation, world, image = NPC, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = SmallBullet):
		minionclass1.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)

class MyAlienMinion(minionclass2):
	
	def __init__(self, position, orientation, world, image = JACKAL, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = SmallBullet):
		minionclass2.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)


########################
### Hero Subclasses

class MyHumanHero(heroclass1):
	
	def __init__(self, position, orientation, world, image = AGENT, speed = SPEED, viewangle = 360, hitpoints = HEROHITPOINTS, firerate = FIRERATE, bulletclass = BigBullet, dodgerate = DODGERATE, areaeffectrate = AREAEFFECTRATE, areaeffectdamage = AREAEFFECTDAMAGE):
		heroclass1.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass, dodgerate, areaeffectrate, areaeffectdamage)

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
agent = Hero((600, 500), 0, world, AGENT)
world.setPlayerAgent(agent)
world.initializeTerrain(obstacles, (0, 0, 0), 4)
agent.setNavigator(Navigator())
agent.team = 1
world.debugging = True

# create AStarNavigator using student's astar module
nav1.setWorld(world)

b1 = Base(BASE, (25, 25), world, 1, MyHumanMinion, MyHumanHero, BUILDRATE)
b1.setNavigator(nav1)
world.addBase(b1)

t11 = Tower(TOWER, (200, 50), world, 1)
world.addTower(t11)
t12 = Tower(TOWER, (50, 200), world, 1)
world.addTower(t12)


# create AStarNavigator using student's astar module
nav2.setWorld(world)

b2 = Base(BASE, (1075, 1075), world, 2, MyAlienMinion, MyAlienHero, BUILDRATE)
b2.setNavigator(nav2)
world.addBase(b2)

t21 = Tower(TOWER, (1100, 950), world, 2)
world.addTower(t21)
t22 = Tower(TOWER, (950, 1100), world, 2)
world.addTower(t22)


#hero1 = MyHumanHero((125, 125), 0, world)
#hero1.setNavigator(cloneDynamicAStarNavigator(astar1, nav1))
#hero1.team = 1
#world.addNPC(hero1)
hero2 = MyAlienHero((1025, 1025), 0, world)
hero2.setNavigator(cloneDynamicAStarNavigator(astar2, nav2))
hero2.team = 2
world.addNPC(hero2)

world.makePotentialGates()

#hero1.start()
hero2.start()

world.run()
