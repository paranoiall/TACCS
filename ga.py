import pygad
import numpy as np
import time
from data import datacoder

# from numba import jit

# 碎片时间上限 单位s
seg_limit = 5 * 60

code = datacoder("access.csv")

code.sat_matrix()
code.sen_matrix()

solve_index, solve_space = code.ga_coder()


# 适应度计算
def fitness_func(solution, _):
    _, f1, f2, f3 = f_cul(solution)
    fitness = - f1

    return fitness


# 缺点：若选择相同弧段两次，则f1+2
def f_cul(solution):
    # f1:冲突数量 f2:工作时长 f3:碎片时长
    f1 = 0
    f2 = 0
    f3 = 0

    # 弧段总序号
    acc = [code.sat_dict[solve_index[i]][solution[i]] for i in range(len(solution))]
    # 注：访问data_arr时需要-1

    # 同sat弧段冲突
    cnt = 0
    for i in range(len(code.req)):
        for j in range(cnt, cnt + code.req[i] - 1):
            # 顺便统计工作时长
            # f2 += code.data_arr[acc[j] - 1][3]
            for k in range(j + 1, cnt + code.req[i]):
                # assert code.data_arr[acc[j] - 1][6] == code.data_arr[acc[k] - 1][6]
                if code.sat_clash[i][solution[j]][solution[k]]:
                    f1 += 1

        cnt += code.req[i]
        # 最后一位工作时长
        # f2 += code.data_arr[acc[cnt - 1] - 1][3]

    # sen桶
    bucket = [[] for _ in range(len(code.sen_name))]
    for i in range(len(solution)):
        # sen序号
        sen_i = code.sen_dict[acc[i]][0]
        # 总弧段号入桶
        bucket[sen_i].append(acc[i])

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
                # for k in range(j + 1, len(bucket[i])):
                # assert code.data_arr[bucket[i][j] - 1][5] == code.data_arr[bucket[i][k] - 1][5]

                # 计算冲突数量
                # if code.sen_clash[i][code.sen_dict[bucket[i][j]][1]][code.sen_dict[bucket[i][k]][1]]:
                f1 += 1
                # else:
                #     break

    return acc, f1, f2, f3


def on_generation(ga_inst):
    global time_gen
    if not ga_inst.generations_completed % 100:
        print('Generation:%d, Time:%f' % (ga_inst.generations_completed, (time.time() - time_gen)))
        time_gen = time.time()


req_num = int(np.sum(code.req))
print("Request num:%d" % req_num)
genes_num = 20

ga_instance = pygad.GA(num_generations=2000,
                       num_parents_mating=genes_num,
                       fitness_func=fitness_func,
                       sol_per_pop=genes_num,
                       num_genes=req_num,
                       gene_type=int,
                       crossover_probability=0.7,
                       mutation_probability=0.05,
                       gene_space=solve_space,
                       on_generation=on_generation)

time_start = time.time()
time_gen = time.time()
print('GA Start!')
ga_instance.run()
print('GA End! Cost Time:%f' % (time.time() - time_start))

best_solution, best_fitness, _ = ga_instance.best_solution()
best_acc, best_f1, best_f2, best_f3 = f_cul(best_solution)

print(best_acc)
print('Fitness:%f' % best_fitness)
print('f1:%f, f2:%f, f3:%f ' % (best_f1, best_f2, best_f3))

ga_instance.plot_fitness(plot_type="plot")
# ga_instance.plot_new_solution_rate(plot_type="plot")
# ga_instance.plot_genes(plot_type="plot", solutions='all')
# ga_instance.plot_genes(plot_type="plot", solutions='best')
