import sys, pygame, math, numpy, random, time, copy

from pygame.locals import * 
from constants import *
from customLevel.optimization import SimulatedAnnealing


########################
### PYGAME STUFF

def load_image(name, colorkey=None):
  image = pygame.image.load(name)
  image = image.convert()
  if colorkey is not None:
    if colorkey is -1:
      colorkey = image.get_at((0,0))
    image.set_colorkey(colorkey, RLEACCEL)
  return image, image.get_rect()


############################
### OTHER STUFF

### Distance between two points
def distance(p1, p2):
	return (((p2[0]-p1[0])**2) + ((p2[1]-p1[1])**2))**0.5
  
# Calc the gradient 'm' of a line between p1 and p2
def calculateGradient(p1, p2):
  
	# Ensure that the line is not vertical
	if (p1[0] != p2[0]):
		m = (p1[1] - p2[1]) / float(p1[0] - p2[0])
		return m
	else:
		return None
 
# Calc the point 'b' where line crosses the Y axis
def calculateYAxisIntersect(p, m):
	return  p[1] - (m * p[0])
 
# Calc the point where two infinitely long lines (p1 to p2 and p3 to p4) intersect.
# Handle parallel lines and vertical lines (the later has infinite 'm').
# Returns a point tuple of points like this ((x,y),...)  or None
# In non parallel cases the tuple will contain just one point.
# For parallel lines that lay on top of one another the tuple will contain
# all four points of the two lines
def getIntersectPoint(p1, p2, p3, p4):
	m1 = calculateGradient(p1, p2)
	m2 = calculateGradient(p3, p4)
      
	# See if the the lines are parallel
	if (m1 != m2):
		# Not parallel
      
		# See if either line is vertical
		if (m1 is not None and m2 is not None):
			# Neither line vertical           
			b1 = calculateYAxisIntersect(p1, m1)
			b2 = calculateYAxisIntersect(p3, m2)  
			x = (b2 - b1) / float(m1 - m2)       
			y = (m1 * x) + b1           
		else:
			# Line 1 is vertical so use line 2's values
			if (m1 is None):
				b2 = calculateYAxisIntersect(p3, m2)   
				x = p1[0]
				y = (m2 * x) + b2
			# Line 2 is vertical so use line 1's values               
			elif (m2 is None):
				b1 = calculateYAxisIntersect(p1, m1)
				x = p3[0]
				y = (m1 * x) + b1           
			else:
				assert false
              
		return ((x,y),)
	else:
		# Parallel lines with same 'b' value must be the same line so they intersect
		# everywhere in this case we return the start and end points of both lines
		# the calculateIntersectPoint method will sort out which of these points
		# lays on both line segments
		b1, b2 = None, None # vertical lines have no b value
		if m1 is not None:
			b1 = calculateYAxisIntersect(p1, m1)
          
		if m2 is not None:   
			b2 = calculateYAxisIntersect(p3, m2)
      
		# If these parallel lines lay on one another   
		if b1 == b2:
			return p1,p2,p3,p4
		else:
			return None  
  
  
 
# For line segments (ie not infinitely long lines) the intersect point
# may not lay on both lines.
#   
# If the point where two lines intersect is inside both line's bounding
# rectangles then the lines intersect. Returns intersect point if the line
# intesect o None if not
def calculateIntersectPoint(p1, p2, p3, p4):
	p = getIntersectPoint(p1, p2, p3, p4)
	if p is not None:
		p = p[0]
		if p[0] >= min(p1[0], p2[0]) and p[0] <= max(p1[0], p2[0]) and p[1] >= min(p1[1], p2[1]) and p[1] <= max(p1[1], p2[1]) and p[0] >= min(p3[0], p4[0]) and p[0] <= max(p3[0], p4[0]) and p[1] >= min(p3[1], p4[1]) and p[1] <= max(p3[1], p4[1]):
			return p
	return None



def rayTrace(p1, p2, line):
	return calculateIntersectPoint(line[0], line[1], p1, p2)
	#pygame.draw.line(background, (0, 0, 0), p1, p2)
	
def rayTraceWorld(p1, p2, worldLines):
	for l in worldLines:
		hit = rayTrace(p1, p2, l)
		if hit != None:
			return hit
	return None

# Check whether two lines intersect anywhere except within a given distance of an endpoint
def rayTraceWithThreshold(p1, p2, line, threshold):
	hitpoint = calculateIntersectPoint(line[0], line[1], p1, p2)
	if hitpoint != None and withinRangeOfPoints(hitpoint, threshold, line) == False:
		return hitpoint
	return None

