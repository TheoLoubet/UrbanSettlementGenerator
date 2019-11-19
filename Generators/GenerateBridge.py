import logging
import utilityFunctions as utilityFunctions
air_like = [0, 6, 17, 18, 30, 31, 32, 37, 38, 39, 40, 59, 81, 83, 85, 104, 105, 106, 107, 111, 141, 142, 161, 162, 175, 78, 79, 99]
water_like = [8, 9, 10, 11]

def generateBridge(matrix, height_map, p1, p2): #generate a bridge between p1 and p2
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

	cleanFundation(matrix, p1, h1, height_map)
	cleanFundation(matrix, p2, h2, height_map)

	#get the path for the 2 side of the bridge
	middlepoint = (int((p1[0]+p2[0])/2),(int((p1[1]+p2[1])/2)))
	path_bridge1 = getPathBridge(matrix, p1, middlepoint) #first half
	path_bridge2 = getPathBridge(matrix, p2, middlepoint) #second half

	#check if this bridge is buildable 
	if h1 + len(path_bridge1)*0.5 >= h_bridge and h2 + len(path_bridge2)*0.5 >= h_bridge:
		#build the bridge
		buildBridge(matrix, path_bridge1, h_bridge, h1+1, middlepoint, 'y') #we build the pillar in the middle point only once
		buildBridge(matrix, path_bridge2, h_bridge, h2+1, None, 'y')
	else: #bridge can't be built that way, going up only from one side
		path_bridge = getPathBridge(matrix, min_point, max_point) #full bridge
		buildBridge(matrix, path_bridge, max(h1,h2), h1+1, None, 'n')

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

