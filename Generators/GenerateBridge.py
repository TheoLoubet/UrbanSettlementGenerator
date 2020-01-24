import logging
import utilityFunctions as utilityFunctions
air_like = [0, 6, 17, 18, 30, 31, 32, 37, 38, 39, 40, 59, 81, 83, 85, 104, 105, 106, 107, 111, 141, 142, 161, 162, 175, 78, 79, 99]
water_like = [8, 9, 10, 11]

def generateBridge(matrix, height_map, p1, p2): #generate a bridge between p1 and p2
	logging.info("Trying to generate bridge between {} and {}".format(p1, p2))
	#finding height
	h1 = height_map[p1[0]][p1[1]]
	h2 = height_map[p2[0]][p2[1]]
	h_bridge = max(h1,h2)+2
	if min(h1,h2) == h1:
		min_point = p1
		max_point = p2
	else:
		min_point = p2
		max_point = p1

	cleanFundation(matrix, p1, height_map)
	cleanFundation(matrix, p2, height_map)

	#get the path for the 2 sides of the bridge
	logging.info("Get the path for the 2 sides of the bridge")
	middlepoint = (int((p1[0]+p2[0])/2),(int((p1[1]+p2[1])/2)))
	path_bridge1 = getPathBridge(matrix, p1, middlepoint) #first half
	path_bridge2 = getPathBridge(matrix, p2, middlepoint) #second half
	
	if utilityFunctions.getManhattanDistance(p1,p2) < 6:
		logging.info("Length of the bridge = {}, Bridge too small, building a small one".format(utilityFunctions.getManhattanDistance(p1,p2)))
		buildSmallBridge(matrix, path_bridge1, height_map)
		buildSmallBridge(matrix, path_bridge2, height_map)

	else:
		#check if the normal bridge is buildable 
		if height_map[min_point[0]][min_point[1]] + len(path_bridge1)*0.5 >= h_bridge:
			logging.info("Length of the bridge = {}, enough to go up on both sides, building a normal bridge".format(utilityFunctions.getManhattanDistance(p1,p2)))
			#build cross in the middle of the bridge
			matrix.setValue(h_bridge, middlepoint[0], middlepoint[1], (43,5))
			matrix.setValue(h_bridge, middlepoint[0]+1, middlepoint[1], (43,5))
			matrix.setValue(h_bridge, middlepoint[0]-1, middlepoint[1], (43,5))
			matrix.setValue(h_bridge, middlepoint[0], middlepoint[1]+1, (43,5))
			matrix.setValue(h_bridge, middlepoint[0], middlepoint[1]-1, (43,5))
			buildPillar(matrix, h_bridge-1, middlepoint)
			#build the bridge
			buildBridge(matrix, path_bridge1, h_bridge, h1+1, True) #first part of the bridge
			buildBridge(matrix, path_bridge2, h_bridge, h2+1 ,True) #second part
		else: #bridge can't be built that way, going up only from one side
			logging.info("Length of the bridge = {}, too small to go up on both sides, trying to go up only from the lowest point".format(utilityFunctions.getManhattanDistance(p1,p2)))
			path_bridge = getPathBridge(matrix, min_point, max_point) #full bridge
			if height_map[min_point[0]][min_point[1]] + len(path_bridge)*0.5 >= height_map[max_point[0]][max_point[1]]: #check if the difference of height is still too big
				logging.info("Bridge buildable from one side")
				buildBridge(matrix, path_bridge, max(h1,h2), min(h1,h2)+1, False)
			else:
				logging.info("Bridge non buildable")
				raise ValueError('Bridge non buildable')

def getPathBridge(matrix, p1, p2): #find a path to link p1 to p2
	path_bridge = []
	actual_point = p1
	path_bridge.append(actual_point)
	while actual_point != p2:
		if actual_point[0] < p2[0]:
			actual_point = (actual_point[0] + 1, actual_point[1])
			path_bridge.append(actual_point)
		if actual_point[0] > p2[0]:
			actual_point = (actual_point[0] - 1, actual_point[1])
			path_bridge.append(actual_point)
		if actual_point[1] < p2[1]:
			actual_point = (actual_point[0], actual_point[1] + 1)
			path_bridge.append(actual_point)
		if actual_point[1] > p2[1]:
			actual_point = (actual_point[0], actual_point[1] - 1)
			path_bridge.append(actual_point)
	return path_bridge

