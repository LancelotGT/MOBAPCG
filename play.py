### This is the main function of the game
if __name__ == "__main__":
	numOfGame = sum(1 for line in open("player.txt"))
	print "Number of Game: ", numOfGame
	if numOfGame == 0:
		execfile("./level1/runLevel1.py")
	elif numOfGame == 1:
		execfile("./level2/runLevel2.py")
	elif numOfGame == 2:
		execfile("./level3/runLevel3.py")
	elif numOfGame == 3:
		execfile("./level4/runLevel4.py")
	elif numOfGame == 4:
		execfile("./level5/runLevel5.py")
	else:
		execfile("runversus.py")