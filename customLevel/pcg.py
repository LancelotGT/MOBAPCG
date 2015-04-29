import sys, pygame, math, numpy, random, time, copy

from pygame.locals import * 
from mobaCustom import *
import imp

from optimization import SimulatedAnnealing


def isFar(towers, towerLoc, coeff) :

  thebool = True
  for tower in towers :
    if (distance(tower, towerLoc) < 0.6*coeff*TOWERBULLETRANGE) :
      return False

  return thebool



def isFarBis(towers, towerLoc, minDist) :

  thebool = True
  for tower in towers :
    if (distance(tower, towerLoc) < minDist) :
      return False

  return thebool


def PCG(world, score, model):

  # features = [random.randint(4, 12), random.randint(2,5)]
  # coeff = random.uniform(0.6, 1)
  # features.append(features[0]*coeff)

  # coeffs = model.getParams()

  # while (model.testScore(features) > score) :
  #   features[0] -= 1
  #   features[2] -= coeff
  # while (model.testScore(features) < score) :
  #   features[0] += 1 
  #   features[2] += coeff
  
  # while (model.testScore(features) > score) and (coeff > 0.6) :
  #   coeff -= 0.05
  #   features[2] = features[0]*coeff

  # features[1] = (score - features[0]*coeffs[0] - features[2]*coeffs[2])/coeffs[1]
  # towerhitpoints = 50 + 25*(features[1]/3)
  # towerbulletdamage = ((features[1]%3)+2)*5

  ### optimzation part
  target = score
  SA = SimulatedAnnealing(model, target)
  features = SA.finalState()
  features = (int(round(features[0])), features[1], features[2]) # take three feature from level.txt
  # print "Optimized features: ", features
  # model.testScore(features)
  # towerhitpoints = 50 + 25*(features[1]/3)

  BIGBULLETDAMAGE = 5
  TOWEREBULLETDAMAGE = features[1] #int(round(BIGBULLETDAMAGE / features[1]))
  if TOWEREBULLETDAMAGE < 10:
    TOWEREBULLETDAMAGE = 10
  towerhitpoints = 50

  ### PCG part
  towers = []
  
  # randomly place features[0] towers on the field, multiple conditions : not in obstacle, not too close from the other towers, not too close from the hero base
  for i in range(0, features[0]) :
    towerLoc = (random.randint(0, world.getDimensions()[0]), random.randint(0, world.getDimensions()[1]))
    while ( (not isGood(towerLoc, world, 50))
            or (distance(towerLoc, (25, 25)) > 990)
            or (not isFar(towers[0:i], towerLoc, features[2])) ) :
        towerLoc = (random.randint(0, world.getDimensions()[0]), random.randint(0, world.getDimensions()[1]))

    towers.append(towerLoc)

  for tower in towers :
    theTower = Tower(TOWER, tower, world, 1, towerhitpoints, TOWERBULLETDAMAGE)
    world.addTower(theTower)
    
  world.setAreaFeature()

  while (world.areaFeature > 1.05*features[2]*features[0]) :

    prox = numpy.zeros(len(towers))
    index = 0

    for tower in towers :      
      for otherTower in towers :
        if tower == otherTower :
          continue
        if (not rayTraceWorld(tower, otherTower, world.getLines()) ) :
          continue
        if (distance(tower, otherTower) < 2*TOWERBULLETRANGE):
          prox[index] += 1

      if (prox[index] == 0) :
        prox[index] = 1

      index += 1

    theIndex = numpy.argmin(prox)


    previousAreaFeature = world.areaFeature

    while (world.areaFeature > 0.97*previousAreaFeature) :
      towers.pop(theIndex)
      towerLoc = (random.randint(0, world.getDimensions()[0]), random.randint(0, world.getDimensions()[1]))
      while ( (not isGood(towerLoc, world, 50))
              or (distance(towerLoc, (25, 25)) > 990)
              or (not isFarBis(towers[0:len(towers)-1], towerLoc, 175)) ) :
        towerLoc = (random.randint(0, world.getDimensions()[0]), random.randint(0, world.getDimensions()[1]))

      world.deleteTower(world.getTowers()[theIndex])
      theTower = Tower(TOWER, towerLoc, world, 1, towerhitpoints, TOWERBULLETDAMAGE)
      world.addTower(theTower)
      towers.insert(theIndex, towerLoc)

      world.setAreaFeature()

  world.levelDifficulty["numOfTower"] = features[0]
  world.levelDifficulty["powerOfTower"] = features[1]
  world.levelDifficulty["powerOfBase"] = BASEBULLETDAMAGE
  world.levelDifficulty["powerOfHero"] = BIGBULLETDAMAGE
  world.levelDifficulty["healthOfHero"] = 50

  print "PCG finishes."
  print "Number of towers: ", features[0]
  print "Tower damage: ", TOWEREBULLETDAMAGE
  print "Area features: ", world.areaFeature/features[0] #features[2]
  print "============================================================"
  return features


def isGood(point, world, threshold):
	if point[0] > 0 and point[0] < world.dimensions[0] and point[1] > 0 and point[1] < world.dimensions[1]:
		for o in world.obstacles:
			if pointInsidePolygonPoints(point, o.getPoints()):
				return False
		for l in world.getLines():
			if minimumDistance(l, point) < threshold:
				return False
		return True
	return False
