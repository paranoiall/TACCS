import time
import random
import numpy as np
import pygad

from data_circle import datacoder

# 碎片时间上限 单位s
seg_limit = 5 * 60

code = datacoder("access.csv")


num_generations = 2000
num_genes = 20

# 生成gene范围
def ga_init():
    solve = []

    # k种群数量
    for k in range(num_genes):
        solve_k = []

        for i in range(len(code.sat_name)):
            # i卫星
            circle = random.choice(code.circle[i])
            solve_i = []
            for j in circle:
                # j圈号
                acc = code.sat_circle[i][j - 1]
                solve_i.append(random.choice(acc))
            solve_k.append(solve_i)
        
        solve.append(np.array(solve_k, dtype=object))

    return solve


init_solve = ga_init()


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

    return solution, f1, f2, f3


def on_generation(ga_inst):
    global time_gen
    if not ga_inst.generations_completed % 100:
        print('Generation:%d, Time:%f' % (ga_inst.generations_completed, (time.time() - time_gen)))
        time_gen = time.time()


def fitness_func(solution, _):
    _, f1, f2, f3 = f_cul(solution)
    fitness = - f1 - f3 * 0.0001

    return fitness


def mutation_func(offspring, ga_instance):
    for num_offspring in range(len(offspring)):
        sat_move = np.random.randint(0, len(offspring[num_offspring]))
        new_circle = random.choice(code.circle[sat_move])

        new_solve = []
        for i in new_circle:
            acc = code.sat_circle[sat_move][i - 1]
            assert len(acc) > 0
            new_solve.append(random.choice(acc))

        offspring[num_offspring][sat_move] = new_solve

    return offspring

ga_instance = pygad.GA(num_generations=num_generations,
                       num_parents_mating=num_genes,
                       fitness_func=fitness_func,
                       gene_type=object,
                       initial_population=init_solve,
                       crossover_probability=0.7,
                       mutation_probability=0.05,
                       mutation_type=mutation_func,
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