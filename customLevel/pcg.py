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


def PCG(world, score, model):

  features = [random.randint(4, 12), random.randint(2,5)]
  coeff = random.uniform(0.6, 1)
  features.append(features[0]*coeff)

  coeffs = model.getParams()

  while (model.testScore(features) > score) :
    features[0] -= 1
    features[2] -= coeff
  while (model.testScore(features) < score) :
    features[0] += 1 
    features[2] += coeff
  
  while (model.testScore(features) > score) and (coeff > 0.6) :
    coeff -= 0.05
    features[2] = features[0]*coeff

  features[1] = (score - features[0]*coeffs[0] - features[2]*coeffs[2])/coeffs[1]
  towerhitpoints = 50 + 25*(features[1]/3)
  towerbulletdamage = ((features[1]%3)+2)*5

  ### optimzation part
  #target = score
  #SA = SimulatedAnnealing(model, target)
  #features = SA.finalState()
  #features = (int(round(features[0])), features[2], features[3]) # take three feature from level.txt
  #print "Optimized features: ", features
  #model.testScore(features)

  ### PCG part
  towers = []
  
  # randomly place features[0] towers on the field, multiple conditions : not in obstacle, not too close from the other towers, not too close from the hero base
  for i in range(0, features[0]) :
    towerLoc = (random.randint(0, world.getDimensions()[0]), random.randint(0, world.getDimensions()[1]))

    while ( (not isGood(towerLoc, world, 50))
            or (distance(towerLoc, (25, 25)) > 990)
            or (not isFar(towers[0:i], towerLoc, coeff)) ) :
        towerLoc = (random.randint(0, world.getDimensions()[0]), random.randint(0, world.getDimensions()[1]))

    towers.append(towerLoc)

  for tower in towers :
    theTower = Tower(TOWER, tower, world, 1, towerhitpoints)
    TOWEREBULLETDAMAGE = towerbulletdamage
    world.addTower(theTower)
    
  world.setAreaFeature()
  


  while (world.areaFeature > 1.05*features[2]) :

    locs = []
    dists = []

    for tower in towers :
      loc1 = (0,0)
      loc2 = (0,0)
      first = true
      
      for otherTower in towers :
        if tower == otherTower :
          continue
        if first :
          loc1 = otherTower
          first = false

        if (distance(tower, loc1) > distance(tower, otherTower)):
          loc2 = loc1
          loc1 = otherTower
        elif (distance(tower, loc2) > distance(tower, otherTower)):
          loc2 = otherTower
          
      if ( (not rayTraceWorld(tower, loc1, world.getLines()))
           or (not rayTraceWorld(tower, loc2, world.getLines()))
           or (not rayTraceWorld(loc1, loc2, world.getLines())) ) :
        dists.append(0)
      else :
        dists.append(distance(tower, loc1) + distance(tower, loc2))
      locs.append(loc1, loc2)
    
    index = dists.index(max(dists))
    if (dists[index] == 0) :
      break
      
    if (distance(locs[index][0], towers[index]) > 2*TOWERBULLETRANGE) :
      thePosition = ((2*locs[index][0][0] + towers[index][0])/3, (2*locs[index][0][1] + towers[index][1])/3)
      world.getTowers()[index].rect.move(thePosition)
    else :
      thePosition = ((locs[index][0][0] + locs[index][1][0])/2, (locs[index][0][1] + locs[index][1][1])/2)
      world.getTowers()[index].rect.move(thePosition)

    previousAreaFeature = world.areaFeature
    world.setAreaFeature()
    if (abs(world.areaFeature-previousAreaFeature) < 0.05) :
      break

  print features
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