def buildBridge(matrix, path_bridge, h_bridge, h_start, normal_bridge):
	#check if the bridge is more x or z axis
	if abs(path_bridge[0][0] - path_bridge[len(path_bridge)-1][0]) >= abs(path_bridge[0][1] - path_bridge[len(path_bridge)-1][1]):
		x_val = 0
		z_val = 1
	else:
		x_val = 1
		z_val = 0

	#_______________________main path of the bridge______________________________
	is_half_block = True
	h_actual = h_start
	#start of the bridge
	matrix.setValue(h_actual, path_bridge[0][0], path_bridge[0][1], (44,5))
	fillUnder(matrix, h_actual, path_bridge[0][0], path_bridge[0][1])
	matrix.setValue(h_actual, path_bridge[1][0], path_bridge[1][1], (43,5))
	fillUnder(matrix, h_actual, path_bridge[1][0], path_bridge[1][1])

	for i in range(2, len(path_bridge)-1):
		#the bridge goes up
		if h_actual != h_bridge:
			if is_half_block == True: #check if we need to put a full block or 2 slabs
				matrix.setValue(h_actual, path_bridge[i][0], path_bridge[i][1], (44,13))
				matrix.setValue(h_actual+1, path_bridge[i][0], path_bridge[i][1], (44,5))
				h_actual += 1
			else:
				matrix.setValue(h_actual, path_bridge[i][0], path_bridge[i][1], (43,5))
			is_half_block = not is_half_block
		
		#max height reached
		else:
			matrix.setValue(h_bridge, path_bridge[i][0], path_bridge[i][1], (43,5))

	#_______________________extend the bridge on both sides______________________________
	is_half_block = True
	h_actual = h_start
	barrierPut = False
	#start of the bridge
	setIfCorrect(matrix, h_actual, path_bridge[0][0]-x_val, path_bridge[0][1]-z_val, (44,0))
	fillUnder(matrix, h_actual, path_bridge[0][0]-x_val, path_bridge[0][1]-z_val)
	setIfCorrect(matrix, h_actual, path_bridge[0][0]+x_val, path_bridge[0][1]+z_val, (44,0))
	fillUnder(matrix, h_actual, path_bridge[0][0]+x_val, path_bridge[0][1]+z_val)
	setIfCorrect(matrix, h_actual, path_bridge[1][0]-x_val, path_bridge[1][1]-z_val, (43,0))
	fillUnder(matrix, h_actual, path_bridge[1][0]-x_val, path_bridge[1][1]-z_val)
	setIfCorrect(matrix, h_actual, path_bridge[1][0]+x_val, path_bridge[1][1]+z_val, (43,0))
	fillUnder(matrix, h_actual, path_bridge[1][0]+x_val, path_bridge[1][1]+z_val)

	for i in range(2, len(path_bridge)-1):
		#the bridge goes up
		if h_actual != h_bridge:
			if is_half_block == True: #check if we need to put a full block or 2 slabs
				setIfCorrect(matrix, h_actual+1, path_bridge[i][0]-x_val, path_bridge[i][1]-z_val, (44,0))
				setIfCorrect(matrix, h_actual, path_bridge[i][0]-x_val, path_bridge[i][1]-z_val, (44,8))
				setIfCorrect(matrix, h_actual+1, path_bridge[i][0]+x_val, path_bridge[i][1]+z_val, (44,0))
				setIfCorrect(matrix, h_actual, path_bridge[i][0]+x_val, path_bridge[i][1]+z_val, (44,8))
				h_actual += 1
			else:
				setIfCorrect(matrix, h_actual, path_bridge[i][0]-x_val, path_bridge[i][1]-z_val, (43,0))
				setIfCorrect(matrix, h_actual, path_bridge[i][0]+x_val, path_bridge[i][1]+z_val, (43,0))
			is_half_block = not is_half_block
		
		#max height reached
		else:
			setIfCorrect(matrix, h_bridge, path_bridge[i][0]-x_val, path_bridge[i][1]-z_val, (43,0))
			setIfCorrect(matrix, h_bridge, path_bridge[i][0]+x_val, path_bridge[i][1]+z_val, (43,0))
			#Build the barrier and light when the direction is fixed if the bridge is normal
			if normal_bridge == True and barrierPut == False and len(path_bridge) - i >= 3:
				if path_bridge[i-1][0] != path_bridge[i][0] != path_bridge[i+1][0]:
					buildBarrierX(matrix, h_bridge, path_bridge[i:len(path_bridge)])
					barrierPut = True
				if path_bridge[i-1][1] != path_bridge[i][1] != path_bridge[i+1][1]:
					buildBarrierZ(matrix, h_bridge, path_bridge[i:len(path_bridge)])
					barrierPut = True

def fillUnder(matrix, h, x, z): #put blocks under the position if there is air
	(b, d) = utilityFunctions.getBlockFullValue(matrix, h, x, z)
	if (b, d) in [(44,13),(44,8)]:
		matrix.setValue(h, x, z, (b-1, d-8))
	h -= 1
	while matrix.getValue(h, x, z) in air_like+water_like:
		matrix.setValue(h, x, z, (43,8))
		h -= 1

def cleanAbove(matrix, h, x, z): #erase block above the block selected
	h += 1
	while matrix.getValue(h, x, z) not in air_like:
		matrix.setValue(h, x, z, 0)
		h += 1

def setIfCorrect(matrix, h, x, z, i): #put block only if the position given is correct
	(b,d) = utilityFunctions.getBlockFullValue(matrix, h-1, x, z)
	if matrix.getValue(h, x, z) in air_like and (b,d) not in [(43,0),(44,8),(44,0),(43,5),(44,13),(44,5)]:
		matrix.setValue(h, x, z, i)


