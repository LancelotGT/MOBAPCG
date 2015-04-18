from sklearn.linear_model import LinearRegression
import numpy as np
    
class playerModel():
    ### train on level.txt file
    def __init__(self):
        levelData = open("level.txt")
        dataset = np.loadtxt(levelData, delimiter = "\t")
        self.dataset_X_train = dataset[:, 0:6]
        self.dataset_Y_train = dataset[:, 6]
        self.regr = LinearRegression()
        self.regr.fit(self.dataset_X_train, self.dataset_Y_train)
        print('Coefficients: \n', self.regr.coef_)

    def testScore(self, test_X):
        score = self.regr.predict(test_X)
        print("Predicted Score: %.2f" % np.mean(score))
        return np.mean(score)

    def getCoefficients(self):
        return self.regr.coef_

    def getTrainingX(self):
        return self.dataset_X_train

    def getTrainingY(self):
        return self.dataset_Y_train