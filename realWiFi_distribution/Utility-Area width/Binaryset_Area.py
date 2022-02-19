import numpy as np
import dbfread
from math import radians, cos, sin, asin, sqrt

# 从.DBF文件里读取WiFi坐标的经纬度，保存至all_wifi数组中
def readDbfFile(filename):
    all_wifi = []
    i = 0
    table = dbfread.DBF(filename, encoding='GBK', char_decode_errors='ignore', load=True)
    for record in table:
        all_wifi.append([])
        lon = record['lon']
        lat = record['lat']
        all_wifi[i].append(lon)
        all_wifi[i].append(lat)
        i += 1
    return all_wifi

# 通过经纬度坐标计算两点间的距离
def geodistance(lng1, lat1, lng2, lat2):
    lng1, lat1, lng2, lat2 = map(radians, [float(lng1), float(lat1), float(lng2), float(lat2)])  # 经纬度转换成弧度
    dlon = lng2 - lng1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    distance = 2 * asin(sqrt(a)) * 6371 * 1000  # 地球平均半径，6371km
    distance = round(distance, 3)
    return distance

# 计算all_wifi数组中所有点之间是否存在干扰，并保存至all_inter_binary中
def two_distance(d, filename):
    all_wifi = readDbfFile(filename)    # 从.DBF文件里读取WiFi坐标的经纬度
    N = len(all_wifi)   
    all_inter_binary = np.full((N, N), 0)  # define one n*n all 0 matrix
    for i in range(N):
        for j in range(i + 1, N):
            two_dis = geodistance(all_wifi[i][0], all_wifi[i][1], all_wifi[j][0], all_wifi[j][1])
            if (two_dis - d < 0):
                all_inter_binary[i][j] = 1
                all_inter_binary[j][i] = 1
    return all_inter_binary, all_wifi

#获得在正方形区域内的干扰图，保存至binary_set_area中
def getGAA(all_wifi, width, all_inter_binary):
    in_area = []  # in_area表示在边长为width的正方形中的点（序号）的集合
    j = 0  # 序号0表示第一个点
    for i in all_wifi:  # 遍历所有的wifi节点，寻找在正方形内的点集合，保存在in_area内
        # 整个区域：lon: (-74.245 ~ -73.714), lat: (40.509 ~ 40.904)
        if (-73.9795 - width * 0.0531) < i[0] < (-73.9795 + width * 0.0531) and (40.7065 - width * 0.0395)< i[1] < (40.7065 + width * 0.0395):  # 判断点是否在正方形内
            in_area.append(j)  # in_area存放的是在正方形内的点的序号
        j += 1
    l = len(in_area)
    binary_set_area = np.full((l, l), 0)  # 用于存在正方形内点的干扰矩阵，set_in_area为二进制矩阵
    for m in range(l):
        for n in range(l):
            binary_set_area[m][n] = all_inter_binary[in_area[m]][in_area[n]]
    return binary_set_area

def binaryset_in_area(filename, stepwidth, d):
    all_wifi = readDbfFile(filename)  # 表示所有wifi经纬度的数组
    all_inter_binary = two_distance(d, all_wifi)
    binary_set_area = getGAA(all_wifi, stepwidth, all_inter_binary)
    return binary_set_area, all_inter_binary


if __name__ == '__main__':
    d = 460
    filename = 'E:\\pythonprojects\\WiFi\\geo.DBF'
    all_inter_binary, all_wifi = two_distance(d, filename)    # 通过经纬度坐标计算两点间的距离
