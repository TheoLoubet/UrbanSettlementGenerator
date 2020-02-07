import random
import RNG
import logging
import utilityFunctions as utilityFunctions

AIR_ID = (0, 0)
FENCE_ID = (85, 0)
OAK_WOOD_ID = (17, 0)
FARMLAND_ID = (60, 0)
WATER_ID = (9, 0)
TORCH_ID = (50, 5)
WHEAT_ID = (59, 0)
CARROT_ID = (141, 0)
POTATO_ID = (142, 0)
GRASS_PATH_ID = (208, 0)
OAK_FENCE_GATE_ID = 107
plants = [WHEAT_ID, CARROT_ID, POTATO_ID]
PLANT_SPECIES_NUMBER = 3

def generateFarm(matrix, h_min, h_max, x_min, x_max, z_min, z_max, farmType):

	farm = utilityFunctions.dotdict()
	farm.type = "farm"
	farm.lotArea = utilityFunctions.dotdict({"y_min": h_min, "y_max": h_max, "x_min": x_min, "x_max": x_max, "z_min": z_min, "z_max": z_max})

	utilityFunctions.cleanProperty(matrix, h_min + 1, h_max, x_min, x_max, z_min, z_max)

	(h_min, h_max, x_min, x_max, z_min, z_max) = getFarmAreaInsideLot(h_min, h_max, x_min, x_max, z_min, z_max, farmType)
	farm.buildArea = utilityFunctions.dotdict({"y_min": h_min, "y_max": h_max, "x_min": x_min, "x_max": x_max, "z_min": z_min, "z_max": z_max})

	logging.info("Generating farm at area {}".format(farm.lotArea))
	logging.info("Construction area {}".format(farm.buildArea))

	farm.orientation = getOrientation(matrix, farm.lotArea)

	if farmType == None:
		generateBasicPattern(matrix, h_min, x_min, x_max, z_min, z_max)
	elif farmType == "smiley":
		generateSmileyPattern(matrix, h_min, x_min, x_max, z_min, z_max)

	#create door and entrance path
	if farm.orientation == "S":
		door_x = x_max - 2
		door_z = z_max - 1
		farm.entranceLot = (door_x, farm.lotArea.z_max)
		generateEntrance(matrix, 0, h_min, door_x, door_z, door_z + 1, farm.lotArea.z_max + 1)

	elif farm.orientation == "N":
		door_x = x_min + 2
		door_z = z_min + 1
		farm.entranceLot = (door_x, farm.lotArea.z_min)
		generateEntrance(matrix, 2, h_min, door_x, door_z, farm.lotArea.z_min, door_z)

	elif farm.orientation == "W":
		door_x = x_min + 1
		door_z = z_max - 2
		farm.entranceLot = (farm.lotArea.x_min, door_z)
		generateEntrance(matrix, 1, h_min, door_x, door_z, farm.lotArea.x_min, door_x)

	elif farm.orientation == "E":
		door_x = x_max - 1
		door_z = z_min + 2
		farm.entranceLot = (farm.lotArea.x_max, door_z)
		generateEntrance(matrix, 3, h_min, door_x, door_z, door_x + 1, farm.lotArea.x_max + 1)

	return farm

def generateEntrance(matrix, orientation, h_min, door_x, door_z, min_bound, max_bound):
	if orientation % 2 == 0:
		for z in range(min_bound, max_bound):
			matrix.setValue(h_min, door_x, z, GRASS_PATH_ID)
			matrix.setValue(h_min, door_x - 1, z, GRASS_PATH_ID)
			matrix.setValue(h_min, door_x + 1, z, GRASS_PATH_ID)
	else:
		for x in range(min_bound, max_bound):
			matrix.setValue(h_min, x, door_z, GRASS_PATH_ID)
			matrix.setValue(h_min, x, door_z - 1, GRASS_PATH_ID)
			matrix.setValue(h_min, x, door_z + 1, GRASS_PATH_ID)
	matrix.setValue(h_min + 1, door_x, door_z, (OAK_FENCE_GATE_ID, orientation))

def getFarmAreaInsideLot(h_min, h_max, x_min, x_max, z_min, z_max, farmType):
	farm_size_x = farm_size_z = 0
	if farmType == None:
		farm_size_x = RNG.randint(11, 16)
		farm_size_z = RNG.randint(11, 16)
	elif farmType == "smiley":
		farm_size_x = farm_size_z = 16

	if x_max-x_min > farm_size_x:
		x_mid = x_min + (x_max - x_min) / 2
		x_min = x_mid - farm_size_x / 2
		x_max = x_mid + farm_size_x / 2

	if z_max-z_min > farm_size_z:
		z_mid = z_min + (z_max - z_min) / 2
		z_min = z_mid - farm_size_z / 2
		z_max = z_mid + farm_size_z / 2

	farm_size_h = (farm_size_x + farm_size_z) / 2
	if h_max - h_min > 19 or h_max - h_min > farm_size_h:
		h_max = h_min + ((farm_size_x + farm_size_z) / 2)

	return (h_min, h_max, x_min, x_max, z_min, z_max)

