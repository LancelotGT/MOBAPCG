CS 7632 Game AI final project
==========

Procedural Content Generation for MOBA (DOTA-like) Game
-----------------------------------------------------------

### Install package dependencies and configuration files (MacOS)
```
% To run the game, manually install OSX pygame distribution
% sudo pip install -U numpy scipy scikit-learn
% sudo apt-get install git
% git clone https://github.com/LancelotGT/MOBAPCG.git
```

### Install package dependencies and configuration files (Linux)
```
% To run the game, manually install Linux pygame distribution
% sudo apt-get update
% sudo apt-get install build-essential python-dev python-setuptools \
                      python-numpy python-scipy \
                      libatlas-dev libatlas3gf-base
% sudo apt-get install git
% git clone https://github.com/LancelotGT/MOBAPCG.git
```

### How to run
```
% To run game with PCG, use python play.py
% To run game without PCG, use python runversus.py
```

### Explanation
This repo is for Game AI final project. The goal of this project is to implement procedural content generation with a MOBA game. The project intends to design a system that uses AI optimization to design maps for different players. The map that is generated is customized to an individual's skill level. That is, players who are more skilled at the game should receive a map that is more challenging, and players that are less skilled should receive a map that is less challenging.

### Development Logs
04/12 Created three training levels. The entrance of the game is play.py. It will call certain training level according to the current number of finished games. For example, the entrance for level1 is runLevel1.py, and the moba configuration for level 1 is in mobaLevel1.py.

04/21 Write two python wrappers for linear regression and support vector regression, based on Scikit-Learn.

04/22 Implement Simulated Annealing from scratch to do optimization
