import sys, pygame, math, numpy, random, time, copy
from pygame.locals import *

from astarnavigator import *

############################
### HELPERS

'''
def cloneAPSPNavigator(nav):
	newnav = APSPNavigator()
	newnav.world = nav.world
	newnav.pathnodes = nav.pathnodes
	newnav.pathnetwork = nav.pathnetwork
	newnav.next = nav.next
	newnav.dist = nav.dist
	return newnav
'''

def cloneAStarNavigator(nav):
	newnav = AStarNavigator()
	newnav.world = nav.world
	newnav.pathnodes = nav.pathnodes
	newnav.pathnetwork = nav.pathnetwork
	return newnav
