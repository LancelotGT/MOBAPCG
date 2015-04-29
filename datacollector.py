### This file is only for collecting data, will run 5 levels iteratively
import os

if __name__ == "__main__":
    numOfGame = sum(1 for line in open("player.txt"))
    print "Number of Game: ", numOfGame
    
    remainder = numOfGame % 6
    #if remainder == 0:
    #    os.system("python level0/runLevel0.py")
    if remainder == 0:
        os.system("python level1/runLevel1.py")
    elif remainder == 1:
        os.system("python level2/runLevel2.py")
    elif remainder == 2:
	os.system("python level3/runLevel3.py")
    elif remainder == 3:
        os.system("python level6/runLevel6.py")
    elif remainder == 4:
        os.system("python level4/runLevel4.py")
    elif remainder == 5:
        os.system("python level5/runLevel5.py")
