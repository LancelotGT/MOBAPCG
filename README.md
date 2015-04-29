CS 7632 Game AI final project
==========
Author:

Ning Wang
Guillaume Orvain

Procedural Content Generation for MOBA Game
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
% There are several modes in the game.
% To get a whole customized game. Run bash restart.sh first to clear the data. Then use python play.py
% It will run the 6 predefined levels and then customize the level for you.
% To run the customized game directly swith the pre-generated data, use python customLevel/runCustom.py. 
% Make sure to run the game in MOBAPCG/ directory so that all the packages required can be found.
```

### How to change target score of PCG
```
% To change the target score of PCG, currently the only way is to manually modify the input for PCG 
% function in customLevel/runCustom.py file line 167.
```

### Explanation
This repository is for Game AI final project. The goal of this project is to implement procedural content generation with a MOBA game. The project intends to design a system that uses AI optimization to design maps for different players. The map that is generated is customized to an individual's skill level. That is, players who are more skilled at the game should receive a map that is more challenging, and players that are less skilled should receive a map that is less challenging.