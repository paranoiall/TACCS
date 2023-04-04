import comtypes
from comtypes.client import CreateObject
from win32api import GetSystemMetrics
# 以下2句：是因为【 root=uiApplication.Personality2 】 运行后，生成了【comtypes.gen】
from comtypes.gen import STKUtil
from comtypes.gen import STKObjects
from tqdm import tqdm
import random
import pandas as pd
from pandas import DataFrame
import numpy as np
import time

uiApplication = CreateObject("STK11.Application")
# 显示 STK11 软件界面
# 这2个开不开？go

uiApplication.Visible = True
uiApplication.UserControl = True

# Personality2 返回【STK对象模型的根对象】的新实例 IAgStkObjectRoot 接口
# 假如是 Personality, 则 打开现有STK对象
root = uiApplication.Personality2
root.NewScenario('sce')
sc = root.CurrentScenario
scenario2 = sc.QueryInterface(STKObjects.IAgScenario)
scenario2.SetTimePeriod('Today', '+%dhr' % (24*7+1))
stkRoot = uiApplication.personality2

# 创造卫星的参数
sat_num_total = 10
column1 = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
para_sat = []
for num in range(0, sat_num_total):
    locals()['SatObj' + str(num)] = sc.Children.New(18, 'sat' + str(num))
    # SatSensor = SatObj.Children.New(STKObjects.eSensor,'sensor'+str(num))
    locals()['SatIAF' + str(num)] = locals()['SatObj' + str(num)].QueryInterface(STKObjects.IAgSatellite)
    # 查看当前卫星轨道预报模型
    ProIAF = locals()['SatIAF' + str(num)].Propagator
    # 由IAgVePropagator跳转至IAgVePropagatorTwoBody
    ProTwoBodyIAF = ProIAF.QueryInterface(STKObjects.IAgVePropagatorTwoBody)
    # 设置卫星坐标系为J2000，轨道六要素为7000km，0，num×10°，0°，0°，0°
    a = 3
    b = random.randint(6900, 7500)
    c = 0
    d = random.randint(60, 90)
    e = random.randint(0, 360)
    f = random.randint(0, 360)
    g = random.randint(0, 360)
    para1 = [a, b, c, d, e, f, g]
    para_sat.append(para1)
    ProTwoBodyIAF.InitialState.Representation.AssignClassical(a, b, c, d, e, f, g)
    # 传递参数
    ProTwoBodyIAF.Propagate()
para_sat1 = pd.DataFrame(para_sat, columns=column1)
para_sat1.to_csv("stkdata/sat_para.csv")
print("sat created!")

# num为传感器的数量,num2为地面站的数量
column2 = ['a', 'b', 'c']
para_sen = []
num = 0
num2 = 0

down = 25
up=35
fac_total=10
res = [random.randint(down, up) for _ in range(fac_total)]
all_sum = sum(res)
sen_num_total = 300
while all_sum != sen_num_total:
    res = sorted(res)
    if all_sum > sen_num_total:
        res[-1] = random.randint(down, up)
    elif all_sum < sen_num_total:
        res[0] = random.randint(down, up)
    all_sum = sum(res)

num = 0
for num2 in range(len(res)):
    locals()['fac' + str(num2)] = sc.Children.New(STKObjects.eFacility, 'fac' + str(num2))
    locals()['facIAF' + str(num2)] = locals()['fac' + str(num2)].QueryInterface(STKObjects.IAgFacility)

    a = random.uniform(20, 50)
    if a < 30:
        b = random.uniform(100, 120)
    elif a > 40:
        b = random.uniform(115, 120)
    else:
        b = random.uniform(80, 120)

    c = 0
    para2 = [a, b, c]
    para_sen.append(para2)
    locals()['facIAF' + str(num2)].Position.AssignGeodetic(a, b, c)
    # ref1 = ('fac'+str(num2),a,b,c)
    # arr.append(ref1)
    locals()['facIAF' + str(num2)].UseTerrain = True
    locals()['facIAF' + str(num2)].HeightAboveGround = 0
    for i in range(res[num2]):
        locals()['sen' + str(num)] = locals()['fac' + str(num2)].Children.New(STKObjects.eSensor, 'sen' + str(num))
        locals()['senIAF' + str(num)] = locals()['sen' + str(num)].QueryInterface(STKObjects.IAgSensor)
        locals()['sensimple' + str(num)] = locals()['senIAF' + str(num)].CommonTasks
        locals()['sensimple' + str(num)] = locals()['sensimple' + str(num)].QueryInterface(STKObjects.IAgSnCommonTasks)
        locals()['sensimple' + str(num)].SetPatternSimpleConic(60, 1)
        num = num + 1

