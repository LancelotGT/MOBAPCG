import pygame, math, numpy, random, time, copy
from pygame.locals import * 
from modules import *

### Modifications:
### - Hero can dodge
### - MAXSPAWN = 3
### - Press 'j' to make agent dodge randomly
### - MOBABulletse tell MOBAAgents who did the damage
### - MOBAAgent.creditKill, Hero.creditKill

HITPOINTS = 25
BASEHITPOINTS = 75
TOWERHITPOINTS = 50
HEROHITPOINTS = 50
BUILDRATE = 180
TOWERFIRERATE = 15
BASEFIRERATE = 20
BULLETRANGE = 150
SMALLBULLETRANGE = 150
BIGBULLETRANGE = 250
TOWERBULLETRANGE = 250
TOWERBULLETSPEED = (20, 20)
BASEBULLETRANGE = 300
BASEBULLETSPEED = (20, 20)
SPAWNNUM = 5
MAXSPAWN = 10
AREAEFFECTDAMAGE = 25
AREAEFFECTRATE = 60
AREAEFFECTRANGE = 2
MAXLIVES = 3
SMALLBULLETSPEED = (20, 20)
BIGBULLETSPEED = (20, 20)
FIRERATE = 10
DODGERATE = 10
BASEBULLETDAMAGE = 10
SMALLBULLETDAMAGE = 1


TOWERBULLETDAMAGE = 15
BIGBULLETDAMAGE = 4

######################
### MOBABullet
###
### MOBABullets are like regular bullets, but expire after a certain distance is traversed.

class MOBABullet(Bullet):
	
	### range: how far the bullet will travel before expiring
	
	def __init__(self, position, orientation, world, image = SMALLBULLET, speed = SMALLBULLETSPEED, damage = SMALLBULLETDAMAGE, range = BULLETRANGE):
		Bullet.__init__(self, position, orientation, world, image, speed, damage)
		self.range = range
	
	def update(self, delta):
		Bullet.update(self, delta)
		if self.distanceTraveled > self.range:
			self.speed = (0, 0)
			self.world.deleteBullet(self)

	def collision(self, thing):
		Bullet.collision(self, thing)
		if isinstance(thing, Base) and (thing.getTeam() == None or thing.getTeam() != self.owner.getTeam()):
			self.hit(thing)
		elif isinstance(thing, Tower) and (thing.getTeam() == None or thing.getTeam() != self.owner.getTeam()):
			self.hit(thing)

	def hit(self, thing):
		ret = Bullet.hit(self, thing)
		if isinstance(thing, MOBAAgent) and (thing.getTeam() == None or thing.getTeam() != self.owner.getTeam()):
			#Already dished damage to another agent, so just keep track of who did the damage
			thing.lastDamagedBy = self.owner
			ret = True
			if isinstance(thing, Hero):
				self.world.damageTaken += self.damage
			# Should the agent get some score? Heros score by shooting Heros
			self.world.damageCaused(self.owner, thing, self.damage)
		elif isinstance(thing, Base) and (thing.getTeam() == None or thing.getTeam() != self.owner.getTeam()):
			thing.damage(self.damage)
			ret = True
			if isinstance(self.owner, Hero):
				self.world.damageToBase += self.damage
				self.world.damageDealt += self.damage
		elif isinstance(thing, Tower) and (thing.getTeam() == None or thing.getTeam() != self.owner.getTeam()):
			thing.damage(self.damage)
			ret = True
			if isinstance(self.owner, Hero):
				self.world.damageToTower += self.damage
				self.world.damageDealt += self.damage
		return ret

######################
### BigBullet

class BigBullet(MOBABullet):
	
	def __init__(self, position, orientation, world):
		MOBABullet.__init__(self, position, orientation, world, BIGBULLET, BIGBULLETSPEED, BIGBULLETDAMAGE, BIGBULLETRANGE)

###########################
### SmallBullet

class SmallBullet(MOBABullet):
	
	def __init__(self, position, orientation, world):
		MOBABullet.__init__(self, position, orientation, world, SMALLBULLET, SMALLBULLETSPEED, SMALLBULLETDAMAGE, BIGBULLETRANGE)


###########################
### TowerBullet

