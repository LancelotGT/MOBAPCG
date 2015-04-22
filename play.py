### This is the main function of the game
import os

if __name__ == "__main__":
	numOfGame = sum(1 for line in open("player.txt"))
	print "Number of Game: ", numOfGame
	if numOfGame == 0:
		os.system("python level1/runLevel1.py")
	elif numOfGame == 1:
		os.system("python level2/runLevel2.py")
	elif numOfGame == 2:
		os.system("python level3/runLevel3.py")
	elif numOfGame == 3:
		os.system("python level4/runLevel4.py")
	elif numOfGame == 4:
		os.system("python level5/runLevel5.py")
	else:
		os.system("python customLevel/runCustom.py")