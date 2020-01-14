import logging
import utilityFunctions as utilityFunctions

air_like = [0, 6, 17, 18, 30, 31, 32, 37, 38, 39, 40, 59, 81, 83, 85, 104, 105, 106, 107, 111, 141, 142, 161, 162, 175, 78, 79, 99]
water_like = [8, 9, 10, 11]
wood_like = [17, 162]
leaf_like = [18, 161]

def prepareMap(matrix, height_map):
	list_trees = []
	for x in range(0, len(height_map)):
		for z in range(0, len(height_map[0])):
				if matrix.getValue(height_map[x][z]+1, x, z) in wood_like:
					list_trees.append((findFullTree(matrix, height_map, height_map[x][z]+1, x, z), (height_map[x][z]+1, x, z)))
	
	eraseAllTrees(list_trees, matrix)
	return list_trees

def findFullTree(matrix, height_map, h, xt, zt):
	tree_block = []
	while matrix.getValue(h, xt, zt) in wood_like:
		tree_block.append((h, xt, zt, utilityFunctions.getBlockFullValue(matrix, h, xt, zt)))
		for x in range(xt-2, xt+3):
			for z in range(zt-2, zt+3):
				try:
					if matrix.getValue(h, x, z) in leaf_like:
						tree_block.append((h, x, z, utilityFunctions.getBlockFullValue(matrix, h, x, z)))
				except:
					continue
		h += 1
	tree_block.append((h, xt, zt, utilityFunctions.getBlockFullValue(matrix, h, xt, zt)))
	for x in range(xt-2, xt+3):
		for z in range(zt-2, zt+3):
			try:
				if matrix.getValue(h, x, z) in leaf_like:
					tree_block.append((h, x, z, utilityFunctions.getBlockFullValue(matrix, h, x, z)))
			except:
				continue
	return tree_block

def putBackTrees(matrix, height_map, list_trees):
	for tree, origin in list_trees:
		if checkIfGroundValid(matrix, height_map, origin) == True and checkIfTreeUntouched(matrix, tree) == True:
			for h, x, z, i in tree:
				matrix.setValue(h, x, z, i)

def checkIfTreeUntouched(matrix, tree):
	for h, x, z, i in tree:
		if utilityFunctions.getBlockFullValue(matrix, h, x, z) != (0,0):
			return False
	return True

def checkIfGroundValid(matrix, height_map, origin):
	(b, d) = utilityFunctions.getBlockFullValue(matrix, origin[0]-1, origin[1], origin[2])
	if (b, d) == (0,0) or b == 65:
		return False
	else:
		for x in range(origin[1]-2, origin[1]+3):
			for z in range(origin[2]-2, origin[2]+3):
				try:
					if height_map[x][z] == -1 or utilityFunctions.getBlockFullValue(matrix, height_map[x][z], x, z) == (1,6):
						return False
				except:
					continue
	return True

def eraseAllTrees(list_trees, matrix):
	block_q = []
	for tree, origin in list_trees:
		block_q.append(origin)
		while len(block_q) != 0:
			actual_block = block_q[-1]
			block_q.pop()
			block_q = addNeighborTreeBlockToQueue(matrix, block_q, actual_block)
			matrix.setValue(actual_block[0], actual_block[1], actual_block[2], (0,0))

def addNeighborTreeBlockToQueue(matrix, block_q, actual_block):
	for neighbor_position in [(1, 0, 0),(-1, 0, 0),(0, 1, 0),(0, -1, 0),(0, 0, 1),(0, 0, -1)]:
		neighbor_block = (actual_block[0] + neighbor_position[0], actual_block[1] + neighbor_position[1], actual_block[2] + neighbor_position[2])
		try:
			if matrix.getValue(neighbor_block[0], neighbor_block[1], neighbor_block[2]) in leaf_like+wood_like+[106]:
				block_q.append(neighbor_block)
		except:
			continue
	return block_q