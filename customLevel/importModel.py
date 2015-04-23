import os, sys
cwd = os.getcwd()
# print cwd
sys.path.append(os.path.relpath('../', cwd))
from model.PlayerModel import LR
from model.PlayerModel import SVR
# model = LR()
# print model