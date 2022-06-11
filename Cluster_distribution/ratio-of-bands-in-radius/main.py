# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import sympy
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import Wifi_Set
import Binaryset_Area
#path loss model on 3.5GHz
# 得出的结果：每个集合当中每种颜色所对应的顶点数
#the process of graph coloring algorithm is presented as following
def graph_coloring(binary_set_area, node_sets):
    edge_num_all = [sum(e) for e in binary_set_area]    #this represents the number of every point's edges
    #color_num_all = []  # 每个集合所需颜色数的总数组
    color_all = []  # 每个集合内每个顶点所对应的颜色的总数组
    for i in range(len(node_sets)):
        color_num = 0   #表示一个集合内所需的颜色总数
        disabled = []   #表示已经被染色的点
        color = []  # initiate the list color, and record the number of color required for each vertex(顶点)
        edge_num = [] #this represents the number of calculated point's edges
        points = node_sets[i]   # points表示相连在一起的点的集合，node_sets是由多个集合组成的数组
        edge = np.zeros((len(points),len(points)), dtype=int)   # edge表示一个集合内的干扰图
        for m in range(len(points)):
            color.append(0) # 初始化每个顶点无颜色为0
            edge_num.append(edge_num_all[points[m]])
            for z in range(m+1,len(points)):
                if (binary_set_area[points[m]][points[z]]==1):
                    edge[m][z] = 1
                    edge[z][m] = 1
        for k in range(len(points)):
            #get the maximum edge number of the vertex
            #maxEdgePoint为边最多的点的序号
            maxEdgePoint = [n for n in range(len(points)) if edge_num[n] == max(edge_num) and edge_num[n] != 0]
            #print('max:'+str(maxEdgePoint))
            #ergodi the maximum edge number
            for p in maxEdgePoint:
                if p not in disabled:
                    #select the point having maximum edge number and the point have not been colored
                    color[p] = color_num + 1
                    disabled.append(p)
                    edge_num[p] = 0
                    #temp represents the next point colored
                    temp = edge[p]
                    for q in range(len(points)):
                        if q not in disabled:
                            if (temp[q] ==0):
                                color[q] = color_num + 1
                                disabled.append(q)
                                edge_num[q] = 0
                                temp = [x + y for (x, y) in zip(edge[q], temp)]
                    color_num = color_num + 1
            if 0 not in color:
                break
        # 前面的color数组表示集合中各顶点对应的信道
        color = Counter(color)  # 计算每个集合当中各颜色所对应的顶点的数量
        color_all.append(color)
        #color_num_all.append(color_num)
    return color_all

def figure(rate_node_my, rate_node_oth, d_set):
    font1 = {'family': 'Times New Roman',
             'weight': 'normal',
             'size': 13,
             }
    font2 = {'family': 'Times New Roman',
             'weight': 'normal',
             'size': 13,
             }
    ax.tick_params(labelsize=12)
    # -------------两种算法能够支持的用户比例----------------------------------
    ax.set_ylabel(r'Ratio of channel reused $q$', font1)
    x = d_set
    #ax.set_title('The bandwidth demand')
    ax.set_xlabel(r"radius of node's required area $r ( km )$", font1)
    #plt.savefig('fix.eps', dpi=300)  # 指定分辨率保存
    lns1 = ax.plot(x, rate_node_my, ls='-', color='orangered', marker="o", markersize=10, label= r"$q$ in proposed algorithm")
    lns2 = ax.plot(x, rate_node_oth, ls='-', color='blue', marker="^", markersize=10, label= r"$q$ in WIF scheme")
    ax.set_ylim(400, 520, 20)
    '''x_ticks = np.arange(10, 60, 10)
    plt.xticks(x_ticks)'''
    lns = lns1 + lns2
    labs = [l.get_label() for l in lns]
    ax.legend(lns, labs, loc = 0, prop=font2, framealpha=0.8)
    ax.grid()
    ax.margins(0) #让图坐标两边无间隔
    plt.savefig('virtual_2.eps', dpi=300)
    plt.show()

def rate_node(N):
    rate_node_my = []  # 所提出的算法所对应的获得信道的节点占总节点数的比例
    rate_node_oth = [] # 对比算法对应的获得信道的节点占总节点数的比例
    nodeset_num = []   #正方形内集合的数量
    Num_points = 5000  #节点总数
    d_set = []  # 节点保护区域的半径
    time = 100
    for d1 in range(8, 15, 1):
        d = d1 * 0.1
        node_num_loop_1 = 0
        node_num_loop_2 = 0
        for looptime in range(time):
            lists_all = [] #对比算法中所有信道对应的能支持的用户数
            binary_set_area = Binaryset_Area.connected_point(Num_points, d)  # 获取在所规定正方形区域内的点的干扰图
            # node_sets表示所规定正方形区域内相连点的集合，node_one表示没有相连点的集合
            node_sets, node_one = Wifi_Set.connected_sets(binary_set_area)
            node_one_num = len(node_one)
            # color_all表示每个集合内每种颜色对应顶点数量的总数组,比如[[1: 3, 2: 3, 3: 1, 4: 1],[1: 1, 2: 4]]
            color_all = graph_coloring(binary_set_area, node_sets)
            node_lice_num = np.zeros((len(color_all),), dtype=np.int)  # 每个集合中获得信道的node总数
            for i in range(len(color_all)):
                # ------------------本算法计算能支持的用户总数----------------------------------------------------------------
                color_one = color_all[i]  # color_one表示color_all中的一个相连点集合
                lists = list(color_one.values())
                lists = sorted(lists, reverse=True)  # 对字lists列表排序（倒序）
                if max(color_one) > N:  # 如果需要的信道数大于N，则说明信道不够分，需选出前N个信道下支持的最多的点
                    for j in range(N):  # 将前N个信道下的用户数相加
                        node_lice_num[i] += lists[j]
                else:  # 如果所需的信道数小于等于N，只需将所有信道下的用户数相加
                    node_lice_num[i] += sum(lists)
                # ---------------------------------------------------------------------------------------------------------
                # *****************************对比算法计算所能支持的用户总数*************************************************
                lists_all.extend(lists)
            lists_all.append(node_one_num)
            lists_all.sort(reverse=True) #对list_all降序排列
            node_lice_num2 = 0 # 表示对比算法能满足用户数的总数
            if len(lists_all) > N:  # 如果需要的信道数大于N，则说明信道不够分，需选出前N个信道下支持的最多的点
                for m in range(N):  # 将前N个信道下的用户数相加
                    node_lice_num2 += lists_all[m]
            else:  # 如果所需的信道数小于等于N，只需将所有信道下的用户数相加
                node_lice_num2 += sum(lists_all)
            node_num_loop_1 += sum(node_lice_num) + node_one_num
            node_num_loop_2 += node_lice_num2
        # ************************************************************************************************************
        rate_node_my.append((node_num_loop_1 / time) / N)
        rate_node_oth.append((node_num_loop_2 / time) / N)
        d_set.append(d)
        nodeset_num.append(len(color_all))
    return rate_node_my, rate_node_oth, d_set
# The process is very difficult, so it's annotated in Chinese
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    N = 10 # N指信道总数
    rate_node_my, rate_node_oth, d_set = rate_node(N)
    fig, ax = plt.subplots()
    print("my:", rate_node_my)
    print("other:", rate_node_oth)
    figure(rate_node_my, rate_node_oth, d_set)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
