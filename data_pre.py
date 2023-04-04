from collections import Counter
import pandas as pd
import numpy as np

path = "datacsv/sat1000sen300fac10.csv"
cols = ['Access Number', 'starttime', 'endtime', 'Duration', 'To Pass Number', 'Fac_name', 'Sen_name', 'Sat_name',
        'UpDown']

data = pd.read_csv(path, usecols=cols)
data_arr = np.array(data)

# 卫星与天线能力
ability = np.random.rand(300, 61) < 0.8
assert np.any(ability, axis=0).all() and np.any(ability, axis=1).all(), "卫星或天线无意义"

trash = []
for i, access in enumerate(data_arr):
    sat = int(access[6][3:])
    sen = int(access[5][3:])
    if access[3] < 120 or not ability[sat][sen]:
        trash.append(i)

data_arr = np.delete(data_arr, trash, axis=0)
data_ability = pd.DataFrame(data_arr, columns=cols)
data_ability.to_csv("access.csv")
print("Access get!")

# 总结圈信息
sat_info = Counter(data['Sat_name'])
sen_info = Counter(data['Sen_name'])

access_res = []
index = []
for i in sat_info:
    sat_row, _ = np.where(data_arr == i)
    sat_arr = data_arr[sat_row]
    sat_circle = sat_arr[:, 4]
    for j in Counter(sat_circle):
        access = sat_arr[np.where(sat_circle == j)]
        access_start = access[np.lexsort(access[:, :2].T)][0]
        access_end = access[np.lexsort(access[:, :3].T)][-1]
        assert access_start[-1] == access_end[-1]
        access_res.append([i, j, access_start[1], access_end[2], access_start[-1], int(i[3:])])

print("Circle get!")

res = pd.DataFrame(access_res)
res.columns = ['sat_name', 'circle', 'starttime', 'endtime', 'updown', "sat_num"]

res = res.sort_values(by=["sat_num", "circle"])
res = res.reset_index(drop=True)
res.to_csv("circle.csv", columns=['sat_name', 'circle', 'starttime', 'endtime', 'updown'])