def buildBridge(matrix, path_bridge, h_bridge, h_start, middlepoint, normal_bridge):
	isDemi = True
	h_actual = h_start
	barrierPut = False
	#start point of the bridge
	matrix.setValue(h_actual, path_bridge[0][0], path_bridge[0][1], (44,5))
	fillUnder(matrix, h_actual, path_bridge[0][0], path_bridge[0][1])
	matrix.setValue(h_actual, path_bridge[1][0], path_bridge[1][1], (43,5))
	fillUnder(matrix, h_actual, path_bridge[1][0], path_bridge[1][1])

	#main part of the bridge
	for i in range(2, len(path_bridge)-1):
		#the bridge height goes up
		if h_actual != h_bridge:
			if isDemi == True: #check if we need to put a full block or 2 slabs
				matrix.setValue(h_actual, path_bridge[i][0], path_bridge[i][1], (44,13))
				matrix.setValue(h_actual+1, path_bridge[i][0], path_bridge[i][1], (44,5))
				h_actual += 1
			else:
				matrix.setValue(h_actual, path_bridge[i][0], path_bridge[i][1], (43,5))
			isDemi = not isDemi
		
		#max height reached
		else:
			matrix.setValue(h_bridge, path_bridge[i][0], path_bridge[i][1], (43,5))

	#build cross in the middle
	if middlepoint != None:
		matrix.setValue(h_bridge, middlepoint[0], middlepoint[1], (43,5))
		matrix.setValue(h_bridge, middlepoint[0]+1, middlepoint[1], (43,5))
		matrix.setValue(h_bridge, middlepoint[0]-1, middlepoint[1], (43,5))
		matrix.setValue(h_bridge, middlepoint[0], middlepoint[1]+1, (43,5))
		matrix.setValue(h_bridge, middlepoint[0], middlepoint[1]-1, (43,5))
		buildPillar(matrix, h_bridge-1, middlepoint)

	#extend the bridge on both sides #CHECK IF A TOP SLAB IS PUT ON A BLOCK (AND THAT THE BOTTOM SLAB WASN'T BUILT) and check if a top slab is being built on a bottom slab, replace it by a full block
	isDemi = True
	h_actual = h_start
	barrierPut = False
	#start point of the bridge
	#search the right way to extend bridge
	if path_bridge[0][0] != path_bridge[1][0]:
		setIfEmpty(matrix, h_actual, path_bridge[0][0], path_bridge[0][1]-1, (44,0))
		fillUnder(matrix, h_actual, path_bridge[0][0], path_bridge[0][1]-1)
		setIfEmpty(matrix, h_actual, path_bridge[0][0], path_bridge[0][1]+1, (44,0))
		fillUnder(matrix, h_actual, path_bridge[0][0], path_bridge[0][1]+1)
	elif path_bridge[0][1] != path_bridge[1][1]:
		setIfEmpty(matrix, h_actual, path_bridge[0][0]-1, path_bridge[0][1], (44,0))
		fillUnder(matrix, h_actual, path_bridge[0][0]-1, path_bridge[0][1])
		setIfEmpty(matrix, h_actual, path_bridge[0][0]+1, path_bridge[0][1], (44,0))
		fillUnder(matrix, h_actual, path_bridge[0][0]+1, path_bridge[0][1])
	#search the right way to extend bridge
	if path_bridge[1][0] != path_bridge[2][0]:
		setIfEmpty(matrix, h_actual, path_bridge[1][0], path_bridge[1][1]-1, (43,0))
		fillUnder(matrix, h_actual, path_bridge[1][0], path_bridge[1][1]-1)
		setIfEmpty(matrix, h_actual, path_bridge[1][0], path_bridge[1][1]+1, (43,0))
		fillUnder(matrix, h_actual, path_bridge[1][0], path_bridge[1][1]+1)
	elif path_bridge[1][1] != path_bridge[2][1]:
		setIfEmpty(matrix, h_actual, path_bridge[1][0]-1, path_bridge[1][1], (43,0))
		fillUnder(matrix, h_actual, path_bridge[1][0]-1, path_bridge[1][1])
		setIfEmpty(matrix, h_actual, path_bridge[1][0]+1, path_bridge[1][1], (43,0))
		fillUnder(matrix, h_actual, path_bridge[1][0]+1, path_bridge[1][1])

	#main part of the bridge
		for i in range(2, len(path_bridge)-1):
			#the bridge height goes up
			if h_actual != h_bridge:
				if isDemi == True: #check if we need to put a full block or 2 slabs
					#search the right way to extend bridge
					if path_bridge[i][0] != path_bridge[i+1][0]:
						setIfEmpty(matrix, h_actual, path_bridge[i][0], path_bridge[i][1]-1, (44,8))
						setIfEmpty(matrix, h_actual+1, path_bridge[i][0], path_bridge[i][1]-1, (44,0))
						setIfEmpty(matrix, h_actual, path_bridge[i][0], path_bridge[i][1]+1, (44,8))
						setIfEmpty(matrix, h_actual+1, path_bridge[i][0], path_bridge[i][1]+1, (44,0))
					elif path_bridge[i][1] != path_bridge[i+1][1]:
						setIfEmpty(matrix, h_actual, path_bridge[i][0]-1, path_bridge[i][1], (44,8))
						setIfEmpty(matrix, h_actual+1, path_bridge[i][0]-1, path_bridge[i][1], (44,0))
						setIfEmpty(matrix, h_actual, path_bridge[i][0]+1, path_bridge[i][1], (44,8))
						setIfEmpty(matrix, h_actual+1, path_bridge[i][0]+1, path_bridge[i][1], (44,0))
					h_actual += 1
				else:
					#search the right way to extend bridge
					if path_bridge[i][0] != path_bridge[i+1][0]:
						setIfEmpty(matrix, h_actual, path_bridge[i][0], path_bridge[i][1]-1, (43,0))
						setIfEmpty(matrix, h_actual, path_bridge[i][0], path_bridge[i][1]+1, (43,0))
					elif path_bridge[i][1] != path_bridge[i+1][1]:
						setIfEmpty(matrix, h_actual, path_bridge[i][0]-1, path_bridge[i][1], (43,0))
						setIfEmpty(matrix, h_actual, path_bridge[i][0]+1, path_bridge[i][1], (43,0))
				isDemi = not isDemi
			
			#max height reached
			else:
				#search the right way to extend bridge
				if path_bridge[i][0] != path_bridge[i+1][0]:
					setIfEmpty(matrix, h_bridge, path_bridge[i][0], path_bridge[i][1]-1, (43,0))
					setIfEmpty(matrix, h_bridge, path_bridge[i][0], path_bridge[i][1]+1, (43,0))
				elif path_bridge[i][1] != path_bridge[i+1][1]:
					setIfEmpty(matrix, h_bridge, path_bridge[i][0]-1, path_bridge[i][1], (43,0))
					setIfEmpty(matrix, h_bridge, path_bridge[i][0]+1, path_bridge[i][1], (43,0))
				#Build the barrier and light when the direction is fixed if the bridge is normal
				if normal_bridge == 'y':	
					if barrierPut == False and path_bridge[i-1][0] != path_bridge[i][0] != path_bridge[i+1][0]:
						buildBarrierX(matrix, h_bridge, path_bridge[i:len(path_bridge)])
						barrierPut = True
					if barrierPut == False and path_bridge[i-1][1] != path_bridge[i][1] != path_bridge[i+1][1]:
						buildBarrierZ(matrix, h_bridge, path_bridge[i:len(path_bridge)])
						barrierPut = True

