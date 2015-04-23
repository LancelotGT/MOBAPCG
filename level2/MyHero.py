import sys, pygame, math, numpy, random, time, copy
from pygame.locals import *
from mobaLevel2 import *


#############################
# some constants
RATEOFHEALTHFORHEALING = 3
LEADINGFORMOVINGTARGET = 25


#############################
### MyHero

class MyHero(Hero):

	def __init__(self, position, orientation, world, image = AGENT, speed = SPEED, viewangle = 360, hitpoints = HEROHITPOINTS, firerate = FIRERATE, bulletclass = BigBullet, dodgerate = DODGERATE, areaeffectrate = AREAEFFECTRATE, areaeffectdamage = AREAEFFECTDAMAGE):
		Hero.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass, dodgerate, areaeffectrate, areaeffectdamage)
		self.states = [Idle]
		### Add your states to self.states (but don't reHunt Idle)
		### YOUR CODE GOES BELOW HERE ###
		self.states += [Hunt, KillHero, Healing, AttackTower, AttackBase]
		### YOUR CODE GOES ABOVE HERE ###

	def start(self):
		Hero.start(self)
		self.changeState(Idle)

############################
### Idle
###
### This is the default state of MyHero. The main purpose of the Idle state is to figure out what state to change to and do that immediately.

class Idle(State):
	
	def enter(self, oldstate):
		State.enter(self, oldstate)
		# stop moving
		self.agent.stopMoving()
	
	def execute(self, delta = 0):
		State.execute(self, delta)
		### YOUR CODE GOES BELOW HERE ###
		self.agent.changeState(Hunt)
		### YOUR CODE GOES ABOVE HERE ###
		return None

###############################
### YOUR STATE CLASSES GO HERE:

##############################
### Hunt
###
### This is a state to make an agent Hunt. The agent should Hunt to the nearest tower.
### To Hunt someome, Agent.changeState(Hunt)

class Hunt(State):

	def enter(self, delta = 0):
		myTeam = self.agent.getTeam()
		self.enemyHero = None
		for NPC in self.agent.world.getEnemyNPCs(self.agent.getTeam()):
			if isinstance(NPC, Hero):
				self.enemyHero = NPC
				break
		# get the hero moving when enter this state
		if self.enemyHero != None:
			self.agent.navigateTo(predictPosition(self.enemyHero, LEADINGFORMOVINGTARGET))

	def execute(self, delta = 0):
		myTeam = self.agent.getTeam()
		myPos = self.agent.getLocation()
		enemyTowers = self.agent.world.getEnemyTowers(myTeam)
		enemyBase = self.agent.world.getEnemyBases(myTeam)
		visibleEnemyMinions = filter(lambda x: x.getTeam() != myTeam, self.agent.getVisibleType(Minion))
		enemyNPCs = self.agent.world.getEnemyNPCs(self.agent.getTeam())

		# locate the enemy hero in real-time
		for NPC in enemyNPCs:
			if isinstance(NPC, Hero):
				self.enemyHero = NPC
				break

		# if enemy minion or hero in area effect range
		if self.agent.canAreaEffect:
			for npc in enemyNPCs:
				if distance(npc.getLocation(), myPos) <= 50:
					self.agent.areaEffect()
					break

		if self.agent.getHitpoints() <= self.agent.getMaxHitpoints() / RATEOFHEALTHFORHEALING:
			self.agent.changeState(Healing)

		# dodge bullet from enemy minion
		prepareForDodgeBullet(self.agent)

		# periodically check the position of enemy hero and update my navigation route
		if (self.agent.world.ticks % 50) == 0 and self.enemyHero != None:
			if len(enemyBase) > 0:
				enemyHeroDistToBase = distance(enemyBase[0].getLocation(), self.enemyHero.getLocation())
				myHeroDistToEnemyBase = distance(enemyBase[0].getLocation(), self.agent.getLocation())
				# print enemyHeroDistToBase
				if enemyHeroDistToBase < 180 and myHeroDistToEnemyBase > BIGBULLETRANGE and len(enemyTowers) > 0:
					self.agent.changeState(Healing)
				else:
					if self.agent.getLevel() - self.enemyHero.getLevel() >= 5:
						if len(enemyTowers) > 0:
							self.agent.navigateTo(nearestDest(self.agent, enemyTowers)[0].getLocation())					
						else:
							self.agent.navigateTo(enemyBase[0].getLocation())
					elif self.agent.getLevel() <= self.enemyHero.getLevel() and len(visibleEnemyMinions) > 0:
						if len(nearestDest(self.agent, visibleEnemyMinions)) == 2:
							self.agent.navigateTo(predictPosition(nearestDest(self.agent, visibleEnemyMinions)[0], LEADINGFORMOVINGTARGET))
					else:
						if len(enemyTowers) > 0:
							self.agent.navigateTo(nearestDest(self.agent, enemyTowers)[0].getLocation())					
						else:
							self.agent.navigateTo(enemyBase[0].getLocation())

		# if an enemy minion nearby, attack it by the way.
		if len(visibleEnemyMinions) > 0:
			target, dist = nearestDest(self.agent, visibleEnemyMinions)
			if target.isAlive() and dist < 250:
				shootTarget(self.agent, target)

		# if nearby a base, change state to AttackBase
		if len(enemyBase) > 0 and len(enemyTowers) == 0 and distance(self.agent.getLocation(), enemyBase[0].getLocation()) < 150:
			self.agent.changeState(AttackBase)

		# if near a tower, change state to AttackTower
		if len(enemyTowers) > 0:
			if nearestDest(self.agent, enemyTowers)[1] < 150:
					self.agent.changeState(AttackTower)

		# if hero nearby, then kill the hero
		if self.enemyHero != None:
			if distance(self.enemyHero.getLocation(), self.agent.getLocation()) < BIGBULLETRANGE:
				self.agent.changeState(KillHero)

