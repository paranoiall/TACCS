from collections import Counter

import pandas as pd
import numpy as np

path = "datacsv/sat300sen60.csv"
data = pd.read_csv(path, usecols=['Access Number', 'starttime', 'endtime', 'To Pass Number',
                                  'Sen_name', 'Sat_name', 'UpDown'])
data_arr = np.array(data)


def is_number(s):
    try:  # 如果能运行float(s)语句，返回True（字符串s是浮点数）
        float(s)
        return True
    except ValueError:  # ValueError为Python的一种标准异常，表示"传入无效的参数"
        pass  # 如果引发了ValueError这种异常，不做任何事情（pass：不做任何事情，一般用做占位语句）
    try:
        import unicodedata  # 处理ASCii码的包
        unicodedata.numeric(s)  # 把一个表示数字的字符串转换为浮点数返回的函数
        return True
    except (TypeError, ValueError):
        pass
    return False


def get_number(s):
    name_int = ""
    for i in range(0, len(s)):
        if is_number(s[i]) == True:
            name_int = name_int + str(s[i])
    name_int = int(name_int)
    return name_int


sat_info = Counter(data['Sat_name'])
access_res = []
for i in sat_info:
    sat_row, _ = np.where(data_arr == i)
    sat_arr = data_arr[sat_row]
    sat_circle = sat_arr[:, 3]
    for j in Counter(sat_circle):
        access = sat_arr[np.where(sat_circle == j)]
        access_start = access[np.lexsort(access[:, :2].T)][0]
        access_end = access[np.lexsort(access[:, :3].T)][-1]
        assert access_start[-1] == access_end[-1]
        access_res.append([i, j, access_start[1], access_end[2], access_start[-1]])

res = pd.DataFrame(access_res)
res.columns = ['sat_name', 'circle', 'starttime', 'endtime', 'updown']

res['sat_num'] = ''
for i in range(len(res)):
    res.loc[i, 'sat_num'] = get_number(res.loc[i, 'sat_name'])

res = res.sort_values(by=["sat_num", "circle"])
res = res.reset_index(drop=True)
res.to_csv("circle.csv", columns=['sat_name', 'circle', 'starttime', 'endtime', 'updown'])
