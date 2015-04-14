from sklearn.linear_model import LinearRegression
import numpy as np
### parse player.txt to get the training dataset
levelData = open("level.txt")
dataset = np.loadtxt(levelData, delimiter = "\t")
print(dataset.shape)
print(dataset)

dataset_X_train = dataset[:, 0:5]
dataset_Y_train = dataset[:, 5]
print(dataset_X_train)
print(dataset_Y_train)

regr = LinearRegression()
regr.fit(dataset_X_train, dataset_Y_train)

print('Coefficients: \n', regr.coef_)

test_X = [4, 15, 15, 7.5, 75]
print("Predicted Score: %.2f" % np.mean((regr.predict(test_X))))