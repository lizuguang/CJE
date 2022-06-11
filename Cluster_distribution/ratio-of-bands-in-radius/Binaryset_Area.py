from sklearn.datasets._samples_generator import make_blobs
import numpy as np
import matplotlib.pyplot as plt
def connected_point(N, d):
    ##产生随机数据的中心
    centers = [[10, 10], [30, 10], [10, 30], [30, 30]]
    ##生产数据
    X, _ = make_blobs(n_samples = N, n_features = 2, centers=centers, cluster_std= 6,
                      random_state= 0)
    edge_binary = np.full((N,N),0)  #define one n*n all 0 matrix
    for i in range(N):
        for j in range(i+1, N):
            two_dis = ((X[i, 0]-X[j, 0])**2 + (X[i, 1]- X[j, 1])**2)**0.5    #calculate the distance between two points of each other
            if (two_dis- d <= 0):
                edge_binary[i][j] = 1
                edge_binary[j][i] = 1
    return edge_binary
'''centers = [[10, 10], [30, 10], [10, 30], [30, 30]]
##生产数据
X, Y = make_blobs(n_samples = 2000, n_features = 2, centers=centers, cluster_std=6,
                  random_state= 0)
plt.scatter(X[:, 0], X[:, 1], c = Y)
plt.show()'''