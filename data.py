import time
import random
from collections import Counter

import numpy as np
import pandas as pd


class datacoder:
    def __init__(self, path):
        # data = pd.read_csv(path, usecols=['starttime', 'endtime', 'duration', 'circle', 'sen_name', 'sat_name'])
        data = pd.read_csv(path, usecols=['starttime', 'endtime', 'Duration', 'To Pass Number', 'Sen_name', 'Sat_name'])

        self.sat_info = Counter(data['Sat_name'])
        self.sen_info = Counter(data['Sen_name'])

        sat_num = len(self.sat_info)
        sen_num = len(self.sen_info)

        # 名列表 序号->名
        self.sat_name = [x for x in self.sat_info]
        self.sen_name = [x for x in self.sen_info]

        # 卫星需求 待排序
        # self.req = np.random.randint(low=2, high=4, size=sat_num, dtype=int)
        self.req = np.array([3]*sat_num, dtype=int)


        # 卫星与天线关系 待排序
        self.ability = np.random.rand(sat_num, sen_num) < 0.8

        self.time_start = np.inf
        self.data_arr = np.array(data)
        self.data_init()

        self.data_arr = np.insert(self.data_arr, 0, np.arange(1, self.data_arr.shape[0] + 1), axis=1)

        sat_max = self.sat_info.most_common()
        sen_max = self.sen_info.most_common()

        # sat字典，卫星序号+相对弧段号->总弧段号
        self.sat_dict = np.zeros((sat_num, sat_max[0][1]), dtype=int)
        # sen字典 总弧段号:[天线序号, 相对弧段号, 开始时间, 结束时间]
        self.sen_dict = {}

        # 冲突矩阵 数量*最多弧段数量*最多弧段数量
        self.sat_clash = np.zeros((sat_num, sat_max[0][1], sat_max[0][1]), dtype=bool)
        self.sen_clash = np.zeros((sen_num, sen_max[0][1], sen_max[0][1]), dtype=bool)

    def data_init(self):
        # for i in range(self.data_arr.shape[0]):
        #     time_array_start = time.strptime(self.data_arr[i][0], "%Y/%m/%d %H:%M:%S.%f")
        #     time_array_end = time.strptime(self.data_arr[i][1], "%Y/%m/%d %H:%M:%S.%f")
        #     self.data_arr[i][0] = time.mktime(time_array_start)
        #     self.data_arr[i][1] = time.mktime(time_array_end)
        #     self.time_start = min(self.time_start, self.data_arr[i][0], self.data_arr[i][1])

        self.time_start = min(np.min(self.data_arr[:, 0]), np.min(self.data_arr[:, 1]))

        for i in range(self.data_arr.shape[0]):
            self.data_arr[i][0] -= self.time_start
            self.data_arr[i][1] -= self.time_start

    def sat_matrix(self):
        # 完成冲突矩阵
        for i in range(len(self.sat_info)):

            # i卫星所有弧段按开始时间排序
            row, _ = np.where(self.data_arr == self.sat_name[i])
            # sat_clash_i = sorted(self.data_arr[row].tolist(), key=lambda x: x[1])
            sat_row = self.data_arr[row]
            sat_clash_i = sat_row[np.lexsort(sat_row[:, :2].T)]

            for item_i in range(len(row)):
                # 更新sat字典
                self.sat_dict[i][item_i] = sat_clash_i[item_i][0]

                # 更新冲突矩阵
                # 对角线
                self.sat_clash[i][item_i][item_i] = True
                # 非对角线
                for item_j in range(item_i + 1, len(row)):
                    # 不在同一圈
                    if abs(sat_clash_i[item_i][4] - sat_clash_i[item_j][4])>1:
                        self.sat_clash[i][item_i][item_j] = True
                        self.sat_clash[i][item_j][item_i] = True
                    else:
                        break

        print('Sat clash matrix established!')

    def sen_matrix(self):
        for i in range(len(self.sen_info)):
            row, _ = np.where(self.data_arr == self.sen_name[i])
            # sen_clash_i = sorted(self.data_arr[row].tolist(), key=lambda x: x[1])
            sen_row = self.data_arr[row]
            sen_clash_i = sen_row[np.lexsort(sen_row[:, :2].T)]

            for item_i in range(len(row)):
                # 更新sen字典
                self.sen_dict[sen_clash_i[item_i][0]] = [i, item_i, sen_clash_i[item_i][1], sen_clash_i[item_i][2]]

                # 更新冲突矩阵
                self.sen_clash[i][item_i][item_i] = True
                for item_j in range(item_i + 1, len(row)):
                    # i结束时间>j开始时间
                    if sen_clash_i[item_i][2] > sen_clash_i[item_j][1]:
                        self.sen_clash[i][item_i][item_j] = True
                        self.sen_clash[i][item_j][item_i] = True
                    else:
                        break

        print('Sen clash matrix established!')


    def ga_coder(self):
        # index:卫星序号
        solve_index = []
        # 弧段范围 index:卫星相对弧段号
        ga_space = []

        # i个卫星j个任务flatten
        for i in range(len(self.sat_info)):
            for j in range(self.req[i]):
                solve_index.append(i)
                ga_space.append(range(self.sat_info[self.sat_name[i]]))

        print('Code for GA')
        return solve_index, ga_space

    def sa_init(self):
        # 卫星相对弧段范围
        sa_space = []

        # 初始解
        solve = []

        for i in range(len(self.sat_info)):
            assert self.sat_info[self.sat_name[i]] >= self.req[i]
            sa_space.append(range(self.sat_info[self.sat_name[i]]))
            solve.append(random.sample(range(self.sat_info[self.sat_name[i]]), self.req[i]))

        return solve, sa_space


if __name__ == "__main__":
    code = datacoder("datacsv/sat300sen60.csv")
    code.sat_matrix()
    code.sen_matrix()
    code.sa_init()
