# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import sympy
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from collections import Counter
import re
import Wifi_Set
import Binaryset_Area
#path loss model on 3.5GHz
def path_loss():
    d0 = 1  # the reference point
    PL_d0 = 15  # the path loss on reference point d0, dB
    P_t = 15  # the transmit power, dBm
    P_l = -96  # the maximum receive power from other GAA users is allowed if there is no inference
    n = 3.6  # path loss exponent
    d = sympy.symbols("d")
    PL_d =PL_d0 + 10*n*sympy.log(d/d0, 10) #the path loss model
    d1 = sympy.solve([P_t - PL_d - P_l], [d])
    return d1[d]    #when the receive power is equal to P_l, the distance is d1[d]

# 得出的结果：每个集合当中每种颜色所对应的顶点数
#the process of graph coloring algorithm is presented as following
def graph_coloring(binary_set_area, wifi_sets):
    edge_num_all = [sum(e) for e in binary_set_area]    #this represents the number of every point's edges
    #color_num_all = []  # 每个集合所需颜色数的总数组
    color_all = []  # 每个集合内每个顶点所对应的颜色的总数组
    for i in range(len(wifi_sets)):
        color_num = 0   #表示一个集合内所需的颜色总数
        disabled = []   #表示已经被染色的点
        color = []  # initiate the list color, and record the number of color required for each vertex(顶点)
        edge_num = [] #this represents the number of calculated point's edges
        points = wifi_sets[i]   # points表示相连在一起的点的集合，wifi_sets是由多个集合组成的数组
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

def figure(rate_wifi_my, rate_wifi_oth, wifi_density, wifiset_num):
    font1 = {'family': 'Times New Roman',
             'weight': 'normal',
             'size': 18,
             }
    font2 = {'family': 'Times New Roman',
             'weight': 'normal',
             'size': 13,
             }
    ax.tick_params(labelsize=12)
    # -------------两种算法能够支持的用户比例----------------------------------
    ax.set_ylabel(r'Ratio of channel reused $q$', font1)
    x = []
    for i in range(1,6):
        x.append(i * 10)
    #ax.set_title('The bandwidth demand')
    ax.set_xlabel(r'Area Width $h \ (km)$', font1)
    #plt.savefig('fix.eps', dpi=300)  # 指定分辨率保存
    lns1 = ax.plot(x, rate_wifi_my, ls='-', color='orangered', marker="o", markersize=10, label= r"$q$ in proposed algorithm")
    lns2 = ax.plot(x, rate_wifi_oth, ls='-', color='blue', marker="^", markersize=10, label= r"$q$ in WIF scheme")
    ax.set_ylim(0, 200, 40)
    x_ticks = np.arange(10, 60, 10)
    plt.xticks(x_ticks)
    lns = lns1 + lns2
    labs = [l.get_label() for l in lns]
    ax.legend(lns, labs, loc = 0, prop=font2, framealpha=0.8)
    ax.grid()
    ax.margins(0)
    plt.savefig('fix2.eps', dpi=300)
    plt.show()

def rate_wifi(d, N):
    all_inter_binary, all_wifi = Binaryset_Area.two_distance(d, filename)  # 通过经纬度坐标计算两点间的距离
    rate_wifi_my = []  # 所提出的算法所对应的获得信道的节点占总节点数的比例
    rate_wifi_oth = [] # 对比算法对应的获得信道的节点占总节点数的比例
    wifi_density = []  # 正方形下用户的密度
    wifiset_num = []   #正方形内集合的数量
    for stepwidth in range(1, 6):  # 初始话的步长为1，每增加1步长，正方形边长增加10km，正方形的初始化边长为10km stepwidth = 1~5
        lists_all = [] #对比算法中所有信道对应的能支持的用户数
        binary_set_area = Binaryset_Area.getGAA(all_wifi, stepwidth, all_inter_binary)  # 获取在所规定正方形区域内的点的干扰图
        wifi_num = len(binary_set_area)  # 正方形区域内wifi的总数
        # wifi_sets表示所规定正方形区域内相连点的集合，wifi_one表示没有相连点的集合
        wifi_sets, wifi_one = Wifi_Set.connected_sets(binary_set_area)
        wifi_one_num = len(wifi_one)
        # color_all表示每个集合内每种颜色对应顶点数量的总数组,比如[[1: 3, 2: 3, 3: 1, 4: 1],[1: 1, 2: 4]]
        color_all = graph_coloring(binary_set_area, wifi_sets)
        wifi_lice_num = np.zeros((len(color_all),), dtype=np.int)  # 每个集合中获得信道的wifi总数
        for i in range(len(color_all)):
            # ------------------本算法计算能支持的用户总数----------------------------------------------------------------
            color_one = color_all[i]  # color_one表示color_all中的一个相连点集合
            sorted(color_one.items(), key=lambda item: item[1], reverse=True)  # 对字典型color列表按照其values值排序（倒序）
            lists = list(color_one.values())
            if max(color_one) > N:  # 如果需要的信道数大于N，则说明信道不够分，需选出前N个信道下支持的最多的点
                for j in range(N):  # 将前N个信道下的用户数相加
                    wifi_lice_num[i] += lists[j]
            else:  # 如果所需的信道数小于等于N，只需将所有信道下的用户数相加
                wifi_lice_num[i] += sum(lists)
            # ---------------------------------------------------------------------------------------------------------
            # *****************************对比算法计算所能支持的用户总数*************************************************
            lists_all.extend(lists)
        lists_all.append(wifi_one_num)
        lists_all.sort(reverse=True) #对list_all降序排列
        wifi_lice_num2 = 0 # 表示对比算法能满足用户数的总数
        if len(lists_all) > N:  # 如果需要的信道数大于N，则说明信道不够分，需选出前N个信道下支持的最多的点
            for m in range(N):  # 将前N个信道下的用户数相加
                wifi_lice_num2 += lists_all[m]
        else:  # 如果所需的信道数小于等于N，只需将所有信道下的用户数相加
            wifi_lice_num2 += sum(lists_all)
        # ************************************************************************************************************
        rate_wifi_my.append((sum(wifi_lice_num) + wifi_one_num) / 12)
        rate_wifi_oth.append(wifi_lice_num2 / 12)
        wifi_density.append(wifi_num / (stepwidth * 10)**2)
        wifiset_num.append(len(color_all))
    return rate_wifi_my, rate_wifi_oth, wifi_density, wifiset_num
# The process is very difficult, so it's annotated in Chinese
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    N = 12 # N指信道总数
    d = round(float(path_loss()), 3)
    rate_wifi_my, rate_wifi_oth, wifi_density, wifiset_num = rate_wifi(d, N)
    fig, ax = plt.subplots()
    figure(rate_wifi_my, rate_wifi_oth, wifi_density, wifiset_num)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
