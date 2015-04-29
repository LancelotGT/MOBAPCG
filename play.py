### This is the main function of the game
### It will first let the player to play 6 pre-defined levels and give the customized level.
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
	elif numOfGame == 5:
		os.system("python level6/runLevel6.py")
	else:
		os.system("python customLevel/runCustom.py")