def generateBasicPattern(matrix, h, x_min, x_max, z_min, z_max):

	## FENCES
	generateFences(matrix, h, x_min + 1, x_max - 1, z_min + 1, z_max - 1)

	## GROUND & CULTURES
	# select one random plant for this farm
	plant = plants[RNG.randint(0, PLANT_SPECIES_NUMBER - 1)]
	# fill field with dirt and the corresponding plant
	for x in range(x_min + 3, x_max - 2):
		for z in range(z_min + 3, z_max - 2):
			matrix.setValue(h, x, z, FARMLAND_ID)
			matrix.setValue(h + 1, x, z, plant)

	## WATER
	for x in range(x_min + 2, x_max - 1):
		matrix.setValue(h, x, z_max - 2, WATER_ID)
		matrix.setValue(h, x, z_min + 2, WATER_ID)
	for z in range(z_min + 2, z_max - 1):
		matrix.setValue(h, x_max - 2, z, WATER_ID)
		matrix.setValue(h, x_min + 2, z, WATER_ID)

def generateSmileyPattern(matrix, h, x_min, x_max, z_min, z_max):

	## FENCES
	generateFences(matrix, h, x_min + 1, x_max - 1, z_min + 1, z_max - 1)

	## GROUND
	# fill field with dirt and carrots
	for x in range(x_min + 3, x_max - 2):
		for z in range(z_min + 3, z_max - 2):
			matrix.setValue(h, x, z, FARMLAND_ID)
			matrix.setValue(h + 1, x, z, CARROT_ID)

	## SMILEY
	# eyes
	def generateEye(x, z):
		matrix.setValue(h + 1, x, z, WHEAT_ID)
		matrix.setValue(h + 1, x, z + 1, WHEAT_ID)
		matrix.setValue(h + 1, x + 1, z, WHEAT_ID)
		matrix.setValue(h, x + 1, z + 1, WATER_ID)
		matrix.setValue(h + 1, x + 1, z + 1, AIR_ID)
	# left eye
	generateEye(x_min + 5, z_min + 5)
	# right eye
	generateEye(x_max - 6, z_min + 5)
	# mouth
	for x in range(x_min + 6, x_max - 5):
		matrix.setValue(h + 1, x, z_max - 4, WHEAT_ID)
	matrix.setValue(h + 1, x_min + 5, z_max - 5, WHEAT_ID)
	matrix.setValue(h + 1, x_max - 5, z_max - 5, WHEAT_ID)
	matrix.setValue(h + 1, x_min + 4, z_max - 6, WHEAT_ID)
	matrix.setValue(h + 1, x_max - 4, z_max - 6, WHEAT_ID)

	## WATER
	for x in range(x_min + 2, x_max - 1):
		matrix.setValue(h, x, z_max - 2, WATER_ID)
		matrix.setValue(h, x, z_min + 2, WATER_ID)
	for z in range(z_min + 2, z_max - 1):
		matrix.setValue(h, x_max - 2, z, WATER_ID)
		matrix.setValue(h, x_min + 2, z, WATER_ID)


def generateFences(matrix, h, x_min, x_max, z_min, z_max):
	for x in range(x_min, x_max + 1):
		matrix.setValue(h, x, z_max, OAK_WOOD_ID)
		matrix.setValue(h, x, z_min, OAK_WOOD_ID)
		matrix.setValue(h + 1, x, z_max, FENCE_ID)
		matrix.setValue(h + 1, x, z_min, FENCE_ID)
	for z in range(z_min, z_max + 1):
		matrix.setValue(h, x_max, z, OAK_WOOD_ID)
		matrix.setValue(h, x_min, z, OAK_WOOD_ID)
		matrix.setValue(h + 1, x_max, z, FENCE_ID)
		matrix.setValue(h + 1, x_min, z, FENCE_ID)
	matrix.setValue(h + 2, x_min, z_max, TORCH_ID)
	matrix.setValue(h + 2, x_min, z_min, TORCH_ID)
	matrix.setValue(h + 2, x_max, z_max, TORCH_ID)
	matrix.setValue(h + 2, x_max, z_min, TORCH_ID)

def getOrientation(matrix, area):
	x_mid = matrix.width/2
	z_mid = matrix.depth/2

	bx_mid = area.x_min + (area.x_max-area.x_min)/2
	bz_mid = area.z_min + (area.z_max-area.z_min)/2

	if bx_mid <= x_mid:
		if bz_mid <= z_mid:
			#SOUTH, EAST
			return RNG.choice(["S", "E"])
		elif bz_mid > z_mid:
			# SOUTH, WEST
			return RNG.choice(["N", "E"])

	elif bx_mid > x_mid:
		if bz_mid <= z_mid:
			# return NORTH, EAST
			return RNG.choice(["S", "W"])
		elif bz_mid > z_mid:
			# return NORTH, WEST
			return RNG.choice(["N", "W"])
	return None