def fillUnder(matrix, h, x, z): #put path blocks under the position if there is air
	#also check if it's a top slab to replace it by a full block
	h -= 1
	while matrix.getValue(h, x, z) in air_like+water_like:
		matrix.setValue(h, x, z, (1,6))
		h -= 1

def cleanAbove(matrix, h, x, z):
	h += 1
	while matrix.getValue(h, x, z) not in air_like:
		matrix.setValue(h, x, z, 0)
		h += 1

def setIfEmpty(matrix, h, x, z, i): #put block only if the position given or the one under is not occupied by a bridge block (bb)
	if matrix.getValue(h, x, z) in air_like:
		matrix.setValue(h, x, z, i)
	#also check if it's a bottom slab to replace it by a full block


def buildPillar(matrix, h, p): #build a pillar in the water to support the bridge
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
		setIfEmpty(matrix, h_bridge+1, path_bridge[i][0], path_bridge[i][1]-2, 139)
		setIfEmpty(matrix, h_bridge+1, path_bridge[i][0], path_bridge[i][1]+2, 139)

def buildBarrierZ(matrix, h_bridge, path_bridge): #build barrier on the bridge going through the Z axis
	putLight(matrix, h_bridge, path_bridge[0][0]-2, path_bridge[0][1])
	putLight(matrix, h_bridge, path_bridge[0][0]+2, path_bridge[0][1])
	for i in range(1, len(path_bridge)):
		setIfEmpty(matrix, h_bridge+1, path_bridge[i][0]-2, path_bridge[i][1], 139)
		setIfEmpty(matrix, h_bridge+1, path_bridge[i][0]+2, path_bridge[i][1], 139)

def putLight(matrix, h, x, z): #build a light and a pillar under it
	matrix.setValue(h+1,x,z,(139,0))
	matrix.setValue(h+2,x,z,(139,0))
	matrix.setValue(h+3,x,z,(123,0))
	matrix.setEntity(h+4, x, z, (178,15), "daylight_detector")
	buildPillar(matrix, h, (x, z))

def cleanFundation(matrix, p, h, height_map): #clean the endpoints of the bridge
	for neighbor_position in [(0, -1), (0, 1), (-1, 0), (1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
		position_to_clean = (p[0] + neighbor_position[0], p[1] + neighbor_position[1])
		matrix.setValue(h, position_to_clean[0], position_to_clean[1], (1,6))
		fillUnder(matrix, h, position_to_clean[0], position_to_clean[1])
		cleanAbove(matrix, h, position_to_clean[0], position_to_clean[1])
		height_map[position_to_clean[0]][position_to_clean[1]] = h