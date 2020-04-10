import random
import numpy as np
import heapq
import math
from utils import roundl
    
def ftpl(e, epsilon, delta, k):
    iters = 4 * e.n**2 * max(e.A.k, e.B.k)/(epsilon**2)
    for r in range(math.ceil(iters)):
        delta_array_B = np.greater(delta * np.ones(e.n), abs(np.array(e.B.X) - np.mean(e.B.ftpl_history, axis=0)))
        delta_array_A = np.greater(delta * np.ones(e.n), abs(np.array(e.A.X) - np.mean(e.A.ftpl_history, axis=0)))
        if r > 1 and all(delta_array_A) and all(delta_array_B):
            print("breaking early at ", r)
            break 
        if r % 500 == 0:
            print("\nFTPL Iteration {} of {}, Budget {}".format(r, iters, k))
            print("current mean: ", e.calculate_mean())
            print("remaining unconverged entries: ({}, {})".format(e.n-sum(delta_array_A), e.n-sum(delta_array_B)))
        ftpl_iter(e, e.A, r, epsilon)
        ftpl_iter(e, e.B, r, epsilon)
        e.update_network()

        # print('RESULT', e.calculate_mean(), e.theta_0)
    # print("\nEquilibrium after {} iters: ".format(iters))

    # print("Original theta: {}".format(e.theta))
    # print("Final theta: {}".format(e.theta_0))
    print("Original Mean: {}".format(sum(e.theta)))
    print("Final Mean: {}".format(e.calculate_mean()))
    for cand in [e.A, e.B]:
        cand.X = np.mean(cand.ftpl_history, axis=0)
        print("Final X{}: \t{}".format(cand.id, cand.X))

def ftpl_iter(e, cand, r, epsilon):
    opp = cand.opp
    perturb = [random.uniform(0, 1/epsilon) for _ in range(e.n)]
    if r:
        X_opp = np.mean(opp.ftpl_history[:r], axis=0) + np.multiply(1/r, perturb)
    else:
        X_opp = np.zeros(e.n)
    X_opp = [1 if x > 1 else x for x in X_opp]
    X = mov_oracle(e, cand, X_opp)
    cand.ftpl_history.append(X)
    cand.X = X
    # print("best X_" + cand.id + ":", roundl(X, 2))

def mov_oracle(e, cand, X_opp):
    X = np.zeros(e.n)
    remaining = cand.k
    score = cand.marginal_payoff(e, X_opp)
    heap = [(-(score[i]), i) for i in range(len(score))]
    heapq.heapify(heap)
    while remaining > 0 and len(heap):
        if len(heap):
            x_score, x = heapq.heappop(heap)
            max_X = cand.max_expenditure(e, X_opp, x)
            X[x] = min(max_X, remaining)
            assert X[x] >= 0
        remaining -= X[x]
    return X
