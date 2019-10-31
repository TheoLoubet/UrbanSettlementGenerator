import random
import math
import RNG
import logging
from pymclevel import alphaMaterials, BoundingBox
import utilityFunctions as utilityFunctions
from GenerateCarpet import generateCarpet
from GenerateObject import *

def generateHouse(matrix, h_min, h_max, x_min, x_max, z_min, z_max, ceiling = None):

	house = utilityFunctions.dotdict()
	house.type = "house"
	house.lotArea = utilityFunctions.dotdict({"y_min": h_min, "y_max": h_max, "x_min": x_min, "x_max": x_max, "z_min": z_min, "z_max": z_max})

	utilityFunctions.cleanProperty(matrix, h_min+1, h_max, x_min, x_max, z_min, z_max)

	(h_min, h_max, x_min, x_max, z_min, z_max) = getHouseAreaInsideLot(h_min, h_max, x_min, x_max, z_min, z_max)
	# calculate the top height of the walls, i.e. where the first
	# row of blocks of the pitched roof will be placed
	ceiling_bottom = h_max -int((h_max-h_min) * 0.5)
	house.buildArea = utilityFunctions.dotdict({"y_min": h_min, "y_max": ceiling_bottom, "x_min": x_min, "x_max": x_max, "z_min": z_min, "z_max": z_max})
	
	logging.info("Generating house at area {}".format(house.lotArea))
	logging.info("Construction area {}".format(house.buildArea))
	
	wall = (43, RNG.randint(11,15))
	ceiling = (5, RNG.randint(1,5)) if ceiling == None else ceiling
	floor = wall

	# generate walls from x_min+1, x_max-1, etc to leave space for the roof
	generateWalls(matrix, house.buildArea.y_min, house.buildArea.y_max, house.buildArea.x_min, house.buildArea.x_max, house.buildArea.z_min, house.buildArea.z_max, wall)
	generateFloor(matrix, house.buildArea.y_min, house.buildArea.x_min, house.buildArea.x_max, house.buildArea.z_min, house.buildArea.z_max, floor)

	house.orientation = getOrientation(matrix, house.lotArea)
	window_y = house.buildArea.y_min + 3
	door_y = house.buildArea.y_min + 1
	
	if house.orientation == "N":
		door_x = RNG.randint(house.buildArea.x_min+4, house.buildArea.x_max-4)
		door_z = house.buildArea.z_min
		generateDoor(matrix, door_y, door_x, door_z, (64,9), (64,1))
		house.entranceLot = (h_min+1, door_x, house.lotArea.z_min)
		# entrance path
		for z in range(house.lotArea.z_min, door_z):
			matrix.setValue(h_min,door_x,z, (4,0))
			matrix.setValue(h_min,door_x-1,z, (4,0))
			matrix.setValue(h_min,door_x+1,z, (4,0))
		
	elif house.orientation == "S":
		door_x = RNG.randint(house.buildArea.x_min+4, house.buildArea.x_max-4)
		door_z = house.buildArea.z_max
		generateDoor(matrix, door_y, door_x, door_z, (64,9), (64,3))
		house.entranceLot = (h_min+1, door_x, house.lotArea.z_max)
		# entrance path
		for z in range(door_z+1, house.lotArea.z_max+1):
			matrix.setValue(h_min,door_x,z, (4,0))
			matrix.setValue(h_min,door_x-1,z, (4,0))
			matrix.setValue(h_min,door_x+1,z, (4,0))

	elif house.orientation == "W":
		door_x = house.buildArea.x_min
		door_z = RNG.randint(house.buildArea.z_min+4, house.buildArea.z_max-4)
		generateDoor(matrix, door_y, door_x, door_z, (64,8), (64,0))
		house.entranceLot = (h_min+1, house.lotArea.x_min, door_z) 
		# entrance path
		for x in range(house.lotArea.x_min, door_x):
			matrix.setValue(h_min,x,door_z, (4,0))
			matrix.setValue(h_min,x,door_z-1, (4,0))
			matrix.setValue(h_min,x,door_z+1, (4,0))

	elif house.orientation == "E":
		door_x = house.buildArea.x_max
		door_z = RNG.randint(house.buildArea.z_min+4, house.buildArea.z_max-4)
		generateDoor(matrix, door_y, door_x, door_z, (64,9), (64,2))
		house.entranceLot = (h_min+1, house.lotArea.x_max, door_z) 
		# entrance path
		for x in range(door_x+1, house.lotArea.x_max+1):
			matrix.setValue(h_min,x,door_z, (4,0))
			matrix.setValue(h_min,x,door_z-1, (4,0))
			matrix.setValue(h_min,x,door_z+1, (4,0))

	if house.orientation == "N" or house.orientation == "S":
		generateWindow_alongX(matrix, window_y, house.buildArea.x_min, house.buildArea.z_min, house.buildArea.z_max)
		generateWindow_alongX(matrix, window_y, house.buildArea.x_max, house.buildArea.z_min, house.buildArea.z_max)
		generateCeiling_x(matrix, ceiling_bottom, h_max, x_min-1, x_max+1, z_min-1, z_max+1, ceiling, wall, 0)
	elif house.orientation == "E" or house.orientation == "W":
		generateWindow_alongZ(matrix, window_y, house.buildArea.z_min, house.buildArea.x_min, house.buildArea.x_max)
		generateWindow_alongZ(matrix, window_y, house.buildArea.z_max, house.buildArea.x_min, house.buildArea.x_max)
		generateCeiling_z(matrix, ceiling_bottom, h_max, x_min-1, x_max+1, z_min-1, z_max+1, ceiling, wall, 0)

	generateInterior(matrix, h_min, ceiling_bottom, house.buildArea.x_min, house.buildArea.x_max, house.buildArea.z_min, house.buildArea.z_max, ceiling)
	generateGarden(matrix, house)

	return house