##############################
### AttackHero
###
### This is a state where the hero will attack the opponent hero
### Agent.changeState(AttackHero)
class KillHero(State):

	def enter(self, oldstate):
		self.enemyHero = None
		for agent in self.agent.world.getEnemyNPCs(self.agent.getTeam()):
			if isinstance(agent, Hero):
				self.enemyHero = agent

	def execute(self, delta = 0):

		myTeam = self.agent.getTeam()
		enemyTowers = self.agent.world.getEnemyTowers(myTeam)
		enemyNPCs = self.agent.world.getEnemyNPCs(self.agent.getTeam())
		enemyBase = self.agent.world.getEnemyBases(myTeam)

		# dodge bullet
		prepareForDodgeBullet(self.agent)

		# relocating the enemy hero
		for agent in self.agent.world.getEnemyNPCs(self.agent.getTeam()):
			if isinstance(agent, Hero):
				self.enemyHero = agent

		if self.agent.getHitpoints() <= self.agent.getMaxHitpoints() / RATEOFHEALTHFORHEALING:
			self.agent.changeState(Healing)

		# if nearby a base, change state to AttackBase
		if len(enemyBase) > 0 and len(enemyTowers) == 0:
			myHeroDistToEnemyBase = distance(self.agent.getLocation(), enemyBase[0].getLocation())
		 	if (myHeroDistToEnemyBase < BIGBULLETRANGE):
				self.agent.changeState(AttackBase)
			else:
				self.agent.navigateTo(enemyBase[0].getLocation())

		# if near a tower, change state to AttackTower
		if len(enemyTowers) > 0:
			if nearestDest(self.agent, enemyTowers)[1] < 150:
					self.agent.changeState(AttackTower)

		# if enemy minion or hero in area effect range
		if self.agent.canAreaEffect:
			for npc in enemyNPCs:
				if distance(npc.getLocation(), self.agent.getLocation()) <= 50:
					self.agent.areaEffect()
					break

		if self.enemyHero != None:
			distToTarget = distance(self.enemyHero.getLocation(), self.agent.getLocation())
			if distToTarget > 250:
				self.agent.changeState(Hunt)
			else:
				self.agent.stopMoving()
				shootTarget(self.agent, self.enemyHero)
		else:
			self.agent.changeState(Hunt)


#############################
### Healing
###
### This is a state where the hero will go back the base and heal itself
### Agent.changeState(Healing)
class Healing(State):

	def enter(self, oldstate):
		self.myBase = self.agent.world.getBaseForTeam(self.agent.getTeam())
		self.agent.navigateTo(self.myBase.getLocation())

	def execute(self, delta = 0):
		enemyNPCs = self.agent.world.getEnemyNPCs(self.agent.getTeam())
		# dodge bullet
		prepareForDodgeBullet(self.agent)

		# make the agent Hunt again if it returns from other state
		if not self.agent.isMoving():
			self.agent.navigateTo(self.myBase.getLocation())

		myTeam = self.agent.getTeam()
		# locate enemy minions
		visibleEnemyMinions = filter(lambda x: x.getTeam() != myTeam, self.agent.getVisibleType(Minion))

		# locate the enemy hero when retreating
		self.enemyHero = None
		for npc in self.agent.world.getEnemyNPCs(self.agent.getTeam()):
			if isinstance(npc, Hero):
				self.enemyHero = npc

		# if enemy minion or hero in area effect range
		if self.agent.canAreaEffect:
			for npc in enemyNPCs:
				if distance(npc.getLocation(), self.agent.getLocation()) <= 50:
					self.agent.areaEffect()
					break

		distToBase = distance(self.agent.getLocation(), self.myBase.getLocation())
		if distToBase < 2 * self.agent.getRadius():
			self.agent.changeState(Hunt)

		if self.agent.getHitpoints() >= self.agent.getMaxHitpoints() * 0.8:
			self.agent.changeState(Hunt)

		# if an hero nearby, shoot it. If no hero nearby, then shoot minions.
		if self.enemyHero != None and distance(self.enemyHero.getLocation(), self.agent.getLocation()) < BIGBULLETRANGE:
		    shootTarget(self.agent, self.enemyHero)

		if len(visibleEnemyMinions) > 0:
			target, dist = nearestDest(self.agent, visibleEnemyMinions)
			if target.isAlive() and dist < 250:
				shootTarget(self.agent, target)



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
		prepareForDodgeBullet(self.agent)

		if self.agent.getHitpoints() <= self.agent.getMaxHitpoints() / RATEOFHEALTHFORHEALING:
			self.agent.changeState(Healing)

		myTeam = myTeam = self.agent.getTeam()
		enemyTowers = self.agent.world.getEnemyTowers(myTeam)
		if (len(enemyTowers) > 0):
			shootTarget(self.agent, self.target)
			if (not self.target.isAlive()):
				self.agent.changeState(Hunt)
		else:
			self.agent.changeState(Hunt)



