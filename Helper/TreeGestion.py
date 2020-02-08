import logging
import utilityFunctions as utilityFunctions

air_like = [0, 6, 17, 18, 30, 31, 32, 37, 38, 39, 40, 59, 81, 83, 85, 104, 105, 106, 107, 111, 141, 142, 161, 162, 175, 78, 79, 99]
water_like = [8, 9, 10, 11]
trunk_like = [17]
leaf_like = [18]

def prepareMap(matrix, height_map):
	logging.info("Finding all the trees on the map")
	list_trees = []
	for x in range(0, len(height_map)):
		for z in range(0, len(height_map[0])):
				if matrix.getValue(height_map[x][z]+1, x, z) in trunk_like: #find all positions of the trunk of the trees that are on the map
					logging.info("Tree found in {}".format((x, z)))
					list_trees.append((findFullTree(matrix, height_map, height_map[x][z], x, z), (height_map[x][z]+1, x, z))) #save the positions of all the blocks of the threes in a list
				elif matrix.getValue(height_map[x][z]+1, x, z) == 162: #check if it's an acacia tree
					logging.info("Acacia tree found in {}".format((x, z)))
					list_trees.append((findFullAcacia(matrix, height_map, height_map[x][z], x, z), (height_map[x][z]+1, x, z)))

	logging.info("Erasing all the trees")
	eraseAllTrees(list_trees, matrix) #erase all the trees
	return list_trees #return the list so we know where the trees were placed

def findFullTree(matrix, height_map, h, xt, zt):
	tree_block = []
	height_tree = 1
	while matrix.getValue(h+height_tree, xt, zt) in trunk_like: #find all the leaves that are around the trunk level by level
		distance = 1
		visited = []
		block_to_expand_queue = [(xt, zt)]
		new_block_queue = []
		tree_block.append((h+height_tree, xt, zt, utilityFunctions.getBlockFullValue(matrix, h+height_tree, xt, zt)))
		if height_tree < 12:
			while distance <= 3: #go through the level and find the leaves without going too far
				while len(block_to_expand_queue) != 0:
					actual_block = block_to_expand_queue.pop()
					addSameLevelTreeBlockToQueue(matrix, h+height_tree, new_block_queue, visited, tree_block, actual_block, (xt, zt))
				block_to_expand_queue = new_block_queue
				new_block_queue = []
				distance += 1
		else:
			while distance <= 6: #expand the max distance when we reach high level, for trees like jungle trees
				while len(block_to_expand_queue) != 0:
					actual_block = block_to_expand_queue.pop()
					addSameLevelTreeBlockToQueue(matrix, h+height_tree, new_block_queue, visited, tree_block, actual_block, (xt, zt))
				block_to_expand_queue = new_block_queue
				new_block_queue = []
				distance += 1
		height_tree += 1
	#do the same once again for one level above the last block of trunk, since there can be leaves up there
	distance = 1
	visited = []
	block_to_expand_queue = [(xt, zt)]
	new_block_queue = []
	tree_block.append((h+height_tree, xt, zt, utilityFunctions.getBlockFullValue(matrix, h+height_tree, xt, zt)))
	while distance <= 2:
		while len(block_to_expand_queue) != 0:
			actual_block = block_to_expand_queue.pop()
			addSameLevelTreeBlockToQueue(matrix, h+height_tree, new_block_queue, visited, tree_block, actual_block, (xt, zt))
		block_to_expand_queue = new_block_queue
		new_block_queue = []
		distance +=1
	height_tree += 1

	return tree_block

def addSameLevelTreeBlockToQueue(matrix, h, new_block_queue, visited, tree_block, actual_block, (xt, zt)):
	for neighbor_position in [(1, 0),(-1, 0),(0, 1),(0, -1)]:
		neighbor_block = (actual_block[0] + neighbor_position[0], actual_block[1] + neighbor_position[1])
		try:
			if neighbor_block not in visited and matrix.getValue(h, neighbor_block[0], neighbor_block[1]) in leaf_like+[78] and abs(xt-neighbor_block[0])<=2 and abs(zt-neighbor_block[1])<=2:
				tree_block.append((h, neighbor_block[0], neighbor_block[1], utilityFunctions.getBlockFullValue(matrix, h, neighbor_block[0], neighbor_block[1])))
				new_block_queue.append(neighbor_block)
			elif neighbor_block not in visited and matrix.getValue(h, neighbor_block[0], neighbor_block[1]) in trunk_like and abs(xt-neighbor_block[0])<=1 and abs(zt-neighbor_block[1])<=1:
				tree_block.append((h, neighbor_block[0], neighbor_block[1], utilityFunctions.getBlockFullValue(matrix, h, neighbor_block[0], neighbor_block[1])))
				new_block_queue.append(neighbor_block)
		except:
			continue
		visited.append(neighbor_block)

def putBackTrees(matrix, height_map, list_trees): #go through the list saved and see if all the blocks of a tree are valid, if so we put the tree back using the id we saved for each block
	for tree, origin in list_trees:
		if checkIfGroundValid(matrix, height_map, tree) == True and checkIfTreeUntouched(matrix, tree) == True: #check validity of a tree saved
			for h, x, z, i in tree:
				matrix.setValue(h, x, z, i)