class TowerBullet(MOBABullet):
	
	def __init__(self, position, orientation, world):
		MOBABullet.__init__(self, position, orientation, world, TOWERBULLET, TOWERBULLETSPEED, TOWERBULLETDAMAGE, TOWERBULLETRANGE)

###########################
### BaseBullet

class BaseBullet(MOBABullet):
	
	def __init__(self, position, orientation, world):
		MOBABullet.__init__(self, position, orientation, world, BASEBULLET, BASEBULLETSPEED, BASEBULLETDAMAGE, BASEBULLETRANGE)




######################
### MOBAAgent
###
### Abstract base class for MOBA agents

class MOBAAgent(VisionAgent):

	### maxHitpoints: the maximum hitpoints the agent is allowed to have
	### lastDamagedBy: the agent that last did damage to me.
	### level: the level obtained by this agent. Level starts at 0.

	def __init__(self, position, orientation, world, image = NPC, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = MOBABullet):
		VisionAgent.__init__(self, image, position, orientation, speed, viewangle, world, hitpoints, firerate, bulletclass)
		self.maxHitpoints = hitpoints
		self.lastDamagedBy = None
		self.level = 0

	def start(self):
		StateAgent.start(self)
		self.world.computeFreeLocations(self)

	def collision(self, thing):
		StateAgent.collision(self, thing)
		# Agent dies if it hits an obstacle
		if isinstance(thing, Obstacle):
			self.world.deathsByCollision += 1
			self.die()

	def getMaxHitpoints(self):
		return self.maxHitpoints

	def getPossibleDestinations(self):
		return self.world.getFreeLocations(self)

	def die(self):
		VisionAgent.die(self)
		# Give a damage modifier
		if self.lastDamagedBy is not None and isinstance(self.lastDamagedBy, MOBAAgent):
			self.lastDamagedBy.creditKill(self)

	def creditKill(self, killed):
		return None
	
	def getLevel(self):
		return self.level
	
	def shoot(self):
		bullet = VisionAgent.shoot(self)
		# If a bullet is spawned, increase its damage by agent's level
		if bullet is not None:
			bullet.damage = bullet.damage + self.level
		return bullet

#######################
### Hero

class Hero(MOBAAgent):

	### dodgeRate: how often the agent can dodge
	### canDodge: the agent can dodge now
	### dodgeTimer: counting up until the agent can dodge again
	### areaEffectDamage: how much damage the area effect attack does
	### canAreaEffect: the agent can use area effect attack now
	### areaEffectRate: how often the agent can use area effect attack
	### areaEffectTimer: counting up until the agent can use area effect attack

	def __init__(self, position, orientation, world, image = AGENT, speed = SPEED, viewangle = 360, hitpoints = HEROHITPOINTS, firerate = FIRERATE, bulletclass = BigBullet, dodgerate = DODGERATE, areaeffectrate = AREAEFFECTRATE, areaeffectdamage = AREAEFFECTDAMAGE):
		MOBAAgent.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)
		self.dodgeRate = dodgerate
		self.dodgeTimer = 0
		self.canDodge = True
		self.canAreaEffect = True
		self.areaEffectRate = areaeffectrate
		self.areaEffectDamage = areaeffectdamage
		self.areaEffectTimer = 0

	def update(self, delta = 0):
		MOBAAgent.update(self, delta)
		if self.canDodge == False:
			self.dodgeTimer = self.dodgeTimer + 1
			if self.dodgeTimer >= self.dodgeRate:
				self.canDodge = True
				self.dodgeTimer = 0
		if self.canAreaEffect == False:
			self.areaEffectTimer = self.areaEffectTimer + 1
			if self.areaEffectTimer >= self.areaEffectRate:
				self.canAreaEffect = True
				self.areaEffectTimer = 0
		if (self.world.ticks % 20) == 0:
			print "Hitpoints: ", self.hitpoints

	def dodge(self, angle = None):
		if self.canDodge:
			self.world.numOfDodges += 1
			if angle == None:
				angle = corerandom.uniform(0, 360)
			vector = (math.cos(math.radians(angle)), -math.sin(math.radians(angle)))
			self.rect = self.rect.move(vector[0]*self.getRadius()*3, vector[1]*self.getRadius()*3)
			self.canDodge = False

	def areaEffect(self):
		if self.canAreaEffect:
			self.canAreaEffect = False
			pygame.draw.circle(self.world.background, (255, 0, 0), self.getLocation(), int(self.getRadius()*2), 1)
			for x in self.world.getEnemyNPCs(self.getTeam()) + self.world.getEnemyBases(self.getTeam()) + self.world.getEnemyTowers(self.getTeam()):
				if distance(self.getLocation(), x.getLocation()) < (self.getRadius()*AREAEFFECTRANGE)+(x.getRadius()):
					x.damage(self.areaEffectDamage + self.level)
					self.world.damageCaused(self, x, self.areaEffectDamage)
			return True
		return False

	def creditKill(self, killed):
		MOBAAgent.creditKill(self, killed)
		self.level = self.level + 1
		self.maxHitpoints = self.maxHitpoints + 1
		return None

	def reinit(self):
		self.level = 0
		self.maxHitpoints = HEROHITPOINTS

	# override
	def shoot(self):
		bullet = MOBAAgent.shoot(self)
		# If a bullet is spawned, increase its damage by agent's level
		if bullet is not None:
			bullet.damage = bullet.damage + self.level
		self.world.numOfBullets += 1
		return bullet


