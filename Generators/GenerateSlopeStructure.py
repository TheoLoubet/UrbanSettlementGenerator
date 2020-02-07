import random
import RNG
import logging
import utilityFunctions as utilityFunctions
import GenerateTower
from enum import Enum

AIR_ID = (0, 0)
GRASS_ID = (2, 0)
FENCE_ID = (85, 0)
OAK_WOOD_ID = (17, 0)
OAK_FENCE_GATE = (107, 0)
WATER_ID = (8, 0)
TORCH_ID = (50, 0)
REDSTONE_TORCH_ID = (76, 0)
CHEST_ID = (54, 2)
RAIL_ID = 66
POWERED_RAIL_ID = 27
## Orientation goes from 0 to 9 included (2, 3, 4, 5 -> slopes) (6, 7, 8, 9 -> turns)
Orientation = Enum("Orientation", "VERTICAL HORIZONTAL NORTH SOUTH WEST EAST NORTH_EAST SOUTH_EAST SOUTH_WEST NORTH_WEST")

MINIMUM_ROLLER_COASTER_LENGTH = 7
MAX_SAME_HEIGHT_RAIL_LENGTH = 5
MAX_INCREASING_LENGTH_TRIES = 6

max_rail_length = 0

## IMPROVEMENTS IDEAS :
## - being able to put multiple rails on the same (x, z) (for example when the rails are going down a mine)
## -

def generateSlopeStructure(matrix, height_map, h_max, x_min, x_max, z_min, z_max, allowStraightRails=False):
    logging.info("Trying to generate roller coaster")

    cleanProperty(matrix, height_map, h_max, x_min, x_max, z_min, z_max)
    #spawnFlowers(matrix, height_map, x_min, x_max, z_min, z_max)
    return_value = generateRollerCoaster(matrix, height_map, h_max, x_min, x_max, z_min, z_max, allowStraightRails)
    if return_value == 0:
        return 0
    slope = utilityFunctions.dotdict()
    slope.type = "rollerCoaster"
    slope.lotArea = utilityFunctions.dotdict({"y_min": 0, "y_max": h_max, "x_min": x_min, "x_max": x_max, "z_min": z_min, "z_max": z_max})
    slope.buildArea = utilityFunctions.dotdict({"y_min": 0, "y_max": h_max, "x_min": x_min, "x_max": x_max, "z_min": z_min, "z_max": z_max})
    slope.orientation = getOrientation()
    slope.entranceLot = (height_map[x_min][z_min], slope.lotArea.x_min, slope.lotArea.z_min)
    return slope

def spawnFlowers(matrix, height_map, x_min, x_max, z_min, z_max):
    for x in range(x_min, x_max):
        for z in range(z_min, z_max):
            matrix.setValue(height_map[x][z], x, z, GRASS_ID)
            matrix.setValue(height_map[x][z] + 1, x, z, (38, RNG.randint(0, 9)))

def generateRollerCoaster(matrix, height_map, h_max, x_min, x_max, z_min, z_max, allowStraightRails, allowUpdateHeightMap=True):
    global max_rail_length

    ## set rail_map to 0's
    rail_map = [[0 for z in range(z_max + 1)] for x in range(x_max + 1)]

    HPMap = highestPointsMap(height_map, x_min, x_max, z_min, z_max)
    highestPoint = HPMap[0]

    previous_max_rail_length = 0
    for HP in HPMap:
        logging.info("Attempt to generate roller coaster with highest point : {}".format(HP))
        rollRollerRoll(matrix, height_map, rail_map, 0, 0, MAX_SAME_HEIGHT_RAIL_LENGTH, x_min + 1, x_max - 1, z_min + 1, z_max - 1, HP[0], HP[1], 0)
        if previous_max_rail_length < max_rail_length:
            previous_max_rail_length = max_rail_length
            highestPoint = HP

    #logging.info("Final highest point : {}".format(highestPoint))

    ## cancel the run if the roller coaster is not long enough
    if max_rail_length < MINIMUM_ROLLER_COASTER_LENGTH:
        logging.info("Roller coaster is too short with length : {}, cancelling generation".format(max_rail_length))
        return 0

    ## first run
    rail_map = cleanRailMap(rail_map, x_max, z_max)
    railIndex = rollRollerRoll(matrix, height_map, rail_map, 0, 0, MAX_SAME_HEIGHT_RAIL_LENGTH, x_min + 1, x_max - 1, z_min + 1, z_max - 1, highestPoint[0], highestPoint[1], 1)


    ## second run
    for length in range(MAX_SAME_HEIGHT_RAIL_LENGTH, MAX_SAME_HEIGHT_RAIL_LENGTH + MAX_INCREASING_LENGTH_TRIES):
        logging.info("Try to connect rails with max same level length : {}".format(length))
        rail_map = cleanRailMap(rail_map, x_max, z_max, railIndex)
        return_value = rollRollerRoll(matrix, height_map, rail_map, 0, 0, length, x_min, x_max, z_min, z_max, highestPoint[0], highestPoint[1], 2, railIndex)
        if return_value != 0:
            break
    if not allowStraightRails and return_value == 0: # did not find a connecting path
        return 0

    ## reinitialize the starting point in the rail map
    rail_map[highestPoint[0]][highestPoint[1]] = railIndex - 1

    ## generate the rails
    generateRails(matrix, height_map, rail_map, x_min, x_max, z_min, z_max, highestPoint)
    generateChest(matrix, height_map, rail_map, highestPoint[0], highestPoint[1], x_min, x_max, z_min, z_max)

    ## reinitialize global variable
    max_rail_length = 0

    # set rail blocks in height_map to -1
    if allowUpdateHeightMap:
        updateHeightMap(height_map, rail_map, x_max, z_max)
    return 1