##############################
### AttackBase
###
### This is a state where the agent attack the base until it is destroyed. The agent will navigate to base if it is not nearby.
### Agent.changeState(AttackBase)
class AttackBase(State):

	def enter(self, oldstate):
		self.agent.stop()

	def execute(self, delta = 0):
		prepareForDodgeBullet(self.agent)

		if self.agent.getHitpoints() <= self.agent.getMaxHitpoints() / RATEOFHEALTHFORHEALING:
			self.agent.changeState(Healing)

		myTeam = myTeam = self.agent.getTeam()
		enemyBase = self.agent.world.getEnemyBases(myTeam)
		if len(enemyBase) > 0:
			shootTarget(self.agent, enemyBase[0])
		else:
			self.agent.changeState(Hunt)


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
	if isinstance(target, Hero) or isinstance(target, Minion):
		targetPos = predictPosition(target, LEADINGFORMOVINGTARGET)
	agent.turnToFace(targetPos)
	agent.shoot()

# the hero can dodge a bullet in the direction vertical to where the bullet is coming
def dodgeBullet(agent, bullet):
	world = agent.world
	bulletAngle = bullet.getOrientation()
	angleList = [(bulletAngle + 90) % 360, (bulletAngle - 90) % 360]
	for angle in angleList:
		dest = dodgeDest(agent, angle)
		dists = map(minimumDistance, world.getLines(), [dest for i in range(len(world.getLines()))])
		insideObstacle = False
		for obstacle in world.getObstacles():
			if pointInsidePolygonLines(dest, obstacle.getLines()):
				insideObstacle = True
		if min(dists) > 2 * agent.getRadius() and insideObstacle == False:
			agent.dodge(angle)
			break

# predict the position of the target
def predictPosition(agent, speed):
	pos = agent.getLocation()
	if not agent.isMoving():
		return pos
	else:
		angle = agent.getOrientation()
		vector = (math.cos(math.radians(angle)), -math.sin(math.radians(angle)))
		newPos = [0, 0]
		newPos[0] = pos[0] + vector[0] * speed
		newPos[1] = pos[1] + vector[1] * speed
		return tuple(newPos)

# predict the position of the target
def predictBulletPosition(agent, speed):
	pos = agent.getLocation()
	angle = agent.getOrientation()
	vector = (math.cos(math.radians(angle)), -math.sin(math.radians(angle)))
	newPos = [0, 0]
	newPos[0] = pos[0] + vector[0] * speed
	newPos[1] = pos[1] + vector[1] * speed
	return tuple(newPos)

def dodgeDest(agent, angle):
	pos = agent.getLocation()
	vector = (math.cos(math.radians(angle)), -math.sin(math.radians(angle)))
	newPos = [0, 0]
	newPos[0] = pos[0] + vector[0] * agent.getRadius()*1.5
	newPos[1] = pos[1] + vector[1] * agent.getRadius()*1.5
	return tuple(newPos)

def prepareForDodgeBullet(agent):
	if agent.canDodge:
		bullets = agent.getVisibleType(MOBABullet)
		for bullet in bullets:
			distToBullet = distance(bullet.getLocation(), agent.getLocation())
			if distToBullet < 50:
				if bullet.owner.getTeam() != agent.getTeam():
					theta = calculateAngle(bullet, agent.getLocation())
					theta %= 360
					#print "The value of theta: ", theta
					#print "The value of bullet orientation: ", bullet.getOrientation()
					angleDiff = abs(theta - bullet.getOrientation())
					if angleDiff > 180:
						angleDiff = 360 - angleDiff
					#print angleDist
					if angleDiff < 40:
						dodgeBullet(agent, bullet)
						break

def calculateAngle(agent, pos):
	# agent is the bullet, pos if the position of hero
	direction = (pos[0] - agent.getLocation()[0], pos[1] - agent.getLocation()[1])
	angle = math.degrees(numpy.arctan2(direction[0],direction[1]))-90
	return angle