import pandas as pd
import numpy as np
import time
import plotly.express as px


# 输入例子 1,2,3，不能是【1,2,3】，
# 我把那个数据集重新读的，如果数据集没有变的话应该没有错误，理论上无论输入多少组都能输出甘特图
# sensor，也就是图的左侧，已经经过了排序
# 这里的绝对坐标从0开始，如果你的从1开始的话就减1


def draw(solve):
    use_col = ['starttime', 'endtime', 'Duration', 'Sen_name', 'Sat_name']
    data = pd.read_csv("access.csv", usecols=use_col)
    time0 = np.array(data)

    sat_solve = sum(solve[0:300],[])

    for i in range(0, len(sat_solve)):
        sat_solve[i] = sat_solve[i] - 1



    solution = sum(solve, [])

    for i in range(0, len(solution)):
        solution[i] = solution[i] - 1

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

    for i in range(time0.shape[0]):
        time0[i][0] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time0[i][0]))
        time0[i][1] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time0[i][1]))

    # 增加弧段总序号
    time0 = np.insert(time0, 0, np.arange(time0.shape[0]), axis=1)

    time0.tolist()
    solution_info = []

    sensor_name_init = []
    for i in range(0, len(solution)):
        sensor_name_int = ""
        for j in range(0, len(time0[solution[i]][4])):
            if is_number(time0[solution[i]][4][j]) == True:
                sensor_name_int = sensor_name_int + str(time0[solution[i]][4][j])
        sensor_name_int = int(sensor_name_int)
        sensor_name_init.append(sensor_name_int)

    sat_name_init = []
    for i in range(0, len(solution)):
        sat_name_int = ""
        for j in range(0, len(time0[solution[i]][5])):
            if is_number(time0[solution[i]][5][j]) == True:
                sat_name_int = sat_name_int + str(time0[solution[i]][5][j])
        sat_name_int = int(sat_name_int)
        sat_name_init.append(sat_name_int)

        # time0[i]=np.append(time0[i],[sensor_name_int])
        # time0[i].append(sensor_name_int).
    for i in range(0, len(solution)):
        solution_info.append(time0[solution[i]])

    sat_solve_info=[]
    for i in range(0,len(sat_solve)):
        sat_solve_info.append(time0[sat_solve[i]])

    sat_name_init_select = []
    for i in range(0, len(sat_solve)):
        sat_name_int = ""
        for j in range(0, len(time0[sat_solve[i]][5])):
            if is_number(time0[sat_solve[i]][5][j]) == True:
                sat_name_int = sat_name_int + str(time0[sat_solve[i]][5][j])
        sat_name_int = int(sat_name_int)
        sat_name_init_select.append(sat_name_int)

    # print(time0)

    use_col = ['num', 'starttime', 'endtime', 'duration', 'sen_name', 'sat_name']
    # print(sensor_name_init)
    df = pd.DataFrame(solution_info, columns=use_col)
    df1 = pd.DataFrame(solution_info, columns=use_col)
    df.insert(df.shape[1], 'sensor_name_int', sensor_name_init)
    df1.insert(df1.shape[1], 'sat_name_int', sat_name_init)

    df = df.sort_values(by="sensor_name_int", ascending=False)
    fig_sen = px.timeline(df, x_start="starttime", x_end="endtime", y="sen_name", hover_name="sat_name")
    fig_sen.update_yaxes(autorange="reversed")
    fig_sen.show()

    df1 = df1.sort_values(by="sat_name_int", ascending=False)
    fig_sat = px.timeline(df1, x_start="starttime", x_end="endtime", y="sat_name", hover_name="sen_name")
    fig_sat.update_yaxes(autorange="reversed")
    fig_sat.show()

    df2 = pd.DataFrame(sat_solve_info,columns=use_col)
    df2.insert(df2.shape[1], 'sat_name_int', sat_name_init_select)
    df2 = df2.sort_values(by="sat_name_int", ascending=False)
    fig_sat = px.timeline(df2, x_start="starttime", x_end="endtime", y="sat_name", hover_name="sen_name")
    fig_sat.update_yaxes(autorange="reversed")
    fig_sat.show()
    

if __name__ == "__main__":
    solve = []
    draw(solve)
