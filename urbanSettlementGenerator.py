from pymclevel import alphaMaterials, BoundingBox
import utilityFunctions as utilityFunctions
import random
import math
import os
import RNG
import logging
from SpacePartitioning import binarySpacePartitioning, quadtreeSpacePartitioning
import GenerateHouse 
import GenerateBuilding
import GeneratePath
import GenerateBridge
import GenerateTower
from Earthworks import prepareLot
import TreeGestion

# change to INFO if you want a verbose log!
for handler in logging.root.handlers[:]:
   logging.root.removeHandler(handler)
logging.basicConfig(filename="log", level=logging.WARNING, filemode='w')

# remove INFO logs from pymclevel
#logging.getLogger("pymclevel").setLevel(logging.WARNING)

# Uncomment this to log to stdout as well!
#logging.getLogger().addHandler(logging.StreamHandler())

def perform(level, box, options):

	logging.info("BoundingBox coordinates: ({},{}),({},{}),({},{})".format(box.miny, box.maxy, box.minx, box.maxx, box.minz, box.maxz))

	# ==== PREPARATION =====
	(width, height, depth) = utilityFunctions.getBoxSize(box)
	logging.info("Selection box dimensions {}, {}, {}".format(width,height,depth))
	world = utilityFunctions.generateMatrix(level, box, width,depth,height)
	world_space = utilityFunctions.dotdict({"y_min": 0, "y_max": height-1, "x_min": 0, "x_max": width-1, "z_min": 0, "z_max": depth-1})
	simple_height_map = utilityFunctions.getSimpleHeightMap(level,box) #no height = -1 when water block
	list_trees = TreeGestion.prepareMap(world, simple_height_map) #get a list of all trees and erase them, so we can put some of them back after
	height_map = utilityFunctions.getHeightMap(level,box)
	# ==== PARTITIONING OF NEIGHBOURHOODS ==== 
	(center, neighbourhoods) = generateCenterAndNeighbourhood(world_space, height_map)
	all_buildings = []

	# ====  GENERATING CITY CENTER ==== 
	minimum_h = 50 
	minimum_w = 25
	mininum_d = 25

	iterate = 100
	minimum_lots = 6
	available_lots = 0
	maximum_tries = 50
	current_try = 0
	threshold = 1
	partitioning_list = []
	temp_partitioning_list = []

	# run the partitioning algorithm for iterate times to get different partitionings of the same area
	logging.info("Generating {} different partitionings for the the City Centre {}".format(iterate, center))
	while available_lots < minimum_lots and current_try < maximum_tries:

		for i in range(iterate):

			# generate a partitioning through some algorithm
			if RNG.random() < 0.5:
				partitioning = binarySpacePartitioning(center[0], center[1], center[2], center[3], center[4], center[5], [])
			else:
				partitioning = quadtreeSpacePartitioning(center[0], center[1], center[2], center[3], center[4], center[5], [])

			# remove invalid partitions from the partitioning
			valid_partitioning = []
			for p in partitioning:
				(y_min, y_max, x_min, x_max, z_min, z_max) = (p[0], p[1], p[2],p[3], p[4], p[5])
				failed_conditions = []
				cond1 = utilityFunctions.hasValidGroundBlocks(x_min, x_max,z_min,z_max, height_map)
				if cond1 == False: failed_conditions.append(1) 
				cond2 = utilityFunctions.hasMinimumSize(y_min, y_max, x_min, x_max,z_min,z_max, minimum_h, minimum_w, mininum_d)
				if cond2 == False: failed_conditions.append(2) 
				cond3 = utilityFunctions.hasAcceptableSteepness(x_min, x_max, z_min, z_max, height_map, threshold)
				if cond3 == False: failed_conditions.append(3) 
				if cond1 and cond2 and cond3:
					score = utilityFunctions.getScoreArea_type4(height_map, x_min, x_max, z_min, z_max)
					valid_partitioning.append((score, p))
				else:
					logging.info("Failed Conditions {}".format(failed_conditions))

			partitioning_list.extend(valid_partitioning)
			logging.info("Generated a partition with {} valid lots and {} invalids ones".format(len(valid_partitioning), len(partitioning)-len(valid_partitioning)))

		# order partitions by steepness
		partitioning_list = sorted(partitioning_list)
		final_partitioning = utilityFunctions.getNonIntersectingPartitions(partitioning_list)

		available_lots = len(final_partitioning)
		logging.info("Current partitioning with most available_lots: {}, current threshold {}".format(available_lots, threshold))

		threshold += 1
		current_try += 1
	
	logging.info("Final lots ({}) for the City Centre {}: ".format(len(final_partitioning), center))
	for p in final_partitioning:
		logging.info("\t{}".format(p))

	for partition in final_partitioning:
		building = generateBuilding(world, partition, height_map, simple_height_map)
		all_buildings.append(building)

	# ==== GENERATING NEIGHBOURHOODS ==== 
	
	minimum_h = 10 
	minimum_w = 16
	mininum_d = 16

	iterate = 100
	maximum_tries = 50
	current_try = 0
	minimum_lots = 20
	available_lots = 0
	threshold = 1
	partitioning_list = []
	final_partitioning = []
	
	while available_lots < minimum_lots and current_try < maximum_tries:
		partitioning_list = []
		for i in range(iterate):
			for neigh in neighbourhoods:
				logging.info("Generating {} different partitionings for the neighbourhood {}".format(iterate, neigh))
				
				if RNG.random() < 0.5:
					partitioning = binarySpacePartitioning(neigh[0], neigh[1], neigh[2], neigh[3], neigh[4], neigh[5], [])
				else:
					partitioning = quadtreeSpacePartitioning(neigh[0], neigh[1], neigh[2], neigh[3], neigh[4], neigh[5], [])

				valid_partitioning = []
				for p in partitioning:
					(y_min, y_max, x_min, x_max, z_min, z_max) = (p[0], p[1], p[2], p[3], p[4], p[5])
					failed_conditions = [] 
					cond1 = utilityFunctions.hasValidGroundBlocks(x_min, x_max,z_min,z_max, height_map)
					if cond1 == False: failed_conditions.append(1) 
					cond2 = utilityFunctions.hasMinimumSize(y_min, y_max, x_min, x_max,z_min,z_max, minimum_h, minimum_w, mininum_d)
					if cond2 == False: failed_conditions.append(2) 
					cond3 = utilityFunctions.hasAcceptableSteepness(x_min, x_max, z_min, z_max, height_map, threshold)
					if cond3 == False: failed_conditions.append(3) 
					if cond1 and cond2 and cond3:
						score = utilityFunctions.getScoreArea_type4(height_map, x_min, x_max, z_min, z_max)
						valid_partitioning.append((score, p))
						logging.info("Passed the 3 conditions!")
					else:
						logging.info("Failed Conditions {}".format(failed_conditions))

				partitioning_list.extend(valid_partitioning)
				logging.info("Generated a partition with {} valid lots and {} invalids ones".format(len(valid_partitioning), len(partitioning)-len(valid_partitioning)))
	
		temp_partitioning_list.extend(partitioning_list)
		# order partitions by steepness
		temp_partitioning_list = sorted(temp_partitioning_list)
		final_partitioning = utilityFunctions.getNonIntersectingPartitions(temp_partitioning_list)

		available_lots = len(final_partitioning)
		logging.info("Current neighbourhood partitioning with most available_lots: {}, current threshold {}".format(available_lots, threshold))

		threshold += 1
		current_try += 1

		logging.info("Final lots ({})for the neighbourhood {}: ".format(len(final_partitioning), neigh))
		for p in final_partitioning:
			logging.info("\t{}".format(p))

	for i in xrange(0, int(len(final_partitioning)*0.75)+1):
		house = generateHouse(world, final_partitioning[i], height_map, simple_height_map)
		all_buildings.append(house)

	for i in xrange(int(len(final_partitioning)*0.75)+1, len(final_partitioning)):
		tower = generateTower(world, final_partitioning[i], height_map, simple_height_map)
		all_buildings.append(tower)

	# ==== GENERATE PATH MAP  ==== 
 	# generate a path map that gives the cost of moving to each neighbouring cell
	pathMap = utilityFunctions.getPathMap(height_map, width, depth)
	simple_pathMap = utilityFunctions.getPathMap(simple_height_map, width, depth) #not affected by water

	# ==== CONNECTING BUILDINGS WITH ROADS  ==== 
	logging.info("Calling MST on {} buildings".format(len(all_buildings)))
	MST = utilityFunctions.getMST_Manhattan(all_buildings)
	
	pavementBlockID = 1
	pavementBlockSubtype = 6
	for m in MST:
		p1 = m[1]
		p2 = m[2]

	 	simple_path = utilityFunctions.simpleAStar(p1.entranceLot, p2.entranceLot, simple_pathMap, simple_height_map) #water and height are not important
	 	list_end_points = utilityFunctions.findBridgeEndPoints(world, simple_path, simple_height_map)

	 	if len(list_end_points)%2 == 0:
	 		for i in xrange(0,len(list_end_points),2):
	 			logging.info("Found water between {} and {}. Generating bridge...".format(list_end_points[i], list_end_points[i+1]))
	 			GenerateBridge.generateBridge(world, simple_height_map, list_end_points[i], list_end_points[i+1])

	 		list_end_points.insert(0, p1.entranceLot)
	 		list_end_points.append(p2.entranceLot)
	 		for i in xrange(0,len(list_end_points),2):
	 			path = utilityFunctions.aStar(list_end_points[i], list_end_points[i+1], pathMap, height_map)
	 			logging.info("Found path between {} and {}. Generating road...".format(list_end_points[i], list_end_points[i+1]))
	 			GeneratePath.generatePath(world, path, height_map, (pavementBlockID, pavementBlockSubtype))
	 	else:
	 		path = utilityFunctions.aStar(p1.entranceLot, p2.entranceLot, pathMap, height_map)
	 		logging.info("Found path between {} and {}. Generating road...".format(p1.entranceLot, p2.entranceLot))
			GeneratePath.generatePath(world, path, height_map, (pavementBlockID, pavementBlockSubtype))

	# ==== PUT BACK UNTOUCHED TREES ====
	TreeGestion.putBackTrees(world, height_map, list_trees)
	# ==== UPDATE WORLD ====
	world.updateWorld()

