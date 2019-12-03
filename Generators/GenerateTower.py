import random
import math
import RNG
import logging
from pymclevel import alphaMaterials, BoundingBox
import utilityFunctions as utilityFunctions
from GenerateCarpet import generateCarpet
from GenerateObject import *

def generateTower(matrix, x_min, x_max, z_min, z_max, height_map):

	tower = utilityFunctions.dotdict()
	tower.type = "tower"

	(h_tower, min_h, max_h, x_min, x_max, z_min, z_max) = getTowerAreaInsideLot(x_min, x_max, z_min, z_max, height_map)
	cleanTowerArea(matrix, min_h, h_tower, x_min, x_max, z_min, z_max)

	tower.buildArea = utilityFunctions.dotdict({"y_min": min_h, "y_max": h_tower, "x_min": x_min, "x_max": x_max, "z_min": z_min, "z_max": z_max})
	

	logging.info("Generating tower at area {}".format(tower.buildArea))
	
	wall = (45,0)
	floor = wall

	generateWalls(matrix, min_h+1, h_tower, x_min, x_max, z_min, z_max, wall)
	generateCeiling(matrix, h_tower, x_min, x_max, z_min, z_max)

	(door_pos, door_y, tower.orientation) = getOrientation(matrix, tower.buildArea, height_map)
	
	if tower.orientation == "N":
		door_x = door_pos[0]
		door_z = door_pos[1]
		generateDoor(matrix, door_y, door_x, door_z, (64,9), (64,1))
		tower.entranceLot = (door_x, door_z-1)
		matrix.setValue(door_y-1,door_x,door_z-1, (1,6))
		
	elif tower.orientation == "S":
		door_x = door_pos[0]
		door_z = door_pos[1]
		generateDoor(matrix, door_y, door_x, door_z, (64,9), (64,2))
		tower.entranceLot = (door_x, door_z+1)
		matrix.setValue(door_y-1,door_x,door_z+1, (1,6))

	elif tower.orientation == "W":
		door_x = door_pos[0]
		door_z = door_pos[1]
		generateDoor(matrix, door_y, door_x, door_z, (64,8), (64,0))
		tower.entranceLot = (door_x-1, door_z) 
		matrix.setValue(door_y-1,door_x-1,door_z, (1,6))

	elif tower.orientation == "E":
		door_x = door_pos[0]
		door_z = door_pos[1]
		generateDoor(matrix, door_y, door_x, door_z, (64,9), (64,2))
		tower.entranceLot = (door_x+1, door_z) 
		matrix.setValue(door_y-1,door_x+1,door_z, (1,6))

	generateFloor(matrix, door_y-1, x_min, x_max, z_min, z_max, floor)
	generateInside(matrix, door_y, h_tower, x_min, x_max, z_min, z_max, tower.orientation)

	return tower

def getTowerAreaInsideLot(x_min, x_max, z_min, z_max, height_map):
	tower_size = random.choice([5, 7])
	min_h = 255
	max_h = 0
	#fixing base buildArea
	bx_min = x_min+1
	bx_max = bx_min+tower_size-1
	bz_min = z_min+1
	bz_max = bz_min+tower_size-1
	#get base score for this area
	score_buildArea = utilityFunctions.getScoreArea_type1(height_map, bx_min, bx_max, bz_min, bz_max)

	#check every other possible area in the parcel to find if there is an area with a worse flatness score
	for x in range(x_min+1, x_max-tower_size+1):
		for z in range(z_min+1, z_max-tower_size+1):
			nx_min = x
			nx_max = x + tower_size-1
			nz_min = z
			nz_max = z + tower_size-1
			new_score_buildArea = utilityFunctions.getScoreArea_type1(height_map, nx_min, nx_max, nz_min, nz_max)
			if new_score_buildArea > score_buildArea:
				bx_min = nx_min
				bx_max = nx_max
				bz_min = nz_min
				bz_max = nz_max
				score_buildArea = new_score_buildArea


	for x in range(bx_min-1, bx_max+2):
		if height_map[x][bz_max+1] < min_h:
			min_h = height_map[x][bz_max+1]
		if height_map[x][bz_max+1] > max_h:
			max_h = height_map[x][bz_max+1]
		if height_map[x][bz_min-1] < min_h:
			min_h = height_map[x][bz_min-1]
		if height_map[x][bz_min-1] > max_h:
			max_h = height_map[x][bz_min-1]

	for z in range(bz_min-1, bz_max+2):
		if height_map[bx_max+1][z] < min_h:
			min_h = height_map[bx_max+1][z]
		if height_map[bx_max+1][z] > max_h:
			max_h = height_map[bx_max+1][z]
		if height_map[bx_min-1][z] < min_h:
			min_h = height_map[bx_min-1][z]
		if height_map[bx_min-1][z] > max_h:
			max_h = height_map[bx_min-1][z]

	h_tower = max_h + 3 + RNG.randint(1,6)

	return (h_tower, min_h, max_h, bx_min, bx_max, bz_min, bz_max)

