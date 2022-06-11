#功能：本模块用于选取无向图中连接在一起的点，将相连点组成各自不同集合，不属于任何集合的单个点组成一个集合
#Date: April 15，2021
#Author: Zuguang Li
import numpy as np
import dbfread
from collections import deque
def BFS(edge_binary, start): #BFS算法
    global visited
    search_queue = deque()
    search_queue.append(start)
    wifi_set = []
    while(search_queue):    #当寻找数列非空时
        i = search_queue.popleft() #从左边取出第一个i节点
        if visited[i] == 0: #如果visited[start] == 0表示start点还未检查过
            wifi_set.append(i)
            visited[i] = 1
            for j in range(len(edge_binary)):
                if edge_binary[i][j] == 1:
                    search_queue.append(j)
    return(wifi_set)
# 将edge_binary集合中相连点组成各自不同集合，不属于任何集合的单个点组成一个集合，并保存于wifi_set_all中
def connected_sets(edge_binary):
    global visited
    visited = np.zeros(len(edge_binary), dtype='int')
    wifi_set_all = []   #存储不同的集合
    wifi_one = []   #存储与其他点不相连的点的集合
    for i in range(len(edge_binary)):  #依次遍历所有的节点
        if visited[i] == 1:
            continue
        wifi_set = BFS(edge_binary,i)
        if(wifi_set):
            if(len(wifi_set)==1):   #如果wifi_set中只有一个元素
                wifi_one.append(wifi_set[0])
            else:
                wifi_set_all.insert(0,wifi_set)
    return wifi_set_all, wifi_one

if __name__=='__main__':
    edge_binary = [[0,0,1,1,0,0,0,0,0,0],
                   [0,0,0,0,1,0,0,0,0,0],
                   [1,0,0,0,0,0,0,0,0,0],
                   [1,0,0,0,0,0,0,0,0,0],
                   [0,1,0,0,0,0,0,1,0,1],
                   [0,0,0,0,0,0,0,0,0,0],
                   [0,0,0,0,0,0,0,0,0,0],
                   [0,0,0,0,1,0,0,0,0,1],
                   [0,0,0,0,0,0,0,0,0,0],
                   [0,0,0,0,1,0,0,1,0,0]]
    wifi_set_all = connected_sets(edge_binary,len(edge_binary))
    print(wifi_set_all)