def updateHeightMap(height_map, rail_map, x_max, z_max):
    for x in range(x_max + 1):
        for z in range(z_max + 1):
            if rail_map[x][z] > 1:
                height_map[x][z] = -1

def cleanRailMap(rail_map, x_max, z_max, eraseFrom = 1):
    for x in range(x_max + 1):
        for z in range(z_max + 1):
            if rail_map[x][z] == 1 or rail_map[x][z] >= eraseFrom:
                rail_map[x][z] = 0
    return rail_map

def generateRails(matrix, height_map, rail_map, x_min, x_max, z_min, z_max, highestPoint):
    for x in range(x_min, x_max + 1):
        for z in range(z_min, z_max + 1):
            if rail_map[x][z] >= 2:
                ## check rail orientation using neighbouring rails
                binary_orientation_index = getRailOrientation(height_map, rail_map, x, z, x_max, z_max)

                ## set rail orientation
                rail_orientation = getOrientationFromBinaryIndex(binary_orientation_index)

                ## generate the rail
                #logging.info("Generating a rail (index:{}) in x:{}, z:{}, y:{} with orientation:{}".format(rail_map[x][z], x, z, height_map[x][z], rail_orientation))
                matrix.setValue(height_map[x][z], x, z, OAK_WOOD_ID)

                ## regular rail
                if binary_orientation_index < 16:
                    matrix.setValue(height_map[x][z] + 1, x, z, (RAIL_ID, rail_orientation))
                ## powered rail
                else:
                    matrix.setValue(height_map[x][z] + 1, x, z, (POWERED_RAIL_ID, rail_orientation))
                    matrix.setEntity(height_map[x][z] - 1, x, z, REDSTONE_TORCH_ID, "redstone_torch")


def isOneOrLessDifferencial(n1, n2):
    return ((n1 == n2 or n1 == n2 + 1 or n1 == n2 - 1)
            or (n1 == 2 and n2 == max_rail_length)
            or (n2 == 2 and n1 == max_rail_length)
            or (n1 == max_rail_length and n2 == 2)
            or (n2 == max_rail_length and n1 == 2))

def getRailOrientation(height_map, rail_map, x, z, x_max, z_max):
    binary_orientation_index = 0
    if isInBounds(x + 1, z, 0, x_max, 0, z_max) and isOneOrLessDifferencial(rail_map[x][z], rail_map[x + 1][z]):
        binary_orientation_index = 16 if height_map[x][z] + 1 == height_map[x + 1][z] else binary_orientation_index + 1
    if binary_orientation_index < 16 and isInBounds(x, z + 1, 0, x_max, 0, z_max) and isOneOrLessDifferencial(rail_map[x][z], rail_map[x][z + 1]):
        binary_orientation_index = 17 if height_map[x][z] + 1 == height_map[x][z + 1] else binary_orientation_index + 2
    if binary_orientation_index < 16 and isInBounds(x - 1, z, 0, x_max, 0, z_max) and isOneOrLessDifferencial(rail_map[x][z], rail_map[x - 1][z]):
        binary_orientation_index = 18 if height_map[x][z] + 1 == height_map[x - 1][z] else binary_orientation_index + 4
    if binary_orientation_index < 16 and isInBounds(x, z - 1, 0, x_max, 0, z_max) and isOneOrLessDifferencial(rail_map[x][z], rail_map[x][z - 1]):
        binary_orientation_index = 19 if height_map[x][z] + 1 == height_map[x][z - 1] else binary_orientation_index + 8
    return binary_orientation_index