def generateFloor(matrix, h, x_min, x_max, z_min, z_max, floor):
	for x in range(x_min, x_max+1):
		for z in range(z_min, z_max+1):
			matrix.setValue(h,x,z,floor)
	x_mid = int((x_max - x_min)/2)
	z_mid = int((z_max - z_min)/2)
	matrix.setValue(h+1,x_mid,z_mid,(89,0))

def generateWalls(matrix, h_min, h_tower, x_min, x_max, z_min, z_max, wall):

	# walls along x axis
	for x in range(x_min, x_max+1):
		for y in range(h_min, h_tower+1):
			matrix.setValue(y,x,z_max, wall)
			matrix.setValue(y,x,z_min, wall)

	# walls along z axis
	for z in range(z_min, z_max+1):
		for y in range(h_min, h_tower+1):
			matrix.setValue(y,x_max,z, wall)
			matrix.setValue(y,x_min,z, wall)

def generateDoor(matrix, y, x, z, door_up, door_down):
	matrix.setValue(y+1, x, z, door_up)
	matrix.setValue(y, x, z, door_down)

def getOrientation(matrix, area, height_map):
	bx_mid = int(area.x_min + (area.x_max-area.x_min)/2)
	bz_mid = int(area.z_min + (area.z_max-area.z_min)/2)

	N_pos = (bx_mid, area.z_min)
	S_pos = (bx_mid, area.z_max)
	E_pos = (area.x_max, bz_mid)
	W_pos = (area.x_min, bz_mid)

	list_h = [(height_map[N_pos[0]][N_pos[1]-1], N_pos), (height_map[S_pos[0]][S_pos[1]+1], S_pos), (height_map[E_pos[0]+1][E_pos[1]], E_pos), (height_map[W_pos[0]-1][W_pos[1]], W_pos)]
	list_h = sorted(list_h)

	if list_h[0][1] == N_pos:
		return (N_pos, list_h[0][0]+1, "N")
	elif list_h[0][1] == S_pos:
		return (S_pos, list_h[0][0]+1, "S")
	elif list_h[0][1] == E_pos:
		return (E_pos, list_h[0][0]+1, "E")
	elif list_h[0][1] == W_pos:
		return (W_pos, list_h[0][0]+1, "W")

def cleanTowerArea(matrix, min_h, h_tower, x_min, x_max, z_min, z_max):
	for h in range(min_h, h_tower+1):
		for x in range(x_min-1, x_max+2):
			for z in range(z_min-1, z_max+2):
				if matrix.getValue(h,x,z) in [17, 18, 162, 161]:
					matrix.setValue(h,x,z, (0,0))

	for h in range(min_h, h_tower+1):
		for x in range(x_min+1, x_max):
			for z in range(z_min+1, z_max):
				matrix.setValue(h,x,z, (0,0))

def generateCeiling(matrix, h, x_min, x_max, z_min, z_max):
	isTop = True
	i = 0
	while x_min-1+i != x_max+1-i:
		for x in range(x_min-1+i, x_max+2-i):
			if isTop:
				matrix.setValue(h,x,z_min-1+i, (44,12))
				matrix.setValue(h,x,z_max+1-i, (44,12))
			else:
				matrix.setValue(h,x,z_min-1+i, (44,4))
				matrix.setValue(h,x,z_max+1-i, (44,4))
		for z in range(z_min-1+i, z_max+2-i):
			if isTop:
				matrix.setValue(h,x_min-1+i,z, (44,12))
				matrix.setValue(h,x_max+1-i,z, (44,12))
			else:
				matrix.setValue(h,x_min-1+i,z, (44,4))
				matrix.setValue(h,x_max+1-i,z, (44,4))
		if isTop:
			h += 1
		isTop = not isTop
		i += 1
	if isTop:
		matrix.setValue(h,x_min-1+i,z_max+1-i, (44,12))
	else:
		matrix.setValue(h,x_min-1+i,z_max+1-i, (44,4))

