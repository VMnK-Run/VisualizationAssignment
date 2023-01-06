import csv

import numpy as np
import requests
from config import Config


def write_csv(header, datas, file_name):
    with open(file_name, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(datas)


def get_province(lat, lon):
    key = Config.getKey()  # 一个在百度API中申请的密钥
    r = requests.get(url='http://api.map.baidu.com/reverse_geocoding/v3/',
                     params={'location': str(lat) + ',' + str(lon), 'ak': key, 'output': 'json'})
    result = r.json()
    # print(result)
    province = result['result']['addressComponent']['province']
    city = result['result']['addressComponent']['city']
    return province, city


def get_AQI(air_data):
    qua = [0, 50, 100, 150, 200, 300, 400, 500]
    Idata = [
        [0, 35, 75, 115, 150, 250, 350, 500],  # PM2.5
        [0, 50, 150, 250, 350, 420, 500, 600],  # （PM10）
        [0, 50, 150, 475, 800, 1600, 2100, 2620],  # (SO2)
        [0, 40, 80, 180, 280, 565, 750, 940],  # (NO2)
        [0, 2, 4, 14, 24, 36, 48, 60],  # （CO）
        [0, 100, 160, 215, 265, 800]  # (O3)
    ]
    k = 0
    AQI = 0
    for i in range(len(Idata)):
        T_data = air_data[i]
        T_Idata = Idata[i]
        for k in range(1, len(T_Idata)):
            if T_Idata[k] > T_data:
                break
        if k == (len(T_Idata) - 1) and T_Idata[k] < T_data:
            T_IA = T_Idata[k]
        else:
            T_IA = int(round((((qua[k] - qua[k - 1]) / (T_Idata[k] - T_Idata[k - 1])) * (
                    T_data - T_Idata[k - 1]) + qua[k - 1]) + 0.5))
        if T_IA > AQI:
            AQI = T_IA
    return AQI


def is_leap_year(year):
    if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:
        return True
    else:
        return False


def get_wind_power(u, v):
    WindPower = np.sqrt(u * u + v * v)
    return WindPower


if __name__ == '__main__':
    print(get_wind_power(np.array([3, 6]), np.array([4, 8])))
