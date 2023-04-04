import time
import random

from simanneal import Annealer

from data import datacoder

# 碎片时间上限 单位s
seg_limit = 5 * 60

code = datacoder("access.csv")
code.sat_matrix()
code.sen_matrix()
init_solve, sa_space = code.sa_init()


# 缺点：若选择相同弧段两次，则f1+2
def f_cul(solution):
    # f1:冲突数量 f2:工作时长 f3:碎片时长
    f1 = 0
    f2 = 0
    f3 = 0

    # 注：访问data_arr时需要-1

    # sen桶
    bucket = [[] for _ in range(len(code.sen_info))]

    # 同sat弧段冲突
    for i in range(len(solution)):
        for j in range(len(solution[i]) - 1):
            # 顺便统计工作时长
            # f2 += code.data_arr[code.sat_dict[i][j] - 1][3]
            for k in range(j + 1, len(solution[i])):
                # assert code.data_arr[code.sat_dict[i][j] - 1][6] == code.data_arr[code.sat_dict[i][k] - 1][6]
                if code.sat_clash[i][solution[i][j]][solution[i][k]]:
                    f1 += 1

            # 总序号
            # acc = code.sat_dict[i][solution[i][j]]
            # sen序号
            sen_i = code.sen_dict[code.sat_dict[i][solution[i][j]]][0]
            # 总弧段号入桶
            bucket[sen_i].append(code.sat_dict[i][solution[i][j]])

        # 补充len(i)-1
        # f2 += code.data_arr[code.sat_dict[i][solution[i][-1]] - 1][3]
        sen_i = code.sen_dict[code.sat_dict[i][solution[i][-1]]][0]
        bucket[sen_i].append(code.sat_dict[i][solution[i][-1]])

    # 同sen弧段冲突
    for i in range(len(bucket)):

        # 桶排序
        bucket[i] = sorted(bucket[i], key=lambda x: code.sen_dict[x][2])

        for j in range(len(bucket[i]) - 1):

            # 计算碎片时间
            seg = code.sen_dict[bucket[i][j + 1]][2] - code.sen_dict[bucket[i][j]][3]
            if 0 < seg < seg_limit:
                f3 += seg
            elif seg < 0:
                f1 += 1

    return f1, f2, f3


class SANoCircle(Annealer):

    def move(self):
        sat_loc = random.randint(0, len(self.state) - 1)
        loc = random.randint(0, code.req[sat_loc] - 1)

        new_state = random.randint(0, code.sat_info[code.sat_name[sat_loc]] - 1)
        while new_state in self.state[sat_loc]:
            new_state = random.randint(0, code.sat_info[code.sat_name[sat_loc]] - 1)
        self.state[sat_loc][loc] = new_state

    # 优化至最小
    def energy(self):
        f1, f2, f3 = f_cul(self.state)
        fitness = f1
        return fitness


time_start = time.time()
sanc = SANoCircle(init_solve)

# auto_schedule = sanc.auto(minutes=1)
# sanc.set_schedule(auto_schedule)

sanc.Tmax = 25000.0  # Max (starting) temperature
sanc.Tmin = 0.001  # Min (ending) temperature
sanc.steps = 20000  # Number of iterations
# sanc.updates = 100  # Number of updates (by default an update prints to stdout)

best_solve, best_fit = sanc.anneal()
print('GA End! Cost Time:%f' % (time.time() - time_start))

best_f1, best_f2, best_f3 = f_cul(best_solve)
print(f_cul(best_solve), best_fit)
print('f1:%f, f2:%f, f3:%f ' % (best_f1, best_f2, best_f3))
