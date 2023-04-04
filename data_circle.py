import time
import random
from collections import Counter

import numpy as np
import pandas as pd

from cul_circle import circle_choose


class datacoder:
    def __init__(self, path):
        data = pd.read_csv(path, usecols=['starttime', 'endtime', 'Duration', 'To Pass Number', 'Sen_name', 'Sat_name'])

        self.sat_info = Counter(data['Sat_name'])
        self.sen_info = Counter(data['Sen_name'])

        self.data_arr = np.array(data)

        self.time_start = min(np.min(self.data_arr[:, 0]), np.min(self.data_arr[:, 1]))
        for i in range(self.data_arr.shape[0]):
            self.data_arr[i][0] -= self.time_start
            self.data_arr[i][1] -= self.time_start

        self.data_arr = np.insert(self.data_arr, 0, np.arange(1, self.data_arr.shape[0] + 1), axis=1)

        # 名列表 序号->名
        self.sat_name = []
        self.sen_name = [x for x in self.sen_info]

        # 卫星需求 卫星号:需求数
        self.task = np.zeros(len(self.sat_info), dtype=int)

        # 可能圈次组合 卫星号:[[1],...]
        self.circle = []
        self.cul_prop_circle()

        # sen字典 总弧段号:[天线序号, 开始时间, 结束时间]
        self.sen_dict = {}
        self.sen_matrix()

        # 圈内弧段 卫星号 + 圈号-1 -> 弧段号列表
        self.sat_circle = [[] for _ in range(len(self.sat_info))]
        self.sat_circle_list()

    # 晚上地面站dict
    def sen_matrix(self):
        for i in range(len(self.sen_name)):
            row = np.where(self.data_arr[:, 5] == self.sen_name[i])[0]
            sen_row = self.data_arr[row]
            sen_row = sen_row[np.lexsort(sen_row[:, :2].T)]
            for item_i in range(len(row)):
                self.sen_dict[sen_row[item_i][0]] = [i, sen_row[item_i][1], sen_row[item_i][2], sen_row[item_i][3]]
        print('Sen dict established!')

    # 计算卫星每圈可选弧段
    def sat_circle_list(self):
        for i in range(len(self.sat_name)):
            # i卫星
            sat_i = self.data_arr[np.where(self.data_arr[:, 6] == self.sat_name[i])]
            circle_max = max(sat_i[:, 4])
            for j in range(circle_max):
                # j+1圈号
                circle_j = sat_i[np.where(sat_i[:, 4] == j + 1)]
                if circle_j.size > 0:
                    self.sat_circle[i].append(circle_j[:, 0].astype(int).T.tolist())
                else:
                    self.sat_circle[i].append([])
        print('Sat-circle list established!')

    # 生成卫星任务----【修改】
    def task_prop_cul(self, data):
        data = np.array(data)
        task_num = 3
        sat_now = 0  # 当前遍历卫星编号

        circle_dis = 3
        if data[0][1] > circle_dis:
            data[0][5] = 1

        for i in range(1, len(data)):
            if data[i][0] == data[i - 1][0]:  # 当前卫星与前一行是同一卫星
                if data[i][1] - data[i - 1][1] > circle_dis:  # 可见圈次间隔超过三圈及以上则将该可见圈标记为必要观测圈次----【修改】
                    data[i][5] = 1
            else:
                self.task[sat_now] = task_num  # 设置每个卫星的任务数量为4----【修改】
                if data[i][1] > circle_dis:
                    data[i][5] = 1
                sat_now += 1

        self.task[sat_now] = task_num
        return data

    # 计算约束下卫星可选圈
    def cul_prop_circle(self):
        path = "circle.csv"
        circle_data = pd.read_csv(path, usecols=["sat_name", "circle", "starttime", "endtime", "updown"])
        necessary = [0] * len(circle_data)
        circle_data['necessary'] = necessary  # 插入圈次必要性（可以认为是优先级）

        # 计算task
        circle_data_arr = self.task_prop_cul(circle_data)

        # 计算circle
        self.circle, self.sat_name = circle_choose(circle_data_arr, self.task)
        print('Circle calculated!')


if __name__ == "__main__":
    time0 = time.time()
    code = datacoder("access.csv")
    print("Cost time:", time.time() - time0)
