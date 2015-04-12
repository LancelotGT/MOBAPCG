numOfGame = sum(1 for line in open("player.txt")) - 1
print "numOfGame: ", numOfGame
if numOfGame == 0:
	execfile("runLevel1.py")
elif numOfGame == 1:
	execfile("runLevel2.py")
elif numOfGame == 2:
	execfile("runLevel3.py")
else:
	execfile("runversus.py")