######################
### Minion
###
### Base class for Minions

class Minion(MOBAAgent):
	
	
	def __init__(self, position, orientation, world, image = NPC, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = MOBABullet):
		MOBAAgent.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)









############################
### Base
###
### Bases are invulnerable if they have any towers


class Base(Mover):
	
	### team: the name of the team owning the base
	### hitpoints: how much damage the base can withstand
	### nav: a Navigator that will be cloned and given to any NPCs spawned.
	### buildTimer: timer for how often a minion can be built
	### buildRate: how often a minion can be built
	### minionType: type of minion to build
	### heroType: type of hero to build
	### bulletclass: type of bullet used
	### firerate: how often the tower can fire
	### firetimer: time lapsed since last fire
	
	def __init__(self, image, position, world, team = None, minionType = Minion, heroType = Hero, buildrate = BUILDRATE, hitpoints = BASEHITPOINTS, firerate = BASEFIRERATE, bulletclass = BaseBullet):
		Mover.__init__(self, image, position, 0, 0, world)
		self.team = team
		self.hitpoints = hitpoints
		self.buildTimer = buildrate
		self.buildRate = buildrate
		self.nav = None
		self.minionType = minionType
		self.firerate = firerate
		self.firetimer = 0
		self.canfire = True
		self.bulletclass = bulletclass
		self.heroType = heroType
		self.maxHitPoints = hitpoints

	def setNavigator(self, nav):
		self.nav = nav

	def getTeam(self):
		return self.team
	
	def setTeam(self, team):
		self.team = team
	
	### Spawn an agent.
	### type: name of agent class. Must be RTSAgent or subclass thereof
	### angle: specifies where around the base the agent will be spawned
	def spawnNPC(self, type, angle = 0.0):
		agent = None
		n = len(self.world.getNPCsForTeam(self.getTeam()))
		if n < MAXSPAWN:
			vector = (math.cos(math.radians(angle)), -math.sin(math.radians(angle)))
			agent = type(self.getLocation(), 0, self.world)
			pos = (vector[0]*(self.getRadius()+agent.getRadius())/2.0,vector[1]*(self.getRadius()+agent.getRadius())/2.0)
			agent.rect = agent.rect.move(pos)
			if self.nav is not None:
				newnav = cloneAStarNavigator(self.nav)
				agent.setNavigator(newnav)
			agent.setTeam(self.team)
			agent.setOwner(self)
			self.world.addNPC(agent)
			agent.start()
		return agent
	
	def update(self, delta):
		Mover.update(self, delta)
		self.buildTimer = self.buildTimer + 1
		if self.buildTimer >= self.buildRate:
			for x in range(SPAWNNUM):
				angle = corerandom.randint(0, 360)
				self.spawnNPC(self.minionType, angle)
			self.buildTimer = 0
		if self.canfire == False:
			self.firetimer = self.firetimer + 1
			if self.firetimer >= self.firerate:
				self.canfire = True
				self.firetimer = 0
		if self.canfire and len(self.world.getTowersForTeam(self.getTeam())) == 0:
			targets = []
			minions = []
			heros = []
			for npc in self.world.npcs + [self.world.agent]:
				if npc.getTeam() == None or npc.getTeam() != self.getTeam() and distance(self.getLocation(), npc.getLocation()) < BASEBULLETRANGE:
					hit = rayTraceWorld(self.getLocation(), npc.getLocation(), self.world.getLines())
					if hit == None:
						if isinstance(npc, Minion):
							minions.append(npc)
						elif isinstance(npc, Hero):
							heros.append(npc)
			minions = sorted(minions, key=lambda x: distance(self.getLocation(), x.getLocation()))
			heros = sorted(heros, key=lambda x: distance(self.getLocation(), x.getLocation()))
			targets = minions + heros
			if len(targets) > 0:
				self.turnToFace(targets[0].getLocation())
				self.shoot()
		friends = self.world.getNPCsForTeam(self.getTeam())
		# Look for my hero
		hero = None
		for a in friends:
			if isinstance(a, Hero):
				hero = a
				break
		# if hero == None:
		# 	# spawn new hero
		# 	self.spawnNPC(self.heroType)

	def damage(self, amount):
		if len(self.world.getTowersForTeam(self.getTeam())) == 0:
			self.hitpoints = self.hitpoints - amount
			if self.hitpoints <= 0:
				self.die()


	def die(self):
		Mover.die(self)
		print "base dies", self
		self.world.deleteBase(self)

	def shoot(self):
		if self.canfire:
			bullet = self.bulletclass(self.rect.center, self.orientation, self.world)
			bullet.setOwner(self)
			self.world.addBullet(bullet)
			self.canfire = False
			return bullet
		else:
			return None

	def collision(self, thing):
		Mover.collision(self, thing)
		if isinstance(thing, Hero):
			agent = thing
			if agent.getTeam() == self.getTeam():
				# Heal
				agent.hitpoints = agent.maxHitpoints


	def getHitpoints(self):
		return self.hitpoints


