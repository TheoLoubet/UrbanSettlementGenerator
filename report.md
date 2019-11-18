# Advancement report on Generative Design in Minecraft

## Lightpath
To add lighting to the path, I use 16 blocks from the path to compute the center of mass of these block and if the coordinates correspond to a valid block, I put a light template on this position, if it's not, I find a valid block next to it the coordinate and put the light on it, if no good position are find, I try to find one directly on the path.

- I put the light management in the second for loop (the one in which we put the ladder) to get a better result
- The building of the path now update the height map so that the light are not sometimes put in the ground
	-> new bug, sometime the ladder are build under a block and are not usable
- Added a check to see if the light is not being built on the location of a ladder

## Garden
To add garden to the house, I find the opposite orientation of the door of the house, and an other side that has the most space until the end of the house lot. I then randomly get a point from this side and connect with fences this point to the corner of the house on the other side, by building fences until the border of the house lot.

- fence door added to one side of the garden
- the garden is not build if one side would be built right next to the wall of the house
-> put things in garden ?


## Detect water

with a slightly modified A* algorithm, that doesn't take into account water or height, we can generate a simplified path to see if it would be interesting to go on water. When this simplified path is generated, we go through it and we find the coordinates of the points where it goes on water if it does so we can build bridges to connect these points. Then if there are any bridges throughout the path we divide the path so that the bridge is not part of it anymore (so no lantern build on the bridge and no problem with the height of the bridge when we call the A* algorithm that cares about height) and we then generate a new path that connect everything using the non-modified A* algorithm.

-> try to simplify the second a* even more
-> clean the base of the bridge
-> fix the weird thing that happen at the start (maybe a second for loop ?)