def getOrientationFromBinaryIndex(binary_orientation_index):

    orientations = {
        0: Orientation.HORIZONTAL.value,
        1: Orientation.HORIZONTAL.value,
        2: Orientation.VERTICAL.value,
        3: Orientation.NORTH_EAST.value,
        4: Orientation.HORIZONTAL.value,
        5: Orientation.HORIZONTAL.value,
        6: Orientation.SOUTH_EAST.value,
        7: Orientation.HORIZONTAL.value,
        8: Orientation.VERTICAL.value,
        9: Orientation.NORTH_WEST.value,
        10: Orientation.VERTICAL.value,
        11: Orientation.VERTICAL.value,
        12: Orientation.SOUTH_WEST.value,
        13: Orientation.HORIZONTAL.value,
        14: Orientation.VERTICAL.value,
        15: Orientation.NORTH_EAST.value, # default
        16: Orientation.NORTH.value,
        17: Orientation.EAST.value,
        18: Orientation.SOUTH.value,
        19: Orientation.WEST.value
    }

    return orientations[binary_orientation_index] - 1

def spawnChest(matrix, h, x, z):
    ## generate oak log under chest
    matrix.setValue(h, x, z, OAK_WOOD_ID)
    ## generate the chest
    matrix.setEntity(h, x, z, CHEST_ID, "chest")

def generateChest(matrix, height_map, rail_map, x, z, x_min, x_max, z_min, z_max):
    ## check every neighbouring block
    for i in range(x - 1, x + 2):
        for j in range(z - 1, z + 2):
            if isInBounds(i, j, 0, x_max, 0, z_max) and rail_map[i][j] < 2:
                spawnChest(matrix, height_map[i][j] + 1, i, j)
                return
    ## floating chest if no free block
    spawnChest(matrix, height_map[x][z] + 3, x, z)

## Recursive function
## @parameter: generatorIndex is 0 for initial run, 1 for final first path, 2 for second run, 3 for final second path
def rollRollerRoll(matrix, height_map, rail_map, rail_length, current_height_rail_length, max_height_rail_length, x_min, x_max, z_min, z_max, x, z, generatorIndex, railIndex=2, previous_x=-1, previous_z=-1):
    y = height_map[x][z]
    rail_map[x][z] = 1
    rail_length += 1
    current_height_rail_length += 1

    ## Two straigth rails if it is going down
    return_value = 0
    if isNotSameLevel(height_map, x, z, previous_x, previous_z):
        current_height_rail_length = 0
        next_x = x if previous_x == x else x + (x - previous_x)
        next_z = z if previous_z == z else z + (z - previous_z)
        if canGenerateRail(matrix, height_map, rail_map, current_height_rail_length, max_height_rail_length, x_min, x_max, z_min, z_max, x, z, next_x, next_z):
            return_value = rollRollerRoll(matrix, height_map, rail_map, rail_length, current_height_rail_length, max_height_rail_length, x_min, x_max, z_min, z_max, next_x, next_z, generatorIndex, railIndex, x, z)
    ## Random direction otherwise
    else:
        return_value = choseRandomDirection(matrix, height_map, rail_map, rail_length, current_height_rail_length, max_height_rail_length, x_min, x_max, z_min, z_max, x, z, generatorIndex, railIndex, previous_x, previous_z)
    if return_value >= 1:
        rail_map[x][z] = return_value
        if generatorIndex == 1:
            return_value += 1
        else:
            return_value -= 1
    return return_value