def buildPillar(matrix, h, p): #build a pillar in the water as support to bridge
	while matrix.getValue(h, p[0], p[1]) in air_like:
		matrix.setValue(h, p[0], p[1], (139,0))
		h -= 1
	while matrix.getValue(h, p[0], p[1]) in water_like:
		matrix.setValue(h, p[0], p[1], (4,0))
		h -= 1

def buildBarrierX(matrix, h_bridge, path_bridge): #build barrier on the bridge going through the X axis
	putLight(matrix, h_bridge, path_bridge[0][0], path_bridge[0][1]-2)
	putLight(matrix, h_bridge, path_bridge[0][0], path_bridge[0][1]+2)
	for i in range(1, len(path_bridge)):
		matrix.setValue(h_bridge+1, path_bridge[i][0], path_bridge[i][1]-2, (139,0))
		matrix.setValue(h_bridge+1, path_bridge[i][0], path_bridge[i][1]+2, (139,0))

def buildBarrierZ(matrix, h_bridge, path_bridge): #build barrier on the bridge going through the Z axis
	putLight(matrix, h_bridge, path_bridge[0][0]-2, path_bridge[0][1])
	putLight(matrix, h_bridge, path_bridge[0][0]+2, path_bridge[0][1])
	for i in range(1, len(path_bridge)):
		matrix.setValue(h_bridge+1, path_bridge[i][0]-2, path_bridge[i][1], (139,0))
		matrix.setValue(h_bridge+1, path_bridge[i][0]+2, path_bridge[i][1], (139,0))

def putLight(matrix, h, x, z): #build a light and a pillar under it
	matrix.setValue(h+1,x,z,(139,0))
	matrix.setValue(h+2,x,z,(139,0))
	matrix.setValue(h+3,x,z,(123,0))
	matrix.setEntity(h+4, x, z, (178,15), "daylight_detector")
	buildPillar(matrix, h, (x, z))

def cleanFundation(matrix, p, height_map): #clean the endpoints of the bridge
	h = height_map[p[0]][p[1]]
	for neighbor_position in [(0, 0), (0, -1), (0, 1), (-1, 0), (1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
		position_to_clean = (p[0] + neighbor_position[0], p[1] + neighbor_position[1])
		if abs(height_map[position_to_clean[0]][position_to_clean[1]] - h) <= 3:
			cleanAbove(matrix, h, position_to_clean[0], position_to_clean[1])
			height_map[position_to_clean[0]][position_to_clean[1]] = h
		matrix.setValue(h, position_to_clean[0], position_to_clean[1], (1,6))
		fillUnder(matrix, h, position_to_clean[0], position_to_clean[1])

def buildSmallBridge(matrix, path_bridge, height_map):
	if abs(path_bridge[0][0] - path_bridge[len(path_bridge)-1][0]) >= abs(path_bridge[0][1] - path_bridge[len(path_bridge)-1][1]):
		x_val = 0
		z_val = 1
	else:
		x_val = 1
		z_val = 0

	for i in range(0, len(path_bridge)):
		x = path_bridge[i][0]
		z = path_bridge[i][1]
		h = height_map[x][z]
		matrix.setValue(h, x, z, (43,5))

	#cross middle of the bridge
	matrix.setValue(height_map[path_bridge[len(path_bridge)-1][0]][path_bridge[len(path_bridge)-1][1]], path_bridge[len(path_bridge)-1][0], path_bridge[len(path_bridge)-1][1], (43,5))
	matrix.setValue(height_map[path_bridge[len(path_bridge)-1][0]][path_bridge[len(path_bridge)-1][1]], path_bridge[len(path_bridge)-1][0]+1, path_bridge[len(path_bridge)-1][1], (43,5))
	matrix.setValue(height_map[path_bridge[len(path_bridge)-1][0]][path_bridge[len(path_bridge)-1][1]], path_bridge[len(path_bridge)-1][0], path_bridge[len(path_bridge)-1][1]+1, (43,5))
	matrix.setValue(height_map[path_bridge[len(path_bridge)-1][0]][path_bridge[len(path_bridge)-1][1]], path_bridge[len(path_bridge)-1][0]-1, path_bridge[len(path_bridge)-1][1], (43,5))
	matrix.setValue(height_map[path_bridge[len(path_bridge)-1][0]][path_bridge[len(path_bridge)-1][1]], path_bridge[len(path_bridge)-1][0], path_bridge[len(path_bridge)-1][1]-1, (43,5))

	for i in range(0, len(path_bridge)-1):
		setIfCorrect(matrix, height_map[path_bridge[i][0]-x_val][path_bridge[i][1]-z_val], path_bridge[i][0]-x_val, path_bridge[i][1]-z_val, (43,8))
		setIfCorrect(matrix, height_map[path_bridge[i][0]+x_val][path_bridge[i][1]+z_val], path_bridge[i][0]+x_val, path_bridge[i][1]+z_val, (43,8))