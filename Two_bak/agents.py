import sys, pygame, math, numpy, random, time, copy
from pygame.locals import * 

from constants import *
from utils import *
from core import *
from statemachine import *

############################
### STATEAGENT

class StateAgent(Agent, StateMachine):

	### states: a set of states (class names) that the agent can be in
	### state: the current state (State object). 
	
	### NOTE: use self.getStateType() to check what state the agent is in (you usually don't need an actual reference to the state object. self.getState() == Kill works for a conditional check.

	def __init__(self, image, position, orientation, speed, world, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = Bullet, states = []):
		Agent.__init__(self, image, position, orientation, speed, world, hitpoints, firerate, bulletclass)
		StateMachine.__init__(self, states)

		
	def update(self, delta):
		Agent.update(self, delta)
		StateMachine.update(self, delta)
	
	
	def getStateType(self):
		return type(self.state)
		
	def stop(self):
		Agent.stop(self)
		self.changeState(None)


#####################
### VisionAgent

class VisionAgent(StateAgent):

	### viewangle: the amount of angle, centered on the agent's orientation, that the agent can see out of
	### visible: things that are visible (movers)

	def __init__(self, image, position, orientation, speed, viewangle, world, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = Bullet, states = []):
		StateAgent.__init__(self, image, position, orientation, speed, world, hitpoints, firerate, bulletclass, states)
		self.viewangle = viewangle
		self.visible = []


	def update(self, delta):
		StateAgent.update(self, delta)
		# Ask the world for what is visible (Movers) within the cone of vision
		visible = self.world.getVisible(self.getLocation(), self.orientation, self.viewangle)
		self.visible = visible


	def getVisible(self):
		return self.visible

	def getVisibleType(self, type):
		v = []
		for x in self.visible:
			if isinstance(x, type):
				v.append(x)
		return v
		
			
			