############################
### TDBase
###
### A subclass of base which does not spawn any minion and hero
### modification : respawn 3 minions with really simple (stupid) AI every time they die


class TDBase(Base):

	def __init__(self, image, position, world, minionType1, minionType2, minionType3, team = None, hitpoints = BASEHITPOINTS, firerate = BASEFIRERATE, bulletclass = BaseBullet):
		Base.__init__(self, image, position, world, team = 0)
		self.team = team
		self.hitpoints = hitpoints
		self.nav = None
		self.firerate = firerate
		self.firetimer = 0
		self.canfire = True
		self.bulletclass = bulletclass

		self.minionType1 = minionType1
		self.minionType2 = minionType2
		self.minionType3 = minionType3


	# Override
	def update(self, delta):
		Mover.update(self, delta)

		if len(self.world.getNPCsForTeam(self.team)) == 0 :
			self.spawnNPC1()
			self.spawnNPC2()
			self.spawnNPC3()

		if self.canfire == False:
			self.firetimer = self.firetimer + 1
			if self.firetimer >= self.firerate:
				self.canfire = True
				self.firetimer = 0
		if self.canfire and len(self.world.getTowersForTeam(self.getTeam())) == 0:
			targets = []
			minions = []
			heros = []
			for npc in self.world.npcs + [self.world.agent]:
				if npc.getTeam() == None or npc.getTeam() != self.getTeam() and distance(self.getLocation(), npc.getLocation()) < BASEBULLETRANGE:
					hit = rayTraceWorld(self.getLocation(), npc.getLocation(), self.world.getLines())
					if hit == None:
						if isinstance(npc, Minion):
							minions.append(npc)
						elif isinstance(npc, Hero):
							heros.append(npc)
			minions = sorted(minions, key=lambda x: distance(self.getLocation(), x.getLocation()))
			heros = sorted(heros, key=lambda x: distance(self.getLocation(), x.getLocation()))
			targets = minions + heros
			if len(targets) > 0:
				self.turnToFace(targets[0].getLocation())
				self.shoot()
		# friends = self.world.getNPCsForTeam(self.getTeam())
		# # Look for my hero
		# hero = None
		# for a in friends:
		# 	if isinstance(a, Hero):
		# 		hero = a
		# 		break
		# if hero == None:
		# 	# spawn new hero
		# 	self.spawnNPC(self.heroType)

	# Override

	def spawnNPC1(self, angle = 0.0):
		agent = None

		vector = (math.cos(math.radians(angle)), -math.sin(math.radians(angle)))
		agent = self.minionType1(self.getLocation(), 0, self.world)
		pos = (vector[0]*(self.getRadius()+agent.getRadius())/2.0,vector[1]*(self.getRadius()+agent.getRadius())/2.0)
		agent.rect = agent.rect.move(pos)
		if self.nav is not None:
			newnav = cloneAStarNavigator(self.nav)
			agent.setNavigator(newnav)
		agent.setTeam(self.team)
		agent.setOwner(self)
		self.world.addNPC(agent)
		agent.start()
		return agent

	def spawnNPC2(self, angle = 0.0):
		agent = None

		vector = (math.cos(math.radians(angle)), -math.sin(math.radians(angle)))
		agent = self.minionType2(self.getLocation(), 0, self.world)
		pos = (vector[0]*(self.getRadius()+agent.getRadius())/2.0,vector[1]*(self.getRadius()+agent.getRadius())/2.0)
		agent.rect = agent.rect.move(pos)
		if self.nav is not None:
			newnav = cloneAStarNavigator(self.nav)
			agent.setNavigator(newnav)
		agent.setTeam(self.team)
		agent.setOwner(self)
		self.world.addNPC(agent)
		agent.start()
		return agent

	def spawnNPC3(self, angle = 0.0):
		agent = None

		vector = (math.cos(math.radians(angle)), -math.sin(math.radians(angle)))
		agent = self.minionType3(self.getLocation(), 0, self.world)
		pos = (vector[0]*(self.getRadius()+agent.getRadius())/2.0,vector[1]*(self.getRadius()+agent.getRadius())/2.0)
		agent.rect = agent.rect.move(pos)
		if self.nav is not None:
			newnav = cloneAStarNavigator(self.nav)
			agent.setNavigator(newnav)
		agent.setTeam(self.team)
		agent.setOwner(self)
		self.world.addNPC(agent)
		agent.start()
		return agent


	# Override
	def die(self):
		Mover.die(self)
		print "base dies", self
		self.world.deleteBase(self)
		print "Congratulations, you win!"
		writeGameStatistics(self.world)
		sys.exit(0)


