import os, sys, pygame, math, numpy, random, time, copy, compileall
from pygame.locals import *
from mobaCustom import *
from pcg import *
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

def importEnemy1(thisClassFile):
    if os.path.exists(thisClassFile + "enemyAgents.py"):
        sys.path.insert(0, thisClassFile)
        compileall.compile_dir(thisClassFile)
        
    if os.path.exists(thisClassFile + "enemyAgents.pyc"):
        minion = imp.load_compiled('enemyMinion1_module', thisClassFile + "enemyAgents.pyc")
        return minion
    else:
        sys.exit("ERROR: Either no enemyAgents.py file found at " + thisClassFile + " or enemyAgents.py compilation failed.")


def importEnemy2(thisClassFile):
    if os.path.exists(thisClassFile + "enemyAgents2.py"):
        sys.path.insert(0, thisClassFile)
        compileall.compile_dir(thisClassFile)
        
    if os.path.exists(thisClassFile + "enemyAgents2.pyc"):
        minion = imp.load_compiled('enemyMinion2_module', thisClassFile + "enemyAgents2.pyc")
        return minion
    else:
        sys.exit("ERROR: Either no enemyAgents2.py file found at " + thisClassFile + " or enemyAgents2.py compilation failed.")


def importEnemy3(thisClassFile):
    if os.path.exists(thisClassFile + "enemyAgents3.py"):
        sys.path.insert(0, thisClassFile)
        compileall.compile_dir(thisClassFile)
        
    if os.path.exists(thisClassFile + "enemyAgents3.pyc"):
        minion = imp.load_compiled('enemyMinion3_module', thisClassFile + "enemyAgents3.pyc")
        return minion
    else:
        sys.exit("ERROR: Either no enemyAgents3.py file found at " + thisClassFile + " or enemyAgents3.py compilation failed.")

thisClassFile = "./customLevel/"

nav1 = AStarNavigator()
nav2 = AStarNavigator()

# imp.reload(moba)
# mod = reload(sys.modules['moba']) #use imp.reload for Python 3  
# vars().update(mod.__dict__)



# import hero modules
hero2 = importHero2(thisClassFile)

# import minion modules
minion2 = importMinion2(thisClassFile)
enemyMinion1 = importEnemy1(thisClassFile)
enemyMinion2 = importEnemy2(thisClassFile)
enemyMinion3 = importEnemy3(thisClassFile)



# get hero classes from hero modules
heroclass2 = getattr(hero2, "MyHero")

# get minion classes from minion modules
minionclass2 = getattr(minion2, "MyMinion")
enemyMinionClass1 = getattr(enemyMinion1, "enemyMinion")
enemyMinionClass2 = getattr(enemyMinion2, "enemyMinion2")
enemyMinionClass3 = getattr(enemyMinion3, "enemyMinion3")


########################
### Minion Subclasses

class MyAlienMinion(minionclass2):
    
    def __init__(self, position, orientation, world, image = JACKAL, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = SmallBullet):
        minionclass2.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)

class enemyMinion1(enemyMinionClass1):
    
    def __init__(self, position, orientation, world, image = JACKAL, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = SmallBullet):
        enemyMinionClass1.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)

class enemyMinion2(enemyMinionClass2):
    
    def __init__(self, position, orientation, world, image = JACKAL, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = SmallBullet):
        enemyMinionClass2.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)

class enemyMinion3(enemyMinionClass3):
    
    def __init__(self, position, orientation, world, image = JACKAL, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = SmallBullet):
        enemyMinionClass3.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)


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
#            [(800, 170), (1040, 140), (1050, 160), (1040, 500), (810, 310)]]
obstacles = [[(400, 150), (850, 150), (900, 300), (1050, 350), (1050, 800), (1010, 900), (990, 900), (900, 750), (900, 500), (700, 300), (450, 300), (350, 210), (350, 190)]
             ]


mirror = map(lambda poly: map(lambda point: (dims[0]-point[0], dims[1]-point[1]), poly), obstacles)

obstacles = obstacles + mirror



world = MOBAWorld(SEED, dims, dims, 1, 60)
agent = Hero((1055, 1055), 0, world, ELITE)
world.setPlayerAgent(agent)
world.initializeTerrain(obstacles, (0, 0, 0), 4)
agent.setNavigator(nav1)
agent.setTeam(2)
world.debugging = True

# create AStarNavigator using student's astar module
nav1.setWorld(world)

b1 = TDBase(BASE, (25, 25), world, enemyMinion1, enemyMinion2, enemyMinion3, 1)
b1.setNavigator(nav1)
world.addBase(b1)

### use one of the two models
thePlayer = LR()
# thePlayer = SVR()

PCG(world, 0.2, thePlayer)

world.setAreaFeature()


# create AStarNavigator using student's astar module
nav2.setWorld(world)

b2 = Base(BASE, (1075, 1075), world, 2, MyAlienMinion, MyAlienHero, BUILDRATE)
b2.setNavigator(nav2)
world.addBase(b2)

world.run()
