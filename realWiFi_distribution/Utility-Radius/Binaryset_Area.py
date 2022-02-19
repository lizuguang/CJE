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
def two_distance(d, all_wifi):
    N = len(all_wifi)   
    all_inter_binary = np.full((N, N), 0)  # define one n*n all 0 matrix
    for i in range(N):
        for j in range(i + 1, N):
            two_dis = geodistance(all_wifi[i][0], all_wifi[i][1], all_wifi[j][0], all_wifi[j][1])
            if (two_dis - d < 0):
                all_inter_binary[i][j] = 1
                all_inter_binary[j][i] = 1
    return all_inter_binary