#####################
### Tower



class Tower(Mover):
	
	### team: team that the tower is on
	### bulletclass: type of bullet used
	### firerate: how often the tower can fire
	### firetimer: time lapsed since last fire

	def __init__(self, image, position, world, team = None, hitpoints = TOWERHITPOINTS, firerate = TOWERFIRERATE, bulletclass = TowerBullet):
		Mover.__init__(self, image, position, 0, 0, world)
		self.team = team
		self.hitpoints = hitpoints
		self.firerate = firerate
		self.firetimer = 0
		self.canfire = True
		self.bulletclass = bulletclass
		self.maxHitPoints = hitpoints

	def getTeam(self):
		return self.team
	
	def setTeam(self, team):
		self.team = team


	def damage(self, amount):
		self.hitpoints = self.hitpoints - amount
		if self.hitpoints <= 0:
			self.die()

	def die(self):
		Mover.die(self)
		print "tower dies", self
		self.world.deleteTower(self)

	def update(self, delta):
		Mover.update(self, delta)
		if self.canfire == False:
			self.firetimer = self.firetimer + 1
			if self.firetimer >= self.firerate:
				self.canfire = True
				self.firetimer = 0
		if self.canfire:
			targets = []
			minions = []
			heros = []
			for npc in self.world.npcs + [self.world.agent]:
				if npc.getTeam() == None or npc.getTeam() != self.getTeam() and distance(self.getLocation(), npc.getLocation()) < TOWERBULLETRANGE:
					hit = rayTraceWorld(self.getLocation(), npc.getLocation(), self.world.getLines())
					if hit == None:
						if isinstance(npc, Minion):
							minions.append(npc)
						elif isinstance(npc, Hero):
							heros.append(npc)
			minions = sorted(minions, key=lambda x: distance(self.getLocation(), x.getLocation()))
			heros = sorted(heros, key=lambda x: distance(self.getLocation(), x.getLocation()))
			targets = minions + heros
			if len(targets) > 0:
				self.turnToFace(targets[0].getLocation())
				self.shoot()

	def shoot(self):
		if self.canfire:
			bullet = self.bulletclass(self.rect.center, self.orientation, self.world)
			bullet.setOwner(self)
			self.world.addBullet(bullet)
			self.canfire = False
			return bullet
		else:
			return None

	def getHitpoints(self):
		return self.hitpoints