# Check whether the line between p1 and p2 intersects any other line, except within a given distance of an endpoint of those lines.
def rayTraceWorldWithThreshold(p1, p2, worldLines, threshold):
	for l in worldLines:
		hit = rayTraceWithThreshold(p1, p2, l, threshold)
		if hit != None:
			return hit
	return None

# Check whether the line between p1 and p2 intersects with line anywhere except an endpoint.
def rayTraceNoEndpoints(p1, p2, line):
	# They are the same line: bad
	if (p1 == line[0] and p2 == line[1]) or (p2 == line[0] and p1 == line[1]):
		return p1
	# They are not the same line but share an endpoint: good
	if (p1 == line[0] or p2 == line[1]) or (p2 == line[0] or p1 == line[1]):
		return None
	# They do not share any points
	hitpoint = calculateIntersectPoint(line[0], line[1], p1, p2)
	if hitpoint != None:
		return hitpoint
	return None

# Check whether the line between p1 and p2 intersects any line anywhere except an endpoint of any of the lines.
def rayTraceWorldNoEndPoints(p1, p2, worldLines):
	for l in worldLines:
		hit = rayTraceNoEndpoints(p1, p2, l)
		if hit != None:
			return hit
	return None


# Return minimum distance between line segment and point
def minimumDistance(line, point):
	d2 = distance(line[1], line[0])**2.0
	if d2 == 0.0: 
		return distance(point, line[0])
	# Consider the line extending the segment, parameterized as line[0] + t (line[1] - line[0]).
	# We find projection of point p onto the line. 
	# It falls where t = [(point-line[0]) . (line[1]-line[0])] / |line[1]-line[0]|^2
	p1 = (point[0] - line[0][0], point[1] - line[0][1])
	p2 = (line[1][0] - line[0][0], line[1][1] - line[0][1])
	t = dotProduct(p1, p2) / d2  # numpy.dot(p1, p2) / d2
	if t < 0.0: 
		return distance(point, line[0])	# Beyond the line[0] end of the segment
	elif t > 1.0: 
		return distance(point, line[1])	# Beyond the line[1] end of the segment
	p3 = (line[0][0] + (t * (line[1][0] - line[0][0])), line[0][1] + (t * (line[1][1] - line[0][1]))) # projection falls on the segment
	return distance(point, p3)


#Polygon is a set of points
def pointOnPolygon(point, polygon):
	last = None
	for p in polygon:
		if last != None:
			mid = ((last[0]+p[0])/2.0, (last[1]+p[1])/2.0)
			if withinRange(point, mid, 1.5):
				return True
		last = p
	mid = ((polygon[0][0]+polygon[len(polygon)-1][0])/2.0, (polygon[0][1]+polygon[len(polygon)-1][1])/2.0)
	if withinRange(point, mid, 1.5):
		return True
	return False

def withinRange(p1, p2, range):
	return distance(p1, p2) <= range

def withinRangeOfPoints(point, range, list):
	for pt in list:
		if withinRange(point, pt, range):
			return True
	return False

def drawPolygon(poly, screen, color = (0, 0, 0), width = 1, center = False):
	last = None
	for p in poly:
		if last != None:
			pygame.draw.line(screen, color, last, p, width)
		last = p
	pygame.draw.line(screen, color, poly[0], poly[len(poly)-1], width)
	if center:
		c = ( sum(map(lambda p: p[0], poly))/float(len(poly)), sum(map(lambda p: p[1], poly))/float(len(poly)) )
		pygame.draw.line(screen, color, (c[0]-2, c[1]-2), (c[0]+2, c[1]+2), 1)
		pygame.draw.line(screen, color, (c[0]+2, c[1]-2), (c[0]-2, c[1]+2), 1)

def commonPoints(poly1, poly2):
	#if two triangles share 2 points, they are adjacent
	points = []
	for p1 in poly1:
		for p2 in poly2:
			if p1 == p2:
				points.append(p1)
	return points

def polygonsAdjacent(poly1, poly2):
	points = commonPoints(poly1, poly2)
	if len(points) == 2:
		return points
	else:
		return False
		