def checkIfTreeUntouched(matrix, tree): #check that nothing was built on the position of the tree's blocks
	for h, x, z, i in tree:
		if utilityFunctions.getBlockFullValue(matrix, h, x, z) != (0,0):
			return False
	return True

def checkIfGroundValid(matrix, height_map, tree): #check that the tree is not above a path, a rail, or in a building lot
	min_x = 255
	max_x = 0
	min_z = 255
	max_z = 0
	for h, x, z, i in tree:
		if x > max_x:
			max_x = x
		if x < min_x:
			min_x = x
		if z > max_z:
			max_z = z
		if z < min_z:
			min_z = z

	for x in range(min_x, max_x+1):
		for z in range(min_z, max_z+1):
			try:
				(b, d) = utilityFunctions.getBlockFullValue(matrix, height_map[x][z], x, z)
				if height_map[x][z] == -1 or (b, d) == (1,6) or b in [27, 28, 66, 157, 17, 208]:
					return False
			except:
				continue
	return True

def eraseAllTrees(list_trees, matrix): #use a BFS approach to erase all the tree by using their origins as starting nodes
	block_q = []
	for tree, origin in list_trees:
		block_q.append(origin)
		while len(block_q) != 0:
			actual_block = block_q.pop()
			block_q = addNeighborTreeBlockToQueue(matrix, block_q, actual_block)
			matrix.setValue(actual_block[0], actual_block[1], actual_block[2], (0,0))

def addNeighborTreeBlockToQueue(matrix, block_q, actual_block): #get all the neighbor blocks that are part of the tree
	for neighbor_position in [(1, 0, 0),(-1, 0, 0),(0, 1, 0),(0, -1, 0),(0, 0, 1),(0, 0, -1)]:
		neighbor_block = (actual_block[0] + neighbor_position[0], actual_block[1] + neighbor_position[1], actual_block[2] + neighbor_position[2])
		try:
			if matrix.getValue(neighbor_block[0], neighbor_block[1], neighbor_block[2]) in leaf_like+trunk_like+[106, 99, 100, 78]:
				block_q.append(neighbor_block)
		except:
			continue
	return block_q

def findFullAcacia(matrix, height_map, h, xt, zt):
	tree_block = []
	height_tree = 1
	while matrix.getValue(h+height_tree, xt, zt) in trunk_like: #find all the leaves that are around the trunk level by level
		distance = 1
		visited = []
		block_to_expand_queue = [(h+height_tree, xt, zt)]
		new_block_queue = []
		tree_block.append((h+height_tree, xt, zt, utilityFunctions.getBlockFullValue(matrix, h+height_tree, xt, zt)))
		while distance <= 5: #go through the level and find the leaves without going too far
			while len(block_to_expand_queue) != 0:
				actual_block = block_to_expand_queue.pop()
				addSameLevelAcaciaBlockToQueue(matrix, h+height_tree, new_block_queue, visited, tree_block, actual_block, (xt, zt))
			block_to_expand_queue = new_block_queue
			new_block_queue = []
			distance += 1
		height_tree += 1
	#do the same once again for one level above the last block of trunk, since there can be leaves up there
	distance = 1
	visited = []
	block_to_expand_queue = [(h+height_tree, xt, zt)]
	new_block_queue = []
	tree_block.append((h+height_tree, xt, zt, utilityFunctions.getBlockFullValue(matrix, h+height_tree, xt, zt)))
	while distance <= 5:
		while len(block_to_expand_queue) != 0:
			actual_block = block_to_expand_queue.pop()
			addSameLevelAcaciaBlockToQueue(matrix, h+height_tree, new_block_queue, visited, tree_block, actual_block, (xt, zt))
		block_to_expand_queue = new_block_queue
		new_block_queue = []
		distance +=1
	height_tree += 1

	return tree_block

def addSameLevelAcaciaBlockToQueue(matrix, h, new_block_queue, visited, tree_block, actual_block, (xt, zt)):
	for neighbor_position in [(0, 1, 0),(0, -1, 0),(0, 0, 1),(0, 0, -1), (1, 1, 0),(1, -1, 0),(1, 0, 1),(1, 0, -1), (-1, 1, 0),(-1, -1, 0),(-1, 0, 1),(-1, 0, -1)]:
		neighbor_block = (actual_block[0] + neighbor_position[0], actual_block[1] + neighbor_position[1], actual_block[2] + neighbor_position[2])
		try:
			if neighbor_block not in visited and matrix.getValue(neighbor_block[0], neighbor_block[1], neighbor_block[2]) == 161 and abs(xt-neighbor_block[1])<=4 and abs(zt-neighbor_block[2])<=4:
				tree_block.append((neighbor_block[0], neighbor_block[1], neighbor_block[2], utilityFunctions.getBlockFullValue(matrix, neighbor_block[0], neighbor_block[1], neighbor_block[2])))
				new_block_queue.append(neighbor_block)
			elif neighbor_block not in visited and matrix.getValue(neighbor_block[0], neighbor_block[1], neighbor_block[2]) == 162 and abs(xt-neighbor_block[1])<=1 and abs(zt-neighbor_block[2])<=1:
				tree_block.append((neighbor_block[0], neighbor_block[1], neighbor_block[2], utilityFunctions.getBlockFullValue(matrix, neighbor_block[0], neighbor_block[1], neighbor_block[2])))
				new_block_queue.append(neighbor_block)
		except:
			continue
		visited.append(neighbor_block)
