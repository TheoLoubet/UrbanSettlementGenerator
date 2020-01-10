import logging
import utilityFunctions as utilityFunctions
import numpy as np

air_like = [0, 6, 17, 18, 30, 31, 32, 37, 38, 39, 40, 59, 81, 83, 85, 104, 105, 106, 107, 111, 141, 142, 161, 162, 175, 78, 79, 99]
water_like = [8, 9, 10, 11]
wood_like = [17, 162]
leaf_like = [18, 161]

def prepareMap(matrix, height_map):
	minHeightMap = np.min(height_map)
	maxHeightMap = np.max(height_map)
	print("minh : {}; maxh : {}".format(minHeightMap, maxHeightMap))
	list_trees = []
	for x in range(0, len(height_map)):
		for z in range(0, len(height_map[0])):
				if matrix.getValue(height_map[x][z]+1, x, z) in wood_like:
					list_trees.append(findFullTree(matrix, height_map, height_map[x][z]+1, x, z))
	
	eraseAllTrees(matrix, minHeightMap, maxHeightMap+34, len(height_map), len(height_map[0]))
	return list_trees

def findFullTree(matrix, height_map, h, xt, zt):
	tree_block = []
	while matrix.getValue(h, xt, zt) in wood_like:
		for x in range(xt-2, xt+3):
			for z in range(zt-2, zt+3):
				try:
					if matrix.getValue(h, x, z) in wood_like+leaf_like:
						tree_block.append((h, x, z, utilityFunctions.getBlockFullValue(matrix, h, x, z)))
				except:
					continue
		h += 1
	for x in range(xt-2, xt+3):
		for z in range(zt-2, zt+3):
			try:
				if matrix.getValue(h, x, z) in wood_like+leaf_like:
					tree_block.append((h, x, z, utilityFunctions.getBlockFullValue(matrix, h, x, z)))
			except:
				continue
	return tree_block

def eraseAllTrees(matrix, minh, maxh, xsize, zsize):
	for x in range(0, xsize):
		for z in range(0, zsize):
			for h in range(minh, maxh):
				if matrix.getValue(h, x, z) in wood_like+leaf_like+[106]:
					matrix.setValue(h, x, z, (0, 0))

def putBackTrees(matrix, list_trees):
	for tree in list_trees:
		if checkIfTreeUntouched(matrix, tree) == True:
			for h, x, z, i in tree:
				matrix.setValue(h, x, z, i)

def checkIfTreeUntouched(matrix, tree):
	for h, x, z, i in tree:
		if utilityFunctions.getBlockFullValue(matrix, h, x, z) != (0,0):
			return False
	return True