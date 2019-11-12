import logging
import utilityFunctions as utilityFunctions

def generateBridge(matrix, height_map, p1, p2):
	air_like = [0, 6, 17, 18, 30, 31, 32, 37, 38, 39, 40, 59, 81, 83, 85, 104, 105, 106, 107, 111, 141, 142, 161, 162, 175, 78, 79, 99]
	#fundation
	h1 = height_map[p1[0]][p1[1]]
	h2 = height_map[p2[0]][p2[1]]
	h_bridge = max(h1,h2)+1
	for i in range (min(h1,h2), h_bridge+1):
		if matrix.getValue(i, p1[0], p1[1]) in air_like:
			matrix.setValue(i, p1[0], p1[1], (1,6))
		if matrix.getValue(i, p2[0], p2[1]) in air_like:
			matrix.setValue(i, p2[0], p2[1], (1,6))


	middlepoint = (int((p1[0]+p2[0])/2),(int((p1[1]+p2[1])/2)))
	linkBlock(matrix, height_map, h_bridge, p1, middlepoint)
	linkBlock(matrix, height_map, h_bridge, p2, middlepoint)

def linkBlock(matrix, height_map, h_bridge, p1, p2):
	actual_point = p1
	while actual_point != p2:
		if actual_point[0] < p2[0]:
			actual_point = (actual_point[0] + 1, actual_point[1])
			matrix.setValue(h_bridge, actual_point[0], actual_point[1], (1,6))
		if actual_point[0] > p2[0]:
			actual_point = (actual_point[0] - 1, actual_point[1])
			matrix.setValue(h_bridge, actual_point[0], actual_point[1], (1,6))
		if actual_point[1] < p2[1]:
			actual_point = (actual_point[0], actual_point[1] + 1)
			matrix.setValue(h_bridge, actual_point[0], actual_point[1], (1,6))
		if actual_point[1] > p2[1]:
			actual_point = (actual_point[0], actual_point[1] - 1)
			matrix.setValue(h_bridge, actual_point[0], actual_point[1], (1,6))