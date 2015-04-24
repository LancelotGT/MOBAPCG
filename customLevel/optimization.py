from model.PlayerModel import SVR
import numpy as np
import random, math, copy

class SimulatedAnnealing():

    def __init__(self, model, target, startTemperature = 2000, stepsize = 1, threshold = 0.01):
        self.model = model
        self.stepsize = stepsize
        self.kmax = startTemperature
        minmaxList = model.getMinMaxList()
        self.minmaxList = minmaxList
        self.dim = model.getColumns()
        self.alpha = 1.0 * startTemperature
        s0 = np.zeros(self.dim)
        for i in range(self.dim):
            s0[i] = minmaxList[i][1] + random.random() * (minmaxList[i][0] - minmaxList[i][1])
        print "=================================="
        print "=================================="
        print "start simulated annealing: "
        print "start point: ", s0
        s = copy.deepcopy(s0)

        # define the probability function
        P = lambda e_s, e_new: math.exp(self.alpha * (e_new - e_s) / T)

        # start running simulated annealing
        T = startTemperature
        count = 0
        while T > 1:
            # print "s: ", s
            count += 1
            T = self.__temperature(T)
            s_new = self.__neighbor()
            s_score = self.__E(s)
            s_new_score = self.__E(s_new)
            # print "s score: ", s_score
            # print "s_new score: ", s_new_score

            if abs(s_score - target) < threshold:
                break
            if s_new_score > s_score:
                s = s_new
            else:
                # print "probability: ", P(s_score, s_new_score)
                if P(s_score, s_new_score) > random.random():
                    s = s_new
        
        self.s_final = s
        self.count = count
        print "Simulated annealing finished. "
        print "Total iterations: ", count
        print "Final state: ", self.s_final
        print "score: ", self.__E(self.s_final)
        print "=================================="
        print "=================================="

    def __temperature(self, T):
        return T - self.stepsize

    def __neighbor(self):
        s_next = np.zeros(self.dim)
        for i in range(self.dim):
            s_next[i] = self.minmaxList[i][1] + random.random() * (self.minmaxList[i][0] - self.minmaxList[i][1])
        return s_next

    def __E(self, s):
        return self.model.testScore(s)

    # def __P(self, e_s, e_new):
    #     print "probability: ", math.exp(self.alpha * (e_new - e_s) / self.T)
    #     return math.exp(self.alpha * (e_new - e_s) / self.T)

    def finalState(self):
        return self.s_final

if __name__ == "__main__":
    model = SVR()
    SA = SimulatedAnnealing(model, 0.4)
    s = SA.finalState()