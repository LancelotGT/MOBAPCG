### This is the main function of the game
if __name__ == "__main__":
	numOfGame = sum(1 for line in open("player.txt"))
	print "Number of Game: ", numOfGame
	if numOfGame == 0:
		execfile("runLevel1.py")
	elif numOfGame == 1:
		execfile("runLevel2.py")
	elif numOfGame == 2:
		execfile("runLevel3.py")
	elif numOfGame == 3:
		execfile("runLevel4.py")
	elif numOfGame == 4:
		execfile("runLevel5.py")
	else:
		execfile("runversus.py")