def getHouseAreaInsideLot(h_min, h_max, x_min, x_max, z_min, z_max):
	house_size_x = RNG.randint(10,13)
	if x_max-x_min > house_size_x:
		x_mid = x_min + (x_max-x_min)/2
		x_min = x_mid - house_size_x/2
		x_max = x_mid + house_size_x/2

	house_size_z = RNG.randint(10,13)
	if z_max-z_min > house_size_z:
		z_mid = z_min + (z_max-z_min)/2
		z_min = z_mid - house_size_z/2
		z_max = z_mid + house_size_z/2

	house_size_h = (house_size_x+house_size_z)/2
	if h_max-h_min > 15 or h_max-h_min > house_size_h: 
		h_max = h_min+ ((house_size_x+house_size_z)/2)

	return (h_min, h_max, x_min, x_max, z_min, z_max)

def generateFloor(matrix, h, x_min, x_max, z_min, z_max, floor):
	for x in range(x_min, x_max+1):
		for z in range(z_min, z_max+1):
			matrix.setValue(h,x,z,floor)

def generateWalls(matrix, h_min, ceiling_bottom, x_min, x_max, z_min, z_max, wall):

	# walls along x axis
	for x in range(x_min, x_max+1):
		for y in range(h_min, ceiling_bottom):
			matrix.setValue(y,x,z_max, wall)
			matrix.setValue(y,x,z_min, wall)

	# walls along z axis
	for z in range(z_min, z_max+1):
		for y in range(h_min, ceiling_bottom):
			matrix.setValue(y,x_max,z, wall)
			matrix.setValue(y,x_min,z, wall)

def generateInterior(matrix, h_min, h_max, x_min, x_max, z_min, z_max, wood):
	
	generateCarpet(matrix.matrix, h_min+1, x_min+1, x_max, z_min+1, z_max)
	generateBed(matrix, h_min, x_max, z_min)

	x_mid = x_max - int((x_max - x_min)/2)
	z_mid = z_max - int((z_max - z_min)/2)

	generateCentralTable(matrix, h_min, x_mid, z_mid)
	generateBookshelf(matrix, h_min, x_max, z_max)
	generateCouch(matrix, h_min, x_min, z_max)
	# wooden board in which chandelier is fixed
	for z in range(z_min+1, z_max):
		matrix.setValue(h_max, x_mid, z, wood)
	generateChandelier(matrix, h_max, x_mid, z_mid)


