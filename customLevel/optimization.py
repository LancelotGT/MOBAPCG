from model.PlayerModel import SVR
from model.PlayerModel import LR
import numpy as np
import random, math, copy

class SimulatedAnnealing():

    def __init__(self, model, target, startTemperature = 2000, stepsize = 1, threshold = 0.01):
        self.model = model
        self.target = target
        self.stepsize = stepsize
        self.kmax = startTemperature
        minmaxList = model.getMinMaxList()
        self.minmaxList = minmaxList
        self.dim = model.getColumns()
        # print "dimension: ", self.dim
        self.alpha = 1.0 * startTemperature
        s0 = np.zeros(self.dim)
        for i in range(self.dim):
            s0[i] = minmaxList[i][1] + random.random() * (minmaxList[i][0] - minmaxList[i][1])
        print "start simulated annealing: "
        print "start point: ", s0
        s = copy.deepcopy(s0)

        # define the probability function
        P = lambda e_s, e_new: math.exp(self.alpha * (e_new - e_s) / T)

        # start running simulated annealing
        T = startTemperature
        count = 0
        while T > 1:
            count += 1
            T = self.__temperature(T)
            s_new = self.__neighbor(s)
            s_score = self.__E(s)
            s_new_score = self.__E(s_new)
            # print "s score: ", s_score
            # print "s_new score: ", s_new_score

            if abs(s_score - target) < threshold:
                break
            if s_new_score > s_score:
                s = s_new
            else:
                if P(s_score, s_new_score) > random.random():
                    s = s_new

        self.s_final = s
        self.count = count
        print "Simulated annealing finished. "
        print "Total iterations: ", count
        print "Final state: ", self.s_final
        print "Optimized score: ", self.__E(self.s_final)
        print "============================================================"

    def __temperature(self, T):
        return T - self.stepsize

    def __neighbor(self, state):
        s_next = self.model.normalizeTest(state)
        for i in range(self.dim):
            s_next[i] = ( (self.minmaxList[i][1] + self.minmaxList[i][0]) + (2 * random.random() - 1) * (self.minmaxList[i][0] - self.minmaxList[i][1]) ) / 2
        #print "neighbor: ", s_next
        return s_next

    def __E(self, s):
        return self.model.testScore(s)

    def finalState(self):
        return self.s_final

if __name__ == "__main__":
    # model = SVR()
    model = LR()
    SA = SimulatedAnnealing(model, 0.5)
    s = SA.finalState()
