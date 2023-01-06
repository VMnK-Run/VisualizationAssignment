"""
@Author: wys
@Target:    1. 每个子文件夹都csv数据处理为23条csv记录（一省一个记录）
            2. 把每个省的各种数据做平均
            3. 每条原始数据划归到某个省
            4. 处理时以一个文件夹为单位，牢记一条 csv 是一天的数据，需要对一个月内的所有 csv 求和取平均
"""
import json
import os

import numpy as np
import pandas as pd
from tqdm import trange

from utils import get_province, get_AQI, is_leap_year, write_csv, get_wind_power

data_dir = "E:\\VisData"
prefix = "CN-Reanalysis-daily-"
out_file = "datas.csv"

location_cache_file = "location_cache_file.json"
location_cache = {}
province_name_cache = []

header = ['PM2.5(微克每立方米)', 'PM10(微克每立方米)', 'SO2(微克每立方米)', 'NO2(微克每立方米)', 'CO(毫克每立方米)',
          'O3(微克每立方米)', 'U(m/s)', 'V(m/s)', 'WindPower', 'TEMP(K)', 'RH(%)', 'PSFC(Pa)', 'AQI',
          'year', 'month', 'province']
labels = ['PM2.5', "PM10", "SO2", "NO2", "CO", "O3", "U", "V", "WindPower", "TEMP", "RH", "PSFC", "AQI"]
years = [2013, 2014, 2015, 2016, 2017, 2018]
months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
days = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def load_cache():
    if not os.path.exists(location_cache_file):
        return
    with open(location_cache_file, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    for key, value in json_data.items():
        lat = key.split(',')[0]
        lon = key.split(',')[1]
        province = value.split(',')[0]
        city = value.split(',')[1]
        location_cache[(lat, lon)] = province + ',' + city


def read_data(path):
    data_ = pd.read_csv(path)
    return data_


def process_single_file(df):
    """
    处理每一个单独的csv文件
    :param df: csv读入后的data frame
    :return: day_province_map：每个省份当天的各地平均
    """
    length = len(df)
    PM2_5 = np.array(df["PM2.5(微克每立方米)"])
    PM10 = np.array(df[" PM10(微克每立方米)"])
    SO2 = np.array(df[" SO2(微克每立方米)"])
    NO2 = np.array(df[" NO2(微克每立方米)"])
    CO = np.array(df[" CO(毫克每立方米)"])
    O3 = np.array(df[" O3(微克每立方米)"])
    U = np.array(df[" U(m/s)"])
    V = np.array(df[" V(m/s)"])
    WindPower = get_wind_power(U, V)
    TEMP = np.array(df[" TEMP(K)"])
    RH = np.array(df[" RH(%)"])
    PSFC = np.array(df[" PSFC(Pa)"])
    Lat = np.array(df[" lat"])
    Lon = np.array(df[" lon"])
    province_num_cache = {}
    day_province_map = {}
    for i in range(length):
        if location_cache.get((str(Lat[i]), str(Lon[i]))):
            province = location_cache.get((str(Lat[i]), str(Lon[i]))).split(',')[0]
        else:
            province, city = get_province(Lat[i], Lon[i])
            location_cache[str(Lat[i]) + ',' + str(Lon[i])] = province + ',' + city
            f = open('cache.txt', 'a', encoding='utf-8')
            f.write(str(Lat[i]) + ',' + str(Lon[i]) + ';' + province + ',' + city + '\n')
            f.close()
        if province_num_cache.get(province):
            province_num_cache[province] = province_num_cache.get(province) + 1
        else:
            province_num_cache[province] = 1
        if province_name_cache.count(province) == 0:
            province_name_cache.append(province)
        air_data = np.array([PM2_5[i], PM10[i], SO2[i], NO2[i], CO[i], O3[i]])
        AQI = get_AQI(air_data)
        if day_province_map.get(province):
            temp_map = day_province_map.get(province)
            temp_map["PM2.5"] = temp_map.get("PM2.5") + PM2_5[i]
            temp_map["PM10"] = temp_map.get("PM10") + PM10[i]
            temp_map["SO2"] = temp_map.get("SO2") + SO2[i]
            temp_map["NO2"] = temp_map.get("NO2") + NO2[i]
            temp_map["CO"] = temp_map.get("CO") + CO[i]
            temp_map["O3"] = temp_map.get("O3") + O3[i]
            temp_map["U"] = temp_map.get("U") + U[i]
            temp_map["V"] = temp_map.get("V") + V[i]
            temp_map["WindPower"] = temp_map.get("WindPower") + WindPower[i]
            temp_map["TEMP"] = temp_map.get("TEMP") + TEMP[i]
            temp_map["RH"] = temp_map.get("RH") + RH[i]
            temp_map["PSFC"] = temp_map.get("PSFC") + PSFC[i]
            temp_map["AQI"] = temp_map.get("AQI") + AQI
        else:
            single_map = {"PM2.5": PM2_5[i], "PM10": PM10[i], "SO2": SO2[i], "NO2": NO2[i], "CO": CO[i],
                          "O3": O3[i], "U": U[i], "V": V[i], "WindPower": WindPower[i],
                          "TEMP": TEMP[i], "RH": RH[i], "PSFC": PSFC[i], "AQI": AQI}
            day_province_map[province] = single_map
    if not os.path.exists(location_cache_file):
        with open(location_cache_file, 'w', encoding='utf-8') as f:
            json.dump(location_cache, f, ensure_ascii=False)
    # 每个省对各地取平均
    for province in province_name_cache:
        for label in labels:
            day_province_map[province][label] = day_province_map[province].get(label) / province_num_cache[province]
    return day_province_map


# 应该返回23个省的各自一条记录
def process_month_dir(year, month):
    """
    处理每一个子文件夹，即处理某一月的数据
    :param year: 年份
    :param month: 月份
    :return: 该月的每个省的各自一条记录
    """
    year_str = str(year)
    if month < 10:
        month_str = '0' + str(month)
    else:
        month_str = str(month)
    datas = []
    res = []
    print("\n" + year_str + month_str)
    for day in trange(1, days[month] + 1):
        if day < 10:
            day_str = '0' + str(day)
        else:
            day_str = str(day)
        data_sub_dir = "\\" + year_str + month_str + "\\"
        file_name = "CN-Reanalysis-daily-" + year_str + month_str + day_str + "00.csv"
        df = read_data(data_dir + data_sub_dir + file_name)
        day_province_map = process_single_file(df)
        datas.append(day_province_map)
    for province in province_name_cache:
        single_record = {}
        for day in range(days[month]):
            day_province_map = datas[day]
            temp_map = day_province_map.get(province)
            if single_record.get("province"):
                for label in labels:
                    single_record[label] = single_record.get(label) + temp_map.get(label)  # 累加该月数据
            else:  # 该省的第一天数据
                for label in labels:
                    single_record[label] = temp_map.get(label)
                    single_record["year"] = year
                    single_record["month"] = month
                    single_record["province"] = province
        for label in labels:
            single_record[label] = single_record.get(label) / days[month]  # 对该月做平均
        res.append(single_record)
    return res


# 思路：先对每个省一天中每个地点做平均，然后对每个月的值做平均
def main():
    load_cache()
    all_datas = []
    for year in years:
        if is_leap_year(year):
            days[2] = 29
        else:
            days[2] = 28
        for month in months:
            month_datas = process_month_dir(year, month)
            for month_data in month_datas:
                all_datas.append(month_data)

    csv_data = []
    for single_record in all_datas:
        single_data = []
        if len(single_record.get("province")) == 0:
            continue
        first_char = single_record.get("province")[0]
        if not '\u4e00' <= first_char <= '\u9fff':
            continue
        for label in labels:
            single_data.append(single_record.get(label))
        single_data.append(single_record.get("year"))
        single_data.append(single_record.get("month"))
        single_data.append(single_record.get("province"))
        csv_data.append(single_data)
    write_csv(header, csv_data, out_file)


if __name__ == '__main__':
    main()