##############################################
### MOBAWorld

class MOBAWorld(GatedWorld):
	
	### bases: the bases (one per team)
	### towers: the towers (many per team)
	### score: dictionary with team symbol as key and team score as value. Score is amount of damage done to the hero.
	
	def __init__(self, seed, worlddimensions, screendimensions, numgates, alarm):
		GatedWorld.__init__(self, seed, worlddimensions, screendimensions, numgates, alarm)
		self.bases = []
		self.towers = []
		self.score = {}
	
	def addBase(self, base):
		self.bases.append(base)
		if self.sprites is not None:
			self.sprites.add(base)
		self.movers.append(base)
	
	def deleteBase(self, base):
		if base in self.bases:
			self.bases.remove(base)
			if self.sprites is not None:
				self.sprites.remove(base)
			self.movers.remove(base)
	
	
	def addTower(self, tower):
		self.towers.append(tower)
		if self.sprites is not None:
			self.sprites.add(tower)
		self.movers.append(tower)
			
	def deleteTower(self, tower):
		if tower in self.towers:
			self.towers.remove(tower)
			if self.sprites is not None:
				self.sprites.remove(tower)
			self.movers.remove(tower)

	def getBases(self):
		return list(self.bases)
	
	def getBaseForTeam(self, team):
		for b in self.bases:
			if b.getTeam() == team:
				return b
		return None
	
	def getEnemyBases(self, myteam):
		bases = []
		for b in self.bases:
			if b.getTeam() != myteam:
				bases.append(b)
		return bases

	def getTowers(self):
		return list(self.towers)

	def getTowersForTeam(self, team):
		towers = []
		for t in self.towers:
			if t.getTeam() == team:
				towers.append(t)
		return towers

	def getEnemyTowers(self, myteam):
		towers = []
		for t in self.towers:
			if t.getTeam() != myteam:
				towers.append(t)
		return towers
	
	def getNPCsForTeam(self, team):
		npcs = []
		for x in self.getNPCs():
			if x.getTeam() == team:
				npcs.append(x)
		return npcs

	def getEnemyNPCs(self, myteam):
		npcs = []
		for x in self.getNPCs():
			if x.getTeam() != myteam:
				npcs.append(x)
		return npcs


	def doKeyDown(self, key):
		GatedWorld.doKeyDown(self, key)
		if key == 100: #'d'
			if isinstance(self.agent, Hero):
				self.agent.dodge()
		elif key == 97: #'a'
			if isinstance(self.agent, Hero):
				self.agent.areaEffect()

	def damageCaused(self, damager, damagee, amount):
		if isinstance(damager, Hero) and isinstance(damagee, Hero):
			self.addToScore(damager.getTeam(), amount)


	def addToScore(self, team, amount):
		if team is not None:
			if team not in self.score.keys():
				self.score[team] = 0
			self.score[team] = self.score[team] + amount
			print "Score", self.score

	def getScore(self, team):
		if team is not None:
			if team not in self.score.keys():
				self.score[team] = 0
			return self.score[team]
		return 0

	def deleteNPC(self, npc):
		if npc in self.npcs:
			self.npcs.remove(npc)
			if self.sprites is not None:
				self.sprites.remove(npc)
			self.movers.remove(npc)
		elif npc == self.agent:
			print "Player respawned."

			position = self.agent.getLocation()
			displacement = (1055 - position[0] , 1055 - position[1])
			self.agent.rect = self.agent.rect.move(displacement)

			self.agent.reinit
			self.playerDeaths += 1
			if self.playerDeaths == MAXLIVES:
				print "Sorry, you lose!"
				writeGameStatistics(self)
				sys.exit(0)
			else:
				print "Number of lives left: ", MAXLIVES - self.playerDeaths
				position = self.agent.getLocation()
				displacement = (1075 - position[0] , 1075 - position[1])
				self.agent.rect = self.agent.rect.move(displacement)
				self.agent.reinit
			#self.sprites.remove(npc)
			#self.movers.remove(npc)
			#self.agent = None
			#newAgent = Hero((1600, 1500), 0, self, ELITE)
			#newAgent.setNavigator(Navigator())
			#newAgent.team = 2
			#self.sprites.add(newAgent)
			#self.setPlayerAgent(newAgent)