para_sen1 = pd.DataFrame(para_sen, columns=column2)
para_sen1.to_csv("stkdata/sen_para.csv")
print("sen created!")

sat_list = stkRoot.CurrentScenario.Children.GetElements(STKObjects.eSatellite)
fac_list = stkRoot.CurrentScenario.Children.GetElements(STKObjects.eFacility)

sat_num = 0
for each_sat in sat_list:
    locals()['SatIAF' + str(sat_num)] = each_sat.QueryInterface(STKObjects.IAgSatellite)
    sat_num = sat_num + 1

time0 = []
for each_fac in fac_list:
    now_fac_name = each_fac.InstanceName
    sensor_list = each_fac.Children.GetElements(STKObjects.eSensor)
    each_sensor = sensor_list[0]
    print(now_fac_name)

    for each_sat in tqdm(sat_list):

        # locals()['access'+str(access_num)] = each_sensor.GetAccessToObject(each_sat)
        # locals()['access'+str(access_num)].ComputeAccess()
        access = each_sensor.GetAccessToObject(each_sat)
        access.ComputeAccess()
        accessAer=access.DataProviders.Item('AER Data')
 #       accessAer2=accessAer.QueryInterface(STKObjects.IAgDataPrvElement)
        accessDP = access.DataProviders.Item('Access Data')
        accessDP2 = accessDP.QueryInterface(STKObjects.IAgDataPrvInterval)
        results = accessDP2.Exec(scenario2.StartTime, scenario2.StopTime)
        if results.DataSets.Count == 0:
            continue
        accessNum = results.DataSets.GetDataSetByName('Access Number').GetValues()
        accessStartTimes = results.DataSets.GetDataSetByName('Start Time').GetValues()  # 注意是个元组，有多个值
        accessStopTimes = results.DataSets.GetDataSetByName('Stop Time').GetValues()  # 注意是个元组，有多个值
        accessDuration = results.DataSets.GetDataSetByName('Duration').GetValues()
        accessToPassNum = results.DataSets.GetDataSetByName('To Pass Number').GetValues()
        accessStartLat = results.DataSets.GetDataSetByName('To Start Lat').GetValues()
        accessStopLat = results.DataSets.GetDataSetByName('To Stop Lat').GetValues()

        visibleInterval = list(zip(accessNum, accessStartTimes, accessStopTimes, accessDuration, accessToPassNum, accessStartLat, accessStopLat))
        for sensor_i in sensor_list:
            for i in range(len(accessNum)):
                tem = visibleInterval[i]
                tem = list(tem)

                tmtime = tem[1].split('.')[0]
                tem[1] = time.mktime(time.strptime(tmtime, "%d %b %Y %H:%M:%S"))
                endtime = tem[2].split('.')[0]
                tem[2] = time.mktime(time.strptime(endtime, "%d %b %Y %H:%M:%S"))

                edtime = tem.pop()
                sttime = tem.pop()

                tem.append(each_fac.InstanceName)
                tem.append(sensor_i.InstanceName)
                tem.append(each_sat.InstanceName)

                if sttime<edtime:
                    tem.append(1)
                else:
                    tem.append(0)

                time0.append(tem)

# time1 = pd.DataFrame(time0,
#                      columns=['Access Number', 'Start Time', 'Stop Time', 'Duration', 'To Pass Number', 'To Start Lat',
#                               'To Stop Lat', 'Fac_name', 'Sen_name', 'Sat_name'])
# time1['UpDown'] = time1.apply(lambda x: 1 if x[5] < x[6] else 0, axis=1)
# print(time1['Start Time'][0])
# for i in range(time1.shape[0]):
#     str1 = time1.loc[i, 'Start Time']
#     time1.loc[i, 'Start Time'] = str1.split('.')[0]
#     str2 = time1.loc[i, 'Stop Time']
#     time1.loc[i, 'Stop Time'] = str2.split('.')[0]
# time1['starttime'] = time1.apply(lambda x: time.mktime(time.strptime(x['Start Time'], "%d %b %Y %H:%M:%S")), axis=1)
# time1['endtime'] = time1.apply(lambda x: time.mktime(time.strptime(x['Stop Time'], "%d %b %Y %H:%M:%S")), axis=1)
# time1['toptime'] = time1.apply(lambda x: (x['starttime'] + x['endtime']) / 2, axis=1)

# time1 = time1.insert( 0, "Access Absolute Number",np.arange(time1.shape[0]))这是什么，绝对的那个accessnumber。那现在的是啥


column = ['Access Number', 'starttime', 'endtime', 'Duration', 'To Pass Number', 'Fac_name', 'Sen_name',
          'Sat_name', 'UpDown']
test = pd.DataFrame(columns=column, data=time0)
# time0 = time1[column]
test.to_csv("stkdata/sat1000sen300fac10.csv")
