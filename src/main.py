from RoutePlanning_clean import RoadNetwork
import pandas as pd
import numpy as np
import os

tractFolder = r"Data/Tract"
# saveFolder = r"Result/Tract"
saveFolder = r"Result/Tract2"
# tractList = os.listdir(tractFolder)
tractList = ["110", "113", "118", "144", "148", "16", "164", "192", "193", "195", "2"]
tractList.sort()
# existLst = os.listdir(saveFolder)
# tractList = tractList[int(len(tractList)/2):]


# print(i, j)
# savePth = os.path.join(saveFolder, str(tract), str(i), str(j))
# tractPth = os.path.join(tractFolder, str(tract))
# numBase = i
# numTrucks = j
# truckCapacity = 15
# str_time_limit = 10
# # print(os.getcwd())
# if not os.path.exists(savePth):
#     os.makedirs(savePth)
# network = RoadNetwork(tractPth, numBase, numTrucks, truckCapacity, str_time_limit, savePth)
# if network.exist:
#     network.system_planning()

for tract in tractList:
    # if tract in existLst:
    #     continue
    tractPth = os.path.join(tractFolder, str(tract))
    for i in range(1, 6):
        for j in range(1, 6):
            # print(i, j)
            savePth = os.path.join(saveFolder, str(tract), str(i), str(j))

            numBase = i
            numTrucks = j
            truckCapacity = 15
            str_time_limit = 5
            # print(os.getcwd())
            if not os.path.exists(savePth):
                os.makedirs(savePth)
            network = RoadNetwork(tractPth, numBase, numTrucks, truckCapacity, str_time_limit, savePth)
            if network.exist:
                network.system_planning()

# #Tract
# for i in range(2, 6):
#     num_base = i
#     for j in range(1, 6):
#         num_trucks = j
#         truck_capacity = 15
#         str_time_limit = 10

#         tractFolder = r"Data/Tract"
#         resultFolder = r"Result/Tract"
#         tractList = os.listdir(tractFolder)
#         for tract in tractList:
#             # print(tract)
#             # if tract != "260":
#             #     continue
#             print("###############################################################################################")
#             print(i, j, tract)
#             # print(type(tract))
#             tractData = os.path.join(tractFolder, tract)
#             tractResultFolder = os.path.join(resultFolder, tract, str(num_base), str(num_trucks))
#             if not os.path.exists(tractResultFolder):
#                 os.makedirs(tractResultFolder)
#             bcM = np.load(os.path.join(tractData, "bcM.npy"))
#             ccM = np.load(os.path.join(tractData, "ccM.npy"))
#             baseList = pd.read_csv(os.path.join(tractData, "Base_" + str(num_base) + "_2.csv"))
#             baseList = baseList.iloc[0].values[3:] - 1

#             demand = pd.read_csv(os.path.join(tractData, "demand.csv"))
#             demand = demand["TTDDemd"].values.tolist()

#             print(bcM.shape)
#             print(ccM.shape)
#             network = RoadNetwork(ccM, bcM, demand, num_trucks,
#                             truck_capacity, baseList, str_time_limit)
            
#             # print(network.ccM.shape)
#             # print(network.bcM.shape)
#             # print(len(network.demands_d))
#             # print(network.demands_d)
#             # print(bcM)
#             # print(network.demands_d)
#             network.update_demand()
            

#             if len(network.demands_d) == 0:
#                 continue

#             network.system_planning()

#             for base in network.base_list:
#                 baseResultPath = tractResultFolder
#                 base.save_result(baseResultPath, network)
#                 base.optTasks(baseResultPath, baseResultPath)

#     # break


# # C_C_df = pd.read_csv(r'/home/huihai/Huihai/RobotDelivery/Data/C_C.csv')
# # B_C_df = pd.read_csv(r'/home/huihai/Huihai/RobotDelivery/Data/B_C.csv')

# C_C_df = pd.read_csv(r'Data/C_C.csv')
# B_C_df = pd.read_csv(r'Data/B_C.csv')

# C_C_matrix = np.ones((174, 174)) * 1000000000
# B_C_matrix = np.ones((141, 174)) * 1000000000

# # c_c_matrix
# OriginID = C_C_df['OriginID'].values.tolist()
# DestinID = C_C_df['Destinatio'].values.tolist()
# Length = C_C_df['Total_Leng'].values.tolist()
# for i in range(len(OriginID)):
#     C_C_matrix[OriginID[i]-1][DestinID[i]-1] = Length[i]

# # b_c_matrix
# OriginID = B_C_df['OriginID'].values.tolist()
# DestinID = B_C_df['Destinatio'].values.tolist()
# Length = B_C_df['Total_Leng'].values.tolist()
# for i in range(len(OriginID)):
#     B_C_matrix[OriginID[i]-1][DestinID[i]-1] = Length[i]

# demands_data = np.random.randint(0, 5, C_C_matrix.shape[0]).tolist()
# number_trucks = 5
# truck_capacity = 5
# base_ID = [20, 30, 50]
# str_time_limit = "2"

# network = RoadNetwork(C_C_matrix, B_C_matrix, demands_data, number_trucks,
#                       truck_capacity, base_ID, str_time_limit)

# network.update_demand()
# print(network.ccM.shape)
# print(network.bcM.shape)
# print(len(network.demands_d))

# network.system_planning()

# for base in network.base_list:
#     baseResultPath = r'/home/huihai/Huihai/RobotDelivery/Result/'
#     base.save_result(baseResultPath, network)
#     base.optTasks(baseResultPath, baseResultPath)