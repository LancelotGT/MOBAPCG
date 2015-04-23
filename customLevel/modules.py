import os, sys
cwd = os.getcwd()
# print cwd
sys.path.append(os.path.relpath('../', cwd))
from model.PlayerModel import LR
from model.PlayerModel import SVR
# model = LR()
# print model
from sharedcontents.agents import *
from sharedcontents.clonenav import *
from sharedcontents.core import *
from sharedcontents.mynavigatorhelpers import *
from sharedcontents.statemachine import *
from sharedcontents.utils import *
from sharedcontents.astarnavigator import *