def generateCeiling_x(matrix, h_min, h_max, x_min, x_max, z_min, z_max, ceiling, wall, recr):

	if x_min+recr+1 <= x_max-recr-1:
		for z in range(z_min, z_max+1):					  # intended pitched roof effect
			matrix.setValue(h_min+recr, x_min+recr, z, ceiling)   #       _  
			matrix.setValue(h_min+recr, x_max-recr, z, ceiling)   #     _| |_
			matrix.setValue(h_min+recr, x_min+recr+1, z, ceiling) #   _|     |_
			matrix.setValue(h_min+recr, x_max-recr-1, z, ceiling) # _|         |_
		for x in range(x_min+recr+2, x_max-recr-1):		
			matrix.setValue(h_min+recr, x, z_min+1, wall) # fill front and back part of the roof
			matrix.setValue(h_min+recr, x, z_max-1, wall)

	if recr < h_max-h_min:
		generateCeiling_x(matrix, h_min, h_max, x_min, x_max, z_min, z_max, ceiling, wall, recr+1)
	else:
	 	old_recr = h_min+recr
	 	while x_min+recr+1 < x_max-recr-1:
	 		recr += 1
	 		for z in range (z_min, z_max+1):
	 			matrix.setValue(old_recr, x_min+recr+1, z, ceiling)
				matrix.setValue(old_recr, x_max-recr-1, z, ceiling)

def generateCeiling_z(matrix, h_min, h_max, x_min, x_max, z_min, z_max, ceiling, wall, recr):

	if z_min+recr+1 <= z_max-recr-1:
		for x in range(x_min, x_max+1):
			matrix.setValue(h_min+recr, x, z_min+recr, ceiling)
			matrix.setValue(h_min+recr, x, z_max-recr, ceiling)
			matrix.setValue(h_min+recr, x, z_min+recr+1, ceiling)
			matrix.setValue(h_min+recr, x, z_max-recr-1, ceiling)
		for z in range(z_min+recr+2, z_max-recr-1):
			matrix.setValue(h_min+recr, x_min+1, z, wall)
			matrix.setValue(h_min+recr, x_max-1, z, wall)

	if recr < h_max-h_min:
		generateCeiling_z(matrix, h_min, h_max, x_min, x_max, z_min, z_max, ceiling, wall, recr+1)
	else:
		old_recr = h_min+recr
		while  z_min+recr+1 < z_max-recr-1:
			recr += 1
			for x in range (x_min, x_max+1):
				matrix.setValue(old_recr, x, z_min+recr+1, ceiling)
				matrix.setValue(old_recr, x, z_max-recr-1, ceiling)

def generateDoor(matrix, y, x, z, door_up, door_down):
	matrix.setValue(y+1, x, z, door_up)
	matrix.setValue(y, x, z, door_down)


# The next two functions do the same thing, but they are
# separated for more clear understanding
def generateWindow_alongX(matrix, h, x, z_min, z_max):
	for z in range(z_min+2, z_max-2, 3):
		 	matrix.setValue(h, x, z, (20,0))
		 	matrix.setValue(h-1, x, z, (20,0))
		 	matrix.setValue(h, x, z+1, (20,0))
		 	matrix.setValue(h-1, x, z+1, (20,0))

def generateWindow_alongZ(matrix, h, z, x_min, x_max):
	for x in range(x_min+2, x_max-2, 3):

			matrix.setValue(h, x, z, (20,0))
			matrix.setValue(h-1, x, z, (20,0))
			matrix.setValue(h, x+1, z, (20,0))
			matrix.setValue(h-1, x+1, z, (20,0))

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