def isConvex(points):
	p1 = None
	p2 = None
	negpos = 0
	for p3 in points:
		if p1 != None and p2 != None:
			#cross product must always be the same sign
			zcross = crossProduct(p1, p2, p3)
			if negpos == 0:
				if zcross >= 0:
					negpos = 1
				else:
					negpos = -1
			elif negpos >= 0 and zcross < 0:
				return False
			elif negpos < 0 and zcross > 0:
				return False
		p1 = p2
		p2 = p3
	#Do the last check
	zcross = crossProduct(points[len(points)-2], points[len(points)-1], points[0])
	if negpos >= 0 and zcross < 0:
		return False
	elif negpos < 0 and zcross > 0:
		return False
	zcross = crossProduct(points[len(points)-1], points[0], points[1])
	if negpos >= 0 and zcross < 0:
		return False
	elif negpos < 0 and zcross > 0:
		return False
	else:
		return True
	
def crossProduct(p1, p2, p3):
	dx1 = p2[0] - p1[0]
	dy1 = p2[1] - p1[1]
	dx2 = p3[0] - p2[0]
	dy2 = p3[1] - p2[1]
	return (dx1*dy2) - (dy1*dx2)
	
def dotProduct(p1, p2):
	return (p1[0]*p2[0]) + (p1[1]*p2[1])


#Special routine for appending a line to a list of lines, making sure there are no duplicates added. Changes made by side-effect.
def appendLineNoDuplicates(line, lines):
	if (line in lines) == False and (reverseLine(line) in lines) == False:
		return lines.append(line)
	else:
		return lines
	
#Reverse the order of points in a line.	
def reverseLine(line):
	return (line[1], line[0])
	
#Determine whether a point is inside an simple polygon. Polygon is a set of lines.
def pointInsidePolygonLines(point, polygon):
	count = 0
	for l in polygon:
		if rayTrace(point, (-10, SCREEN[1]/2.0), l) != None:
			count = count + 1
	return count%2 == 1

#Determine whether a point is inside an simple polygon. Polygon is a set of points.
def pointInsidePolygonPoints(point, polygon):
	lines = []
	last = None
	for p in polygon:
		if last != None:
			lines.append((last, p))
		last = p
	lines.append((polygon[len(polygon)-1], polygon[0]))
	return pointInsidePolygonLines(point, lines)

# Angle between two lines originating at (0, 0). Lenght of lines must be greater than 0.
def angle(pt1, pt2):
	x1, y1 = pt1
	x2, y2 = pt2
	inner_product = x1*x2 + y1*y2
	len1 = math.hypot(x1, y1)
	len2 = math.hypot(x2, y2)
	return math.acos(inner_product/(len1*len2))

def vectorMagnitude(v):
	return reduce(lambda x, y: (x**2)+(y**2), v)**0.5
	
# Find the point in nodes closest to p that is unobstructed
# NOTE: there is a problem in that this function doesn't compute whether there is enough clearance for an agent to get to the nearest unobstructed point
def findClosestUnobstructed(p, nodes, worldLines):
	best = None
	dist = INFINITY
	for n in nodes:
		if rayTraceWorld(p, n, worldLines) == None:
			d = distance(p, n)
			if best == None or d < dist:
				best = n
				dist = d
	return best

#def findClosestUnobstructed(p, nodes, worldLines, worldPoints = [], threshold = 0.0):
#	best = None
#	dist = INFINITY
#	for n in nodes:
#		if rayTraceWorld(p, n, worldLines) == None:
#			tooclose = False
#			for p2 in worldPoints:
#				if minimumDistance((p, n), p2) <= threshold:
#					tooclose = True
#					break
#			if not tooclose:
#				d = distance(p, n)
#				if best == None or d < dist:
#					best = n
#					dist = d
#	return best


	
def drawCross(surface, point, color = (0, 0, 0), size = 2, width = 1):
	pygame.draw.line(surface, color, (point[0]-size, point[1]-size), (point[0]+size, point[1]+size), width)
	pygame.draw.line(surface, color, (point[0]+size, point[1]-size), (point[0]-size, point[1]+size), width)


### function that will write the game statistics and configuration of level (including the score)
def writeGameStatistics(world):
    timeElapse = time.clock() - world.getStartTime()
    print "Time Elapse: ", timeElapse

    # calculate score for the game
    score = float(dealt) / (1 + 0.5 * math.sqrt(taken))
    score = score / (1 + elapse / (total))
    print "Score: ", score

    currentTime = time.strftime("%b-%d-%Y %H:%M:%S", time.gmtime())
    file = open("player.txt", "a")
    file.write(currentTime + "\t" + str(timeElapse) + "\t" + str(world.playerDeaths) + "\t" + str(world.damageTaken) + "\t" + str(world.damageDealt) \
        + "\t" + str(world.deathsByCollision) + "\t" + str(world.damageToTower) + "\t" + str(world.damageToBase) \
        + "\t" + str(world.numOfDodges) + "\t" + str(world.numOfBullets) + "\n")

    file = open("level.txt", "a")
    file.write(str(world.levelDifficulty["numOfTower"]) + "\t" + str(world.levelDifficulty["powerOfTower"]) + "\t" + str(world.levelDifficulty["powerOfHero"]) \
        + "\t" + str(world.areaFeature) + "\t" + str(score) + "\n")


