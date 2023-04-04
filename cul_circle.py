import copy

import pandas as pd
import numpy as np
import random
from collections import Counter
from itertools import combinations


# 数据预处理；
# ①依据卫星与设备可用关系剔除部分可见但不可用的圈次，得到输出表1；
# ②在输出表1的基础上，计算所有卫星每个圈次的占用时间（最早可见时间），将每个卫星每圈的占用时间、卫星优先级、圈次升降轨信息进行整合，得到输出表2.

# 任务生成：————需要问一下贾师兄任务生成是否会不合理（或者需要根据圈数确定任务数量）
# ①必要任务：依据输出表2（连续5圈以上不可见后第1圈可见必须观测）确定必要任务圈数号，记录必要任务数量为task_nec，记必要圈次优先级为1；
# ②随机任务：每个卫星随机生成1-3个任务圈数，记录随机任务数量为task_ran；
# ③记录卫星的总任务数量：task_num = task_nec + task_ran。
# 最终生成一个任务list(task_list)：sat_name+task_num


def task_prop_cul(data, task_all):
    data = np.array(data)
    task_num = 5
    sat_now = 0  # 当前遍历卫星编号

    circle_dis = 3
    if data[0][1] > circle_dis:
        data[0][5] = 1

    for i in range(1, len(data)):
        if data[i][0] == data[i - 1][0]:  # 当前卫星与前一行是同一卫星
            if data[i][1] - data[i - 1][1] > circle_dis:  # 可见圈次间隔超过三圈及以上则将该可见圈标记为必要观测圈次----【修改】
                data[i][5] = 1
        else:
            task_all[sat_now] = task_num  # 设置每个卫星的任务数量为4----【修改】
            if data[i][1] > circle_dis:
                data[i][5] = 1
            sat_now += 1

    task_all[sat_now] = task_num
    return data, task_all


# print(task_all)
# print("data:", data)


# 相关约束：①圈次间隔圈数；2 ②圈次间隔时间（上一圈次最晚结束可见与下一圈次最早可见时间间隔）
def choose_sat(sat_data, task_all):
    gap_circle = 1
    gap_time = 10000

    sat_choose = []  # 单颗卫星的圈次选择
    selected = []  # 单颗卫星的已选圈次列表
    selectable = []  # 单颗卫星目前的可选圈次列表
    circle = []
    sat = int(sat_data[0][0][3:])
    num_tochoose = task_all[sat]
    for i in range(len(sat_data)):
        if sat_data[i][5] == 1:  # 首先加入必要圈次
            selected.append(sat_data[i])  # 将必要圈次加入已选圈次列表中
            num_tochoose -= 1
        else:
            if selected:
                for j in range(len(selected)):
                    if (selected[j][1] + gap_circle < sat_data[i][1] or sat_data[i][1] < selected[j][1] - gap_circle) and \
                            (selected[j][3] + gap_time < sat_data[i][2] or selected[j][2] - gap_time > sat_data[i][3]):
                        selectable.append(sat_data[i])  # 将非必要圈次加入可选圈次列表中
            else:
                selectable.append(sat_data[i])  # 将非必要圈次加入可选圈次列表中
    # print("selected:", selected)
    # print("selectable:", selectable)
    x = list(range(len(selectable)))
    num_tochoose = min(len(selectable), num_tochoose)
    while num_tochoose > 0:

        if num_tochoose == 1 and len(selectable)>0:
            for i in range(len(selectable)):
                for j in range(len(selected)):
                        circle.append(selected[j][1])
                circle.append(selectable[i][1])
                sat_choose.append(copy.deepcopy(circle))
                circle.clear()
            # 将可选圈次加入已选中
            break

        elif 1 < num_tochoose <= len(selectable):
            for i in combinations(x, num_tochoose):  # i为当前可选圈次列表中满足剩余圈次的所有可能的圈次组合
                flag = 1
                for m in range(len(i) - 1):
                    for n in range(m + 1, len(i)):
                        # print("selectable[i[m]][1]:", selectable[i[m]][1])
                        # print("selectable[i[n]][1]:", selectable[i[n]][1])
                        if selectable[i[m]][1] + gap_circle >= selectable[i[n]][1] or selectable[i[m]][3] + gap_time >= \
                                selectable[i[n]][2]:
                            flag = 0
                # circle = []
                if flag == 1:
                    for j in range(len(selected)):
                        circle.append(selected[j][1])
                    for k in range(len(i)):
                        circle.append(selectable[i[k]][1])
                    sat_choose.append(copy.deepcopy(circle))
                    circle.clear()
            if len(sat_choose) == 0:
                num_tochoose -= 1
            else:
                break

    if len(sat_choose) == 0:
        for j in range(len(selected)):
            circle.append(selected[j][1])
        sat_choose.append(copy.deepcopy(circle))
        circle.clear()

    # print(sat_data[0][0])
    # print("sat_choose:", sat_choose)
    chosen_num = len(sat_choose[0])  # 记录当前方案的被选圈次数

    return sat_choose, chosen_num


def circle_choose(data, task_all):
    choose = []
    sat_name = []
    sat_data = [data[0]]
    chosen_all = 0  # 被选中的圈次总数

    for i in range(1, len(data)):  # 卫星迭代
        if data[i][0] != data[i - 1][0]:
            sat_choose, chosen_num = choose_sat(sat_data, task_all)  # ----【修改】
            choose.append(sat_choose)
            chosen_all += min(chosen_num, task_all[len(choose)-1]) # 记录被选圈次总数
            sat_name.append(data[i - 1][0])
            sat_data.clear()

        sat_data.append(data[i])

    sat_choose, chosen_num = choose_sat(sat_data, task_all)  # ----【修改】
    choose.append(sat_choose)
    chosen_all += min(chosen_num, task_all[-1])
    sat_name.append(data[-1][0])

    task_num_all = sum(task_all)  # ----【修改】
    circle_rate = chosen_all / task_num_all
    print("circle choose completion rate =", circle_rate)

    return choose, sat_name


if __name__ == '__main__':
    path = "circle.csv"
    circle_data = pd.read_csv(path, usecols=["sat_name", "circle", "starttime", "endtime", "updown"])
    necessary = [0] * len(circle_data)
    circle_data['necessary'] = necessary  # 插入圈次必要性（可以认为是优先级）

    # 计算task
    sat_num = Counter(circle_data['sat_name'])
    task = np.zeros(len(sat_num), dtype=int)
    circle_data_arr, task = task_prop_cul(circle_data, task)

    # 计算circle
    circle, sat_name = circle_choose(circle_data_arr, task)
    # print(circle)
    # print(sat_name)
