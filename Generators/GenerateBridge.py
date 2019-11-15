import logging
import utilityFunctions as utilityFunctions
air_like = [0, 6, 17, 18, 30, 31, 32, 37, 38, 39, 40, 59, 81, 83, 85, 104, 105, 106, 107, 111, 141, 142, 161, 162, 175, 78, 79, 99]
water_like = [8, 9, 10, 11]

def generateBridge(matrix, height_map, p1, p2): #generate a bridge between p1 and p2
	#finding height
	h1 = height_map[p1[0]][p1[1]]
	h2 = height_map[p2[0]][p2[1]]
	h_bridge = max(h1,h2)+2

	#cleanFundation(matrix, p1)
	#cleanFundation(matrix, p2)

	#get the path for the 2 side of the bridge
	middlepoint = (int((p1[0]+p2[0])/2),(int((p1[1]+p2[1])/2)))
	path_bridge1 = []
	path_bridge1 = getPathBridge(matrix, height_map, h_bridge, p1, middlepoint, path_bridge1)
	path_bridge2 = []
	path_bridge2 = getPathBridge(matrix, height_map, h_bridge, p2, middlepoint, path_bridge2)

	#build the bridge
	buildBridge(matrix, path_bridge1, h_bridge, h1+1, middlepoint)
	buildBridge(matrix, path_bridge2, h_bridge, h2+1, None)
	buildPillar(matrix, h_bridge-1, middlepoint)

def getPathBridge(matrix, height_map, h_bridge, p1, p2, path_bridge): #find a path to link p1 to p2
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

def buildBridge(matrix, path_bridge, h_bridge, h_start, middlepoint):
	isDemi = True
	h_actual = h_start
	
	#star point of the bridge
	matrix.setValue(h_actual, path_bridge[0][0], path_bridge[0][1], (44,5))
	fillUnder(matrix, h_actual-1, path_bridge[0][0], path_bridge[0][1])
	#search the right way to extend bridge
	if path_bridge[0][0] != path_bridge[1][0]:
		setIfEmpty(matrix, h_actual, path_bridge[0][0], path_bridge[0][1]-1, (44,0))
		fillUnder(matrix, h_actual-1, path_bridge[0][0], path_bridge[0][1]-1)
		setIfEmpty(matrix, h_actual, path_bridge[0][0], path_bridge[0][1]+1, (44,0))
		fillUnder(matrix, h_actual-1, path_bridge[0][0], path_bridge[0][1]+1)
	elif path_bridge[0][1] != path_bridge[1][1]:
		setIfEmpty(matrix, h_actual, path_bridge[0][0]-1, path_bridge[0][1], (44,0))
		fillUnder(matrix, h_actual-1, path_bridge[0][0]-1, path_bridge[0][1])
		setIfEmpty(matrix, h_actual, path_bridge[0][0]+1, path_bridge[0][1], (44,0))
		fillUnder(matrix, h_actual-1, path_bridge[0][0]+1, path_bridge[0][1])
	matrix.setValue(h_actual, path_bridge[1][0], path_bridge[1][1], (43,5))
	fillUnder(matrix, h_actual-1, path_bridge[1][0], path_bridge[1][1])
	#search the right way to extend bridge
	if path_bridge[1][0] != path_bridge[2][0]:
		setIfEmpty(matrix, h_actual, path_bridge[1][0], path_bridge[1][1]-1, (43,0))
		fillUnder(matrix, h_actual-1, path_bridge[1][0], path_bridge[1][1]-1)
		setIfEmpty(matrix, h_actual, path_bridge[1][0], path_bridge[1][1]+1, (43,0))
		fillUnder(matrix, h_actual-1, path_bridge[1][0], path_bridge[1][1]+1)
	elif path_bridge[1][1] != path_bridge[2][1]:
		setIfEmpty(matrix, h_actual, path_bridge[1][0]-1, path_bridge[1][1], (43,0))
		fillUnder(matrix, h_actual-1, path_bridge[1][0]-1, path_bridge[1][1])
		setIfEmpty(matrix, h_actual, path_bridge[1][0]+1, path_bridge[1][1], (43,0))
		fillUnder(matrix, h_actual-1, path_bridge[1][0]+1, path_bridge[1][1])

	#main part of the bridge
	for i in range(2, len(path_bridge)-1):
		#the bridge height goes up
		if h_actual != h_bridge:
			if isDemi == True: #check if we need to put a full block or 2 slabs
				matrix.setValue(h_actual, path_bridge[i][0], path_bridge[i][1], (44,13))
				matrix.setValue(h_actual+1, path_bridge[i][0], path_bridge[i][1], (44,5))
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
				matrix.setValue(h_actual, path_bridge[i][0], path_bridge[i][1], (43,5))
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
			matrix.setValue(h_bridge, path_bridge[i][0], path_bridge[i][1], (43,5))
			#search the right way to extend bridge
			if path_bridge[i][0] != path_bridge[i+1][0]:
				setIfEmpty(matrix, h_bridge, path_bridge[i][0], path_bridge[i][1]-1, (43,0))
				setIfEmpty(matrix, h_bridge, path_bridge[i][0], path_bridge[i][1]+1, (43,0))
			elif path_bridge[i][1] != path_bridge[i+1][1]:
				setIfEmpty(matrix, h_bridge, path_bridge[i][0]-1, path_bridge[i][1], (43,0))
				setIfEmpty(matrix, h_bridge, path_bridge[i][0]+1, path_bridge[i][1], (43,0))

	#build cross in the middle
	if middlepoint != None:
		matrix.setValue(h_bridge, middlepoint[0], middlepoint[1], (43,5))
		matrix.setValue(h_bridge, middlepoint[0]+1, middlepoint[1], (43,5))
		matrix.setValue(h_bridge, middlepoint[0]-1, middlepoint[1], (43,5))
		matrix.setValue(h_bridge, middlepoint[0], middlepoint[1]+1, (43,5))
		matrix.setValue(h_bridge, middlepoint[0], middlepoint[1]-1, (43,5))

def fillUnder(matrix, h, x, z): #put path blocks under the position if there is air
	while matrix.getValue(h, x, z) in air_like:
		matrix.setValue(h, x, z, (1,6))
		h -= 1

def setIfEmpty(matrix, h, x, z, i): #put block only if the position given or the one under is not occupied by a slab
	if matrix.getValue(h, x, z) not in [44, 43] and matrix.getValue(h-1, x, z) not in [44, 43]:
		matrix.setValue(h, x, z, i)

def buildPillar(matrix, h, middlepoint): #build a pillar in the water to support the bridge
	while matrix.getValue(h, middlepoint[0], middlepoint[1]) in air_like:
		matrix.setValue(h, middlepoint[0], middlepoint[1], (139,0))
		h -= 1
	while matrix.getValue(h, middlepoint[0], middlepoint[1]) in water_like:
		matrix.setValue(h, middlepoint[0], middlepoint[1], (4,0))
		h -= 1

def cleanFundation(matrix, p): #clean the endpoints of the bridge

	return True