def generateGarden(matrix, house):

	def findOrientationGarden(house): #finding where to build the garden depending on where there is the most space left on the house lot
		n_space = (abs(house.lotArea.z_min - house.buildArea.z_min), "N")
		s_space = (abs(house.lotArea.z_max - house.buildArea.z_max), "S")
		e_space = (abs(house.lotArea.x_max - house.buildArea.x_max), "E")
		w_space = (abs(house.lotArea.x_min - house.buildArea.x_min), "W")
		space_list = []
		#We check the orientation of the door of the house so that we don't build the garden in front of it
		if house.orientation == "N":
			space_list.append(s_space)
			space_list.append(e_space)
			space_list.append(w_space)
			space_list_sorted = sorted(space_list)
			house.gardenOrientation = space_list_sorted[0][1]
			if house.gardenOrientation == "S":
				house.gardenOrientationSecondary = space_list_sorted[1][1]
			else:
				house.gardenOrientationSecondary = "S"

		if house.orientation == "S":
			space_list.append(n_space)
			space_list.append(e_space)
			space_list.append(w_space)
			space_list_sorted = sorted(space_list)
			house.gardenOrientation = space_list_sorted[0][1]
			if house.gardenOrientation == "N":
				house.gardenOrientationSecondary = space_list_sorted[1][1]
			else:
				house.gardenOrientationSecondary = "N"

		if house.orientation == "E":
			space_list.append(s_space)
			space_list.append(n_space)
			space_list.append(w_space)
			space_list_sorted = sorted(space_list)
			house.gardenOrientation = space_list_sorted[0][1]
			if house.gardenOrientation == "W":
				house.gardenOrientationSecondary = space_list_sorted[1][1]
			else:
				house.gardenOrientationSecondary = "W"

		if house.orientation == "W":
			space_list.append(s_space)
			space_list.append(e_space)
			space_list.append(n_space)
			space_list_sorted = sorted(space_list)
			house.gardenOrientation = space_list_sorted[0][1]
			if house.gardenOrientation == "E":
				house.gardenOrientationSecondary = space_list_sorted[1][1]
			else:
				house.gardenOrientationSecondary = "E"
		return space_list_sorted

	def findPointsGarden(house):
		if house.gardenOrientationSecondary in ["E", "W"]:
			side_position = RNG.randint(house.buildArea.z_min+1, house.buildArea.z_max-1)
		else:
			side_position = RNG.randint(house.buildArea.x_min+1, house.buildArea.x_max-1)

		if house.gardenOrientation == "N":
			if house.gardenOrientationSecondary == "E":
				house.gardenPoint1 = (house.buildArea.x_min, house.buildArea.z_min-1)
				house.gardenPoint2 = (house.buildArea.x_min, house.lotArea.z_min+1)
				house.gardenPoint3 = (house.lotArea.x_max-1, house.lotArea.z_min+1)
				house.gardenPoint4 = (house.lotArea.x_max-1, side_position)
				house.gardenPoint5 = (house.buildArea.x_max+1, side_position)
			else:
				house.gardenPoint1 = (house.buildArea.x_max, house.buildArea.z_min-1)
				house.gardenPoint2 = (house.buildArea.x_max, house.lotArea.z_min+1)
				house.gardenPoint3 = (house.lotArea.x_min+1, house.lotArea.z_min+1)
				house.gardenPoint4 = (house.lotArea.x_min+1, side_position)
				house.gardenPoint5 = (house.buildArea.x_min-1, side_position)

		elif house.gardenOrientation == "S":
			if house.gardenOrientationSecondary == "E":
				house.gardenPoint1 = (house.buildArea.x_min, house.buildArea.z_max+1)
				house.gardenPoint2 = (house.buildArea.x_min, house.lotArea.z_max-1)
				house.gardenPoint3 = (house.lotArea.x_max-1, house.lotArea.z_max-1)
				house.gardenPoint4 = (house.lotArea.x_max-1, side_position)
				house.gardenPoint5 = (house.buildArea.x_max+1, side_position)
			else:
				house.gardenPoint1 = (house.buildArea.x_max, house.buildArea.z_max+1)
				house.gardenPoint2 = (house.buildArea.x_max, house.lotArea.z_max-1)
				house.gardenPoint3 = (house.lotArea.x_min+1, house.lotArea.z_max-1)
				house.gardenPoint4 = (house.lotArea.x_min+1, side_position)
				house.gardenPoint5 = (house.buildArea.x_min-1, side_position)
		elif house.gardenOrientation == "E":
			if house.gardenOrientationSecondary == "N":
				house.gardenPoint1 = (house.buildArea.x_max+1, house.buildArea.z_max)
				house.gardenPoint2 = (house.lotArea.x_max-1, house.buildArea.z_max)
				house.gardenPoint3 = (house.lotArea.x_max-1, house.lotArea.z_min+1)
				house.gardenPoint4 = (side_position, house.lotArea.z_min+1)
				house.gardenPoint5 = (side_position, house.buildArea.z_min-1)
			else:
				house.gardenPoint1 = (house.buildArea.x_max+1, house.buildArea.z_min)
				house.gardenPoint2 = (house.lotArea.x_max-1, house.buildArea.z_min)
				house.gardenPoint3 = (house.lotArea.x_max-1, house.lotArea.z_max-1)
				house.gardenPoint4 = (side_position, house.lotArea.z_max-1)
				house.gardenPoint5 = (side_position, house.buildArea.z_max+1)
		else:
			if house.gardenOrientationSecondary == "N":
				house.gardenPoint1 = (house.buildArea.x_min-1, house.buildArea.z_max)
				house.gardenPoint2 = (house.lotArea.x_min+1, house.buildArea.z_max)
				house.gardenPoint3 = (house.lotArea.x_min+1, house.lotArea.z_min+1)
				house.gardenPoint4 = (side_position, house.lotArea.z_min+1)
				house.gardenPoint5 = (side_position, house.buildArea.z_min-1)
			else:
				house.gardenPoint1 = (house.buildArea.x_min-1, house.buildArea.z_min)
				house.gardenPoint2 = (house.lotArea.x_min+1, house.buildArea.z_min)
				house.gardenPoint3 = (house.lotArea.x_min+1, house.lotArea.z_max-1)
				house.gardenPoint4 = (side_position, house.lotArea.z_max-1)
				house.gardenPoint5 = (side_position, house.buildArea.z_max+1)

	def buildFence(matrix, house, p1, p2, h):
		actual_point = p1
		while actual_point != p2:
			if actual_point[0] < p2[0]:
				actual_point = (actual_point[0] + 1, actual_point[1])
			elif actual_point[0] > p2[0]:
				actual_point = (actual_point[0] - 1, actual_point[1])
			elif actual_point[1] < p2[1]:
				actual_point = (actual_point[0], actual_point[1] + 1)
			elif actual_point[1] > p2[1]:
				actual_point = (actual_point[0], actual_point[1] - 1)
			matrix.setValue(h, actual_point[0], actual_point[1], (85, 0))

	def buildDoorGarden(matrix, house, door_garden_y):
		door_garden_x = int(round((house.gardenPoint3[0] + house.gardenPoint4[0])*0.5))
		door_garden_z = int(round((house.gardenPoint3[1] + house.gardenPoint4[1])*0.5))
		matrix.setValue(door_garden_y, door_garden_x, door_garden_z, 107)

	h = house.lotArea.y_min+1
	list_space = findOrientationGarden(house)
	if list_space[0][0] > 2 and list_space[1][0] > 2:
		findPointsGarden(house)
		matrix.setValue(h, house.gardenPoint1[0], house.gardenPoint1[1], (85, 0))
		buildFence(matrix, house, house.gardenPoint1, house.gardenPoint2, h)
		buildFence(matrix, house, house.gardenPoint2, house.gardenPoint3, h)
		buildFence(matrix, house, house.gardenPoint3, house.gardenPoint4, h)
		buildFence(matrix, house, house.gardenPoint4, house.gardenPoint5, h)
		buildDoorGarden(matrix, house, h)