def generateInside(matrix, h_min, h_tower, x_min, x_max, z_min, z_max, orientation):
	h_actual = h_min
	x_mid = int((x_min+x_max)*0.5)
	z_mid = int((z_min+z_max)*0.5)

	if orientation == "S":
		x_actual = x_min+1
		z_actual = z_max-1
		while h_actual != h_tower - 1.0: #generate the stairs going up the tower depending on its orientation
			while (x_actual, z_actual) != (x_min+1, z_min+1) and h_actual != h_tower - 1.0: #to bot left
				if h_actual%1 != 0:
					matrix.setValue(int(h_actual),x_actual,z_actual, (44,10))
				else:
					matrix.setValue(int(h_actual),x_actual,z_actual, (44,2))
				h_actual += 0.5
				z_actual -= 1
			while (x_actual, z_actual) != (x_max-1, z_min+1) and h_actual != h_tower - 1.0: #to top left
				if h_actual%1 != 0:
					matrix.setValue(int(h_actual),x_actual,z_actual, (44,10))
				else:
					matrix.setValue(int(h_actual),x_actual,z_actual, (44,2))
				h_actual += 0.5
				x_actual += 1
			while (x_actual, z_actual) != (x_max-1, z_max-1) and h_actual != h_tower - 1.0: #to top right
				if h_actual%1 != 0:
					matrix.setValue(int(h_actual),x_actual,z_actual, (44,10))
				else:
					matrix.setValue(int(h_actual),x_actual,z_actual, (44,2))
				h_actual += 0.5
				z_actual += 1
			while (x_actual, z_actual) != (x_min+1, z_max-1) and h_actual != h_tower - 1.0: #to bot right
				if h_actual%1 != 0:
					matrix.setValue(int(h_actual),x_actual,z_actual, (44,10))
				else:
					matrix.setValue(int(h_actual),x_actual,z_actual, (44,2))
				h_actual += 0.5
				x_actual -= 1
		#chest and furnace
		matrix.setEntity(h_min, x_max-1, z_min+1, (54,3), "chest")
		matrix.setEntity(h_min, x_max-2, z_min+1, (61,3), "furnace")
		#plateform
		buildPlatform(matrix, int(h_actual)-1, x_actual, z_actual)


	elif orientation == "N":
		x_actual = x_max-1
		z_actual = z_min+1
		while h_actual != h_tower - 1.0:
			while (x_actual, z_actual) != (x_max-1, z_max-1) and h_actual != h_tower - 1.0: #to top right
				if h_actual%1 != 0:
					matrix.setValue(int(h_actual),x_actual,z_actual, (44,10))
				else:
					matrix.setValue(int(h_actual),x_actual,z_actual, (44,2))
				h_actual += 0.5
				z_actual += 1
			while (x_actual, z_actual) != (x_min+1, z_max-1) and h_actual != h_tower - 1.0: #to bot right
				if h_actual%1 != 0:
					matrix.setValue(int(h_actual),x_actual,z_actual, (44,10))
				else:
					matrix.setValue(int(h_actual),x_actual,z_actual, (44,2))
				h_actual += 0.5
				x_actual -= 1
			while (x_actual, z_actual) != (x_min+1, z_min+1) and h_actual != h_tower - 1.0: #to bot left
				if h_actual%1 != 0:
					matrix.setValue(int(h_actual),x_actual,z_actual, (44,10))
				else:
					matrix.setValue(int(h_actual),x_actual,z_actual, (44,2))
				h_actual += 0.5
				z_actual -= 1
			while (x_actual, z_actual) != (x_max-1, z_min+1) and h_actual != h_tower - 1.0: #to top left
				if h_actual%1 != 0:
					matrix.setValue(int(h_actual),x_actual,z_actual, (44,10))
				else:
					matrix.setValue(int(h_actual),x_actual,z_actual, (44,2))
				h_actual += 0.5
				x_actual += 1
		matrix.setEntity(h_min, x_min+1, z_max-1, (54,2), "chest")
		matrix.setEntity(h_min, x_min+2, z_max-1, (61,2), "furnace")
		buildPlatform(matrix, int(h_actual)-1, x_actual, z_actual)

	elif orientation == "E":
		x_actual = x_max-1
		z_actual = z_max-1
		while h_actual != h_tower - 1.0:
			while (x_actual, z_actual) != (x_min+1, z_max-1) and h_actual != h_tower - 1.0: #to bot right
				if h_actual%1 != 0:
					matrix.setValue(int(h_actual),x_actual,z_actual, (44,10))
				else:
					matrix.setValue(int(h_actual),x_actual,z_actual, (44,2))
				h_actual += 0.5
				x_actual -= 1
			while (x_actual, z_actual) != (x_min+1, z_min+1) and h_actual != h_tower - 1.0: #to bot left
				if h_actual%1 != 0:
					matrix.setValue(int(h_actual),x_actual,z_actual, (44,10))
				else:
					matrix.setValue(int(h_actual),x_actual,z_actual, (44,2))
				h_actual += 0.5
				z_actual -= 1
			while (x_actual, z_actual) != (x_max-1, z_min+1) and h_actual != h_tower - 1.0: #to top left
				if h_actual%1 != 0:
					matrix.setValue(int(h_actual),x_actual,z_actual, (44,10))
				else:
					matrix.setValue(int(h_actual),x_actual,z_actual, (44,2))
				h_actual += 0.5
				x_actual += 1
			while (x_actual, z_actual) != (x_max-1, z_max-1) and h_actual != h_tower - 1.0: #to top right
				if h_actual%1 != 0:
					matrix.setValue(int(h_actual),x_actual,z_actual, (44,10))
				else:
					matrix.setValue(int(h_actual),x_actual,z_actual, (44,2))
				h_actual += 0.5
				z_actual += 1
		matrix.setEntity(h_min, x_min+1, z_min+1, (54,5), "chest")
		matrix.setEntity(h_min, x_min+1, z_min+2, (61,5), "furnace")
		buildPlatform(matrix, int(h_actual)-1, x_actual, z_actual)

	else:
		x_actual = x_min+1
		z_actual = z_min+1
		while h_actual != h_tower - 1.0:
			while (x_actual, z_actual) != (x_max-1, z_min+1) and h_actual != h_tower - 1.0: #to top left
				if h_actual%1 != 0:
					matrix.setValue(int(h_actual),x_actual,z_actual, (44,10))
				else:
					matrix.setValue(int(h_actual),x_actual,z_actual, (44,2))
				h_actual += 0.5
				x_actual += 1
			while (x_actual, z_actual) != (x_max-1, z_max-1) and h_actual != h_tower - 1.0: #to top right
				if h_actual%1 != 0:
					matrix.setValue(int(h_actual),x_actual,z_actual, (44,10))
				else:
					matrix.setValue(int(h_actual),x_actual,z_actual, (44,2))
				h_actual += 0.5
				z_actual += 1
			while (x_actual, z_actual) != (x_min+1, z_max-1) and h_actual != h_tower - 1.0: #to bot right
				if h_actual%1 != 0:
					matrix.setValue(int(h_actual),x_actual,z_actual, (44,10))
				else:
					matrix.setValue(int(h_actual),x_actual,z_actual, (44,2))
				h_actual += 0.5
				x_actual -= 1
			while (x_actual, z_actual) != (x_min+1, z_min+1) and h_actual != h_tower - 1.0: #to bot left
				if h_actual%1 != 0:
					matrix.setValue(int(h_actual),x_actual,z_actual, (44,10))
				else:
					matrix.setValue(int(h_actual),x_actual,z_actual, (44,2))
				h_actual += 0.5
				z_actual -= 1
		matrix.setEntity(h_min, x_max-1, z_max-1, (54,4), "chest")
		matrix.setEntity(h_min, x_max-1, z_max-2, (61,4), "furnace")
		buildPlatform(matrix, int(h_actual)-1, x_actual, z_actual)

	#light
	matrix.setValue(h_min-1,x_mid,z_mid, (89,0))
	#windows
	matrix.setValue(h_tower,x_mid,z_max, (20,0))
	matrix.setValue(h_tower,x_mid,z_min, (20,0))
	matrix.setValue(h_tower,x_max,z_mid, (20,0))
	matrix.setValue(h_tower,x_min,z_mid, (20,0))

def buildPlatform(matrix, h, x_actual, z_actual):
	anvil = False
	craftingTable = False
	light = False
	for neighbor_position in [(0, -1), (0, 1), (-1, 0), (1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1), (0, 0)]:
		new_position = (x_actual + neighbor_position[0], z_actual + neighbor_position[1])
		if utilityFunctions.getBlockFullValue(matrix, new_position[0], h, new_position[1]) == (0,0):
			matrix.setValue(h, new_position[0], new_position[1], (44,10))
			if craftingTable == False:
				matrix.setValue(h+1, new_position[0], new_position[1], (58,0))
				craftingTable = True
			elif light == False:
				matrix.setValue(h+1, new_position[0], new_position[1], (50,5))
				light = True
			elif anvil == False:
				matrix.setValue(h+1, new_position[0], new_position[1], (145,0))
				anvil = True