def generateCenterAndNeighbourhood(space, height_map):
	neighbourhoods = []
	logging.info("Generating Neighbourhood Partitioning...")
	center = utilityFunctions.getSubsection(space.y_min, space.y_max, space.x_min, space.x_max, space.z_min, space.z_max, 0.6)
	logging.info("Generated city center: {}".format(center))
	partitions = utilityFunctions.subtractPartition((space.y_min, space.y_max, space.x_min, space.x_max, space.z_min, space.z_max), center)
	for p in partitions:
		neighbourhoods.append(p)
		logging.info("Generated neighbourhood: {}".format(p))
	return (center, neighbourhoods)

def generateBuilding(matrix, p, height_map, simple_height_map):

	h = prepareLot(matrix, p, height_map)
	building = GenerateBuilding.generateBuilding(matrix, h, p[1],p[2],p[3], p[4], p[5])
	utilityFunctions.updateHeightMap(height_map, p[2]+1, p[3]-2, p[4]+1, p[5]-2, -1)
	utilityFunctions.updateHeightMap(simple_height_map, p[2]+1, p[3]-2, p[4]+1, p[5]-2, -1)
	return building

def generateHouse(matrix, p, height_map, simple_height_map):
	logging.info("Generating a house in lot {}".format(p))
	logging.info("Terrain before flattening: ")
	for x in range (p[2], p[3]):
		line = ""
		for z in range(p[4], p[5]):
			line += str(height_map[x][z])+" "
		logging.info(line)
				
	h = prepareLot(matrix, p, height_map)

	logging.info("Terrain after flattening: ")
	for x in range (p[2], p[3]):
		line = ""
		for z in range(p[4], p[5]):
			line += str(height_map[x][z])+" "
		logging.info(line)

	house = GenerateHouse.generateHouse(matrix, h, p[1],p[2],p[3], p[4], p[5])
	
	utilityFunctions.updateHeightMap(height_map, p[2]+1, p[3]-1, p[4]+1, p[5]-1, -1)
	utilityFunctions.updateHeightMap(simple_height_map, p[2]+1, p[3]-1, p[4]+1, p[5]-1, -1)

	logging.info("Terrain after construction: ")
	for x in range (p[2], p[3]):
		line = ""
		for z in range(p[4], p[5]):
			line += str(height_map[x][z])+" "
		logging.info(line)

	return house

def generateTower(matrix, p, height_map, simple_height_map):

	tower = GenerateTower.generateTower(matrix, p[2], p[3], p[4], p[5], height_map)
	utilityFunctions.updateHeightMap(height_map, tower.buildArea.x_min, tower.buildArea.x_max, tower.buildArea.z_min, tower.buildArea.z_max, -1)
	utilityFunctions.updateHeightMap(simple_height_map, tower.buildArea.x_min, tower.buildArea.x_max, tower.buildArea.z_min, tower.buildArea.z_max, -1)

	return tower