# function that will determine the size of the area where our hero can be shot by a tower
# the closer towers are, the more they cover the same area ==> this area is reduced
# the smallest this area is, the harder it is to target one tower and not being targeted by multiple tower, it seems to be a good feature for the difficulty
def calculateTowerProximityFeature(world):


  mapApprox = numpy.zeros((world.dimensions[0]/10, world.dimensions[1]/10))
  first = True
  singleArea = 0
  totalArea = 0

  for tower in world.getTowers() :
    center = tower.getLocation()
    orig = (max(0, math.floor((center[0]-TOWERBULLETRANGE) / 10)) , max(0, math.floor((center[1]-TOWERBULLETRANGE) / 10)) )
    end = (min(world.dimensions[0]/10 - 1, math.floor((center[0]+TOWERBULLETRANGE) / 10)) , min(world.dimensions[1]/10 - 1, math.floor((center[1]+TOWERBULLETRANGE) / 10)) )


    for y in range((int)(orig[1]), (int)(end[1])+1) :
      for x in range((int)(orig[0]), (int)(end[0])+1) :
        thePoint = (10*x + 5, 10*y + 5)
        if (distance(thePoint, center) <= TOWERBULLETRANGE) :
          if (mapApprox[x][y] == 0) :
            totalArea += 1
          mapApprox[x][y] = 1
          if first :
            singleArea += 1

    first = False



  floatTotalArea = (float)(totalArea)/(float)(singleArea)

  return floatTotalArea



def isFar(towers, towerLoc, coeff) :

  thebool = false
  for tower in towers :
    if (distance(tower, towerLoc) < 0.6*coeff*TOWERBULLETRANGE) :
      return false
    if (distance(tower, towerLoc) < 3*TOWERBULLETRANGE) :
      thebool = true

  return thebool


def PCG(world, score, model):

  # features = [random.randint(4, 12), 30, 5]
  # coeff = random.uniform(0.6, 1)
  # features.append(features[0]*coeff)

  # coeffs = model.getParams()
  # print coeffs

  # while (model.testScore(features) > score) :
  #   print "features", model.testScore(features)
  #   print "score: ", score
  #   features[0] += 1
  #   features[3] += coeff
  # while (model.testScore(features) < score) :
  #   print "features", model.testScore(features)
  #   print "score: ", score
  #   features[0] -= 1 
  #   features[3] -= coeff

  #   print "features", model.testScore(features)
  #   print "score: ", score
  
  # while (model.testScore(features) < score) and (coeff > 0.6) :
  #   coeff -= 0.05
  #   features[3] = features[0]*coeff
  
  ### optimzation part
  target = score
  SA = SimulatedAnnealing(model, target)
  features = SA.finalState()
  features = (int(round(features[0])), features[2], features[3]) # take three feature from level.txt
  print "Optimized features: ", features

  ### PCG part
  towers = []
  
  # randomly place features[0] towers on the field, multiple conditions : not in obstacle, not too close from the other towers, not too close from the hero base
  for i in range(0, features[0]) :
    towerLoc = (random.randint(0, world.getDimensions()[0]), random.randint(0, world.getDimensions()[1]))

    while ( (not isGood(towerLoc, world, 50))
            or (distance(towerLoc, (25, 25)) > 2/3*distance((25, 25), (1075, 1075)))
            or (not isFar(towers[0:i], towerLoc, coeff)) ) :
      towerLoc = (random.randint(0, world.getDimensions()[0]), random.randint(0, world.getDimensions()[1]))

    towers.append(towerLoc)

  for tower in towers :
    world.addTower(Tower(TOWER, tower, world, 1))

  world.setAreaFeature()
  


  while (world.areaFeature > 1.05*features[3]) :

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

  features[1] = score - coeffs[0]*features[0] - coeffs[2]*features[2] - coeffs[3]*world.areaFeature

  print "la"
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
