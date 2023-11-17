import pandas as pd
import numpy as np
import os

def getBaseRobot(num):
    base = num // 5 + 1
    robot = num % 5 + 1
    return base, robot

# base, robot = getBaseRobot(5)
# print(base, robot)

# ##################################################################
# # Get the most environment efficient strategy
# dataFolder = r"Result/"
# tractCO2 = os.path.join(dataFolder, "tractCO2Emission.csv")
# tractTime = os.path.join(dataFolder, "tractLongestTime.csv")
# df = pd.read_csv(tractCO2).drop(columns="Unnamed: 0")
# df_time = pd.read_csv(tractTime).drop(columns="Unnamed: 0")
# row = []
# for i in range(df.shape[0]): 
#     data = df.iloc[i].values[0: 25]
#     tract = df.iloc[i].values[-1]
#     idx = np.argmin(data)
#     numBase, numRobot = getBaseRobot(idx)
#     co2Emission = data[idx]
#     time = df_time.iloc[i][idx]
#     row.append([tract, numBase, numRobot, co2Emission, time])
# df = pd.DataFrame(row, columns=["tract", "Base_Num", "Robot_Num", "CO2", "Time"])
# df.to_csv(os.path.join(dataFolder, "mostCO2Efficiency.csv"))

#####################################################################
# Get the most time efficiency strategy
dataFolder = r"Result/"
tractCO2 = os.path.join(dataFolder, "tractCO2Emission.csv")
tractTime = os.path.join(dataFolder, "tractLongestTime.csv")
df = pd.read_csv(tractTime).drop(columns="Unnamed: 0")
df_CO2 = pd.read_csv(tractCO2).drop(columns="Unnamed: 0")
row = []
for i in range(df.shape[0]): 
    data = df.iloc[i].values[0: 25]
    tract = df.iloc[i].values[-1]
    idx = np.argmin(data)
    numBase, numRobot = getBaseRobot(idx)
    timeEff = data[idx]
    co2Emission = df_CO2.iloc[i][idx]
    row.append([tract, numBase, numRobot, timeEff, co2Emission])
df = pd.DataFrame(row, columns=["tract", "Base_Num", "Robot_Num", "Time", "CO2_Emission"])
df.to_csv(os.path.join(dataFolder, "mostTimeEfficiency.csv"))

# #####################################################################
# # Get the most strategy in a 6 hour threshod with least number of robots
# dataFolder = r"Result/"
# tractInfo = os.path.join(dataFolder, "tractLongestTime.csv")
# tractCO2 = os.path.join(dataFolder, "tractCO2Emission.csv")
# df = pd.read_csv(tractInfo).drop(columns="Unnamed: 0")
# df_CO2  = pd.read_csv(tractCO2).drop(columns="Unnamed: 0")
# row = []
# for i in range(df.shape[0]): 
#     data = df.iloc[i].values[0: 25]
#     tract = df.iloc[i].values[-1]
#     Find = False
#     for j in range(data.shape[0]):
#         if data[j] < 6:
#             Strategy = j
#             Find = True
#             break
#     if Find:
#         idx = Strategy
#         numBase, numRobot = getBaseRobot(idx)
#         Info = data[idx]
#         co2Emission = df_CO2.iloc[i][idx]
#     else:
#         numBase, numRobot = 100000000, 100000000
#         Info = 100000000
#         co2Emission = 100000000
#     row.append([tract, numBase, numRobot, Info, co2Emission])
# df = pd.DataFrame(row, columns=["tract", "Base_Num", "Robot_Num", "Time_6", "CO2_Emission"])
# df.to_csv(os.path.join(dataFolder, "TimeLess6.csv"))