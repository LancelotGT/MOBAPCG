CS 7632 Game AI final project
==========

Procedural Content Generation for MOBA (DOTA-like) Game
-----------------------------------------------------------

### Install packages and configuration files

```
% To run the game, install pygame and numpy (http://pygame.org/download.shtml, http://www.scipy.org/scipylib/download.html)
% sudo apt-get update && sudo apt-get install git
% git clone https://github.com/LancelotGT/MOBAPCG.git
```

### How to run
```
% To run game with PCG, use python play.py
% To run game without PCG, use python runversus.py
```

### Explanation
```
This repo is for Game AI final project. The goal of this project is to implement procedural content generation with a MOBA game. The project intends to design a system that uses AI optimization to design maps for different players. The map that is generated is customized to an individual's skill level. That is, players who are more skilled at the game should receive a map that is more challenging, and players that are less skilled should receive a map that is less challenging.
```

### Development Logs
```
04/12 Created three training levels. The entrance of the game is play.py. It will call certain training level according to the current number of finished games. For example, the entrance for level1 is runLevel1.py, and the moba configuration for level 1 is in mobaLevel1.py.
```