import time
import random

from simanneal import Annealer

from data_circle import datacoder
from gannt_create import draw

# 碎片时间上限 单位s
seg_limit = 5 * 60

code = datacoder("access.csv")


# 生成初始解
def sa_init():
    solve = []

    for i in range(len(code.sat_name)):
        # i卫星
        circle = random.choice(code.circle[i])
        solve_i = []
        for j in circle:
            # j圈号
            acc = code.sat_circle[i][j - 1]
            solve_i.append(random.choice(acc))
        solve.append(solve_i)

    return solve


init_solve = sa_init()


# 冲突计算
def f_cul(solution):
    # f1:冲突数量 f2:工作时长 f3:碎片时长
    f1 = 0
    f2 = 0
    f3 = 0

    # sen桶
    bucket = [[] for _ in range(len(code.sen_info))]
    for i in solution:
        for j in i:
            # 总弧段号入桶
            bucket[code.sen_dict[j][0]].append(j)

    # 同sen弧段冲突
    for i in bucket:

        # 桶排序
        i = sorted(i, key=lambda x: code.sen_dict[x][1])

        for j in range(len(i) - 1):
            # f2 += code.sen_dict[i[j]][3]

            # 计算碎片时间
            seg = code.sen_dict[i[j + 1]][1] - code.sen_dict[i[j]][2]
            if 0 < seg < seg_limit:
                f3 += seg
            elif seg < 0:
                f1 += 1
        # if len(i):
            # f2 += code.sen_dict[i[-1]][3]

    return f1, f2, f3


class SACircle(Annealer):

    def move(self):
        sat_move = random.randint(0, len(self.state) - 1)
        new_circle = random.choice(code.circle[sat_move])

        new_solve = []
        for i in new_circle:
            acc = code.sat_circle[sat_move][i - 1]
            assert len(acc) > 0
            new_solve.append(random.choice(acc))

        self.state[sat_move] = new_solve

    # 优化至最小
    def energy(self):
        f1, f2, f3 = f_cul(self.state)
        fitness = f1 + f3 * 0.0001
        return fitness


time_start = time.time()
sac = SACircle(init_solve)

sac.Tmax = 25000.0  # Max (starting) temperature
sac.Tmin = 0.001  # Min (ending) temperature
sac.steps = 20000  # Number of iterations
# sac.updates = 100  # Number of updates (by default an update prints to stdout)

best_solve, best_fit = sac.anneal()
print('\n', best_solve)

print('SA End! Cost Time:%f' % (time.time() - time_start))
print(f_cul(best_solve), best_fit)

draw(best_solve)
# 改完直接运行就行b 不用随机 0-500就行