def choseRandomDirection(matrix, height_map, rail_map, rail_length, current_height_rail_length, max_height_rail_length, x_min, x_max, z_min, z_max, x, z, generatorIndex, railIndex, previous_x, previous_z):
    global max_rail_length
    return_value = 0
    if return_value == 0 and canGenerateRail(matrix, height_map, rail_map, current_height_rail_length, max_height_rail_length, x_min, x_max, z_min, z_max, x, z, x - 1, z):
        return_value = rollRollerRoll(matrix, height_map, rail_map, rail_length, current_height_rail_length, max_height_rail_length, x_min, x_max, z_min, z_max, x - 1, z, generatorIndex, railIndex, x, z)
    if return_value == 0 and canGenerateRail(matrix, height_map, rail_map, current_height_rail_length, max_height_rail_length, x_min, x_max, z_min, z_max, x, z, x, z - 1):
        return_value = rollRollerRoll(matrix, height_map, rail_map, rail_length, current_height_rail_length, max_height_rail_length, x_min, x_max, z_min, z_max, x, z - 1, generatorIndex, railIndex, x, z)
    if return_value == 0 and canGenerateRail(matrix, height_map, rail_map, current_height_rail_length, max_height_rail_length, x_min, x_max, z_min, z_max, x, z, x + 1, z):
        return_value = rollRollerRoll(matrix, height_map, rail_map, rail_length, current_height_rail_length, max_height_rail_length, x_min, x_max, z_min, z_max, x + 1, z, generatorIndex, railIndex, x, z)
    if return_value == 0 and canGenerateRail(matrix, height_map, rail_map, current_height_rail_length, max_height_rail_length, x_min, x_max, z_min, z_max, x, z, x, z + 1):
        return_value = rollRollerRoll(matrix, height_map, rail_map, rail_length, current_height_rail_length, max_height_rail_length, x_min, x_max, z_min, z_max, x, z + 1, generatorIndex, railIndex, x, z)
    #logging.info("current rail length : {}".format(rail_length))
    if isSameLevel(height_map, x, z, previous_x, previous_z):
        if generatorIndex == 0:
            if rail_length > max_rail_length:
                max_rail_length = rail_length
        elif generatorIndex == 1:
            if rail_length == max_rail_length:
                return_value = railIndex
    if generatorIndex == 2:
        if (hasReachedEnd(height_map, rail_map, x, z, x_min, x_max, z_min, z_max, previous_x, previous_z)):
            max_rail_length += rail_length
            return_value = railIndex + rail_length - 2
    return return_value

def isNotSameLevel(height_map, x, z, previous_x, previous_z):
    return previous_x != -1 and previous_z != -1 and height_map[previous_x][previous_z] != height_map[x][z]

def isSameLevel(height_map, x, z, previous_x, previous_z):
    return previous_x != -1 and previous_z != -1 and height_map[previous_x][previous_z] == height_map[x][z]

def hasReachedEnd(height_map, rail_map, x, z, x_min, x_max, z_min, z_max, previous_x, previous_z):
    #logging.info("Trying to find ending point at coordinates: x:{}, z:{} with x_min:{}, x_max:{}, z_min:{}, z_max:{}".format(x, z, x_min, x_max, z_min, z_max))
    return ((isInBounds(x + 1, z, x_min, x_max, z_min, z_max) and rail_map[x + 1][z] == 2 and height_map[x][z] == height_map[x + 1][z])
            or (isInBounds(x, z + 1, x_min, x_max, z_min, z_max) and rail_map[x][z + 1] == 2 and height_map[x][z] == height_map[x][z + 1])
            or (isInBounds(x - 1, z, x_min, x_max, z_min, z_max) and rail_map[x - 1][z] == 2 and height_map[x][z] == height_map[x - 1][z])
            or (isInBounds(x, z - 1, x_min, x_max, z_min, z_max) and rail_map[x][z - 1] == 2 and height_map[x][z] == height_map[x][z - 1]))

def canGenerateRail(matrix, height_map, rail_map, current_height_rail_length, max_height_rail_length, x_min, x_max, z_min, z_max, x1, z1, x2, z2):
    return (not areRailsTooLongForThisHeight(current_height_rail_length, max_height_rail_length, x1, z1)
            and isInBounds(x2, z2, x_min, x_max, z_min, z_max)
            and isNextBlockSameHeightOrOneLower(height_map, x1, z1, x2, z2)
            and not isAlreadyRail(matrix, height_map, rail_map, x2, z2))

def areRailsTooLongForThisHeight(current_height_rail_length, max_height_rail_length, x, z):
    return current_height_rail_length >= max_height_rail_length

def isInBounds(x, z, x_min, x_max, z_min, z_max):
    return (x >= x_min and x <= x_max and z >= z_min and z <= z_max)

def isNextBlockSameHeightOrOneLower(height_map, x1, z1, x2, z2):
    score = height_map[x1][z1] - height_map[x2][z2]
    return score == 0 or score == 1

def isAlreadyRail(matrix, height_map, rail_map, x, z):
    return rail_map[x][z] >= 1

def cleanProperty(matrix, height_map, h_max, x_min, x_max, z_min, z_max):
    for x in range(x_min, x_max):
        for z in range(z_min, z_max):
            for y in range(height_map[x][z] + 1, h_max):
                matrix.setValue(y, x, z, AIR_ID)

def highestPointsMap(height_map, x_min, x_max, z_min, z_max):
    highestPoint = utilityFunctions.getHighestPoint(height_map, x_min, x_max, z_min, z_max)
    h_max = height_map[highestPoint[0]][highestPoint[1]]

    map = []
    for x in range(x_min, x_max):
        for z in range(z_min, z_max):
            if height_map[x][z] == h_max:
                map.append((x, z))
    return map

def getOrientation():
	return "S"
