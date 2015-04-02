import sys, pygame, math, numpy, random, time, copy
from pygame.locals import * 

from constants import *
from utils import *
from core import *

############################
### STATE

class State(object):

	### agent: the agent this state machine is controlling

	### args is a list of arguments. The args must be parsed by the constructor
	def __init__(self, agent, args = []):
		self.agent = agent
		self.parseArgs(args)

	def execute(self, delta = 0):
		return None
		
	def enter(self, oldstate):
		return None
		
	def exit(self):
		return None
		
	def parseArgs(self, args):
		return None


############################
### STATEMACHINE

class StateMachine():

	### states: a set of states (class names) that the agent can be in
	### state: the current state (State object).
	
	def __init__(self, states):
		self.states = states
		self.state = None
		
	def update(self, delta):
		if self.state is not None:
			self.state.execute(delta)
		
	
	def changeState(self, newstateclass, *args):
		if self.states is not None and (newstateclass == None or newstateclass in self.states):
			old = self.state
			if old is not None:
				old.exit()
			if newstateclass is not None:
				new = newstateclass(self, args)
				if old is not None:
					new.enter(type(old))
				else:
					new.enter(None)
				self.state = new
			else:
				self.state = None

	def getState(self):
		if self.state == None:
			return None
		else:
			return type(self.state)
