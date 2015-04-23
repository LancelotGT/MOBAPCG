import sys, pygame, math, numpy, random, time, copy
from pygame.locals import *
from mobaLevel3 import *


class enemyMinion(Minion):
	
	def __init__(self, position, orientation, world, image = NPC, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = SmallBullet):
		Minion.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)
		self.states = [Idle]
		### Add your states to self.states (but don't remove Idle)
		### YOUR CODE GOES BELOW HERE ###

		self.states.append(MoveToTarget)
		self.states.append(Attack)

		### YOUR CODE GOES ABOVE HERE ###

	def start(self):
		Minion.start(self)
		self.changeState(MoveToTarget)



class Idle(State):
	
	def enter(self, oldstate):
		#State.enter(self, oldstate)
		# stop moving
		self.agent.stopMoving()


	def execute(self, delta = 0):
		if distance(self.agent.world.agent.getLocation(), self.agent.getLocation()) < 2*BULLETRANGE :
			self.agent.changeState(Attack, self.agent.world.agent)

		return None


class Attack(State):

	def parseArgs(self, args):
		self.target = args[0]


	def execute(self, delta = 0):
		
		if self.target.getHitpoints() < 0 :
			self.agent.changeState(MoveToTarget)
			return None

		if distance(self.agent.getLocation(), self.target.getLocation()) > BULLETRANGE*3/4 :
			self.agent.navigateTo(self.target.getLocation())
		else :
			self.agent.stopMoving()

		if distance(self.agent.getLocation(), self.target.getLocation()) > BULLETRANGE :
			return None
		else :
			self.agent.turnToFace(self.target.getLocation())
			self.agent.shoot()


class MoveToTarget(State):

	def enter(self, oldstate):
		self.agent.navigateTo((self.agent.world.dimensions[0]*9/10, self.agent.world.dimensions[1]/10))


	def execute(self, delta = 0):

		target = (self.agent.world.dimensions[0]*9/10, self.agent.world.dimensions[1]/10)
		if distance(self.agent.getLocation(), target) < 10 :
			self.agent.changeState(Idle)
			return None

		if distance(self.agent.world.agent.getLocation(), self.agent.getLocation()) < 2*BULLETRANGE :
			self.agent.changeState(Attack, self.agent.world.agent)
		
		return None
