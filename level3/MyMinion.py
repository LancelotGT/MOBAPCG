import sys, pygame, math, numpy, random, time, copy
from pygame.locals import *
from mobaLevel3 import *

class MyMinion(Minion):
	
	def __init__(self, position, orientation, world, image = NPC, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = SmallBullet):
		Minion.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)
		self.states = [Idle]
		### Add your states to self.states (but don't remove Idle)
		### YOUR CODE GOES BELOW HERE ###
		self.states += [Move, AttackNPC, AttackBase, AttackTower]
		### YOUR CODE GOES ABOVE HERE ###

	def start(self):
		Minion.start(self)
		self.changeState(Idle)





############################
### Idle
###
### This is the default state of MyMinion. The main purpose of the Idle state is to figure out what state to change to and do that immediately.

class Idle(State):
	
	def enter(self, oldstate):
		State.enter(self, oldstate)
		# stop moving
		self.agent.stopMoving()
	
	def execute(self, delta = 0):
		State.execute(self, delta)
		### YOUR CODE GOES BELOW HERE ###
		myTeam = self.agent.getTeam()
		enemyTowers = self.agent.world.getEnemyTowers(myTeam)
		enemyBase = self.agent.world.getEnemyBases(myTeam)
		self.agent.changeState(Move)
		### YOUR CODE GOES ABOVE HERE ###
		return None

##############################
### Taunt
###
### This is a state given as an example of how to pass arbitrary parameters into a State.
### To taunt someome, Agent.changeState(Taunt, enemyagent)

class Taunt(State):

	def parseArgs(self, args):
		self.victim = args[0]

	def execute(self, delta = 0):
		if self.victim is not None:
			print "Hey " + str(self.victim) + ", I don't like you!"
		self.agent.changeState(Idle)

##############################
### YOUR STATES GO HERE:



##############################
### Move
###
### This is a state to make an agent move. The agent should move to the nearest tower.
### To move someome, Agent.changeState(move)

class Move(State):

	def enter(self, delta = 0):
		myTeam = self.agent.getTeam()
		enemyTowers = self.agent.world.getEnemyTowers(myTeam)
		enemyBase = self.agent.world.getEnemyBases(myTeam)
		if len(enemyTowers) > 0:
			self.agent.navigateTo(nearestDest(self.agent, enemyTowers)[0].getLocation())
		elif len(enemyBase) > 0:
			self.agent.navigateTo(nearestDest(self.agent, enemyBase)[0].getLocation())

	def execute(self, delta):
		myTeam = self.agent.getTeam()
		myPos = self.agent.getLocation()
		enemyTowers = self.agent.world.getEnemyTowers(myTeam)
		enemyBase = self.agent.world.getEnemyBases(myTeam)
		visibleEnemyNPCs = filter(lambda x: x.getTeam() != myTeam, self.agent.getVisibleType(MOBAAgent))

		# make the agent move again if it returns from other state
		if (not self.agent.isMoving()):
			if len(enemyTowers) > 0:
				self.agent.navigateTo(nearestDest(self.agent, enemyTowers)[0].getLocation())
			elif len(enemyBase) > 0:
				self.agent.navigateTo(nearestDest(self.agent, enemyBase)[0].getLocation())

		# if nearby a base, change state to AttackBase
		if len(enemyBase) > 0 and len(enemyTowers) == 0 and distance(self.agent.getLocation(), enemyBase[0].getLocation()) < 150:
			self.agent.changeState(AttackBase)

		# most of time agent should go to tower
		if len(enemyTowers) > 0:
			if nearestDest(self.agent, enemyTowers)[1] < 150:
					self.agent.changeState(AttackTower)

		# if an enemy minion nearby, attack it by the way.
		if len(visibleEnemyNPCs) > 0:
			target, dist = nearestDest(self.agent, visibleEnemyNPCs)
			# targetDistToEnemyBase = 10000
			# if len(self.agent.world.getEnemyBases(myTeam)) > 0:
				# targetDistToEnemyBase = distance(target.getLocation(), self.agent.world.getEnemyBases(myTeam)[0].getLocation())
			if target.isAlive() and dist < 150:
				self.agent.changeState(AttackNPC, target)

##############################
### AttackBase
###
### This is a state where the agent attack the base until it is destroyed. The agent will navigate to base if it is not nearby.
### Agent.changeState(AttackBase)
class AttackBase(State):

	def enter(self, oldstate):
		self.agent.stop()

	def execute(self, delta = 0):
		myTeam = myTeam = self.agent.getTeam()
		enemyBase = self.agent.world.getEnemyBases(myTeam)
		if len(enemyBase) > 0:
			shootTarget(self.agent, enemyBase[0])
		else:
			self.agent.changeState(Move)

##############################
### AttackTower
###
### This is a state where the agent attack the tower until it is destroyed
### Agent.changeState(AttackTower)
class AttackTower(State):

	def enter(self, oldstate):
		self.agent.stopMoving()
		myTeam = myTeam = self.agent.getTeam()
		enemyTowers = self.agent.world.getEnemyTowers(myTeam)
		self.target = nearestDest(self.agent, enemyTowers)[0]

	def execute(self, delta = 0):
		myTeam = myTeam = self.agent.getTeam()
		enemyTowers = self.agent.world.getEnemyTowers(myTeam)
		if (len(enemyTowers) > 0):
			shootTarget(self.agent, self.target)
			if (not self.target.isAlive()):
				self.agent.changeState(Move)
		else:
			self.agent.changeState(Move)

##############################
### AttackNPC
###
### This is a state where the agent attack one opponent minion
### Agent.changeState(AttackNPC)
class AttackNPC(State):

	def enter(self, oldstate):
		self.agent.stop()

	def execute(self, delta = 0):
		if self.target != None:
			distToTarget = distance(self.target.getLocation(), self.agent.getLocation())
			if not self.target.isAlive() or distToTarget > 150:
				self.agent.changeState(Move)
			else:
				shootTarget(self.agent, self.target)
		else:
			self.agent.changeState(Move)

	def parseArgs(self, args):
		self.target = args[0]





### some helper functions
# return the nearest point to agent in dests and the distance to that point in a tuple
# return (dest, distToDest)
def nearestDest(agent, dests):
	myPos = agent.getLocation()
	destLocations = [e.getLocation() for e in dests]
	distToDests = map(distance, [myPos for i in range(len(destLocations))], destLocations)
	target = dests[distToDests.index(min(distToDests))]
	targetDist = distToDests[distToDests.index(min(distToDests))]
	return target, targetDist

# shoot a target
def shootTarget(agent, target):
	targetPos = target.getLocation()
	agent.turnToFace(targetPos)
	agent.shoot()
