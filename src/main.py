from RoutePlanning import RoadNetwork
import pandas as pd
import numpy as np

C_C_df = pd.read_csv(r'/home/huihai/Huihai/RobotDelivery/Data/C_C.csv')
B_C_df = pd.read_csv(r'/home/huihai/Huihai/RobotDelivery/Data/B_C.csv')

C_C_matrix = np.ones((174, 174)) * 1000000000
B_C_matrix = np.ones((141, 174)) * 1000000000

# c_c_matrix
OriginID = C_C_df['OriginID'].values.tolist()
DestinID = C_C_df['Destinatio'].values.tolist()
Length = C_C_df['Total_Leng'].values.tolist()
for i in range(len(OriginID)):
    C_C_matrix[OriginID[i]-1][DestinID[i]-1] = Length[i]

# b_c_matrix
OriginID = B_C_df['OriginID'].values.tolist()
DestinID = B_C_df['Destinatio'].values.tolist()
Length = B_C_df['Total_Leng'].values.tolist()
for i in range(len(OriginID)):
    B_C_matrix[OriginID[i]-1][DestinID[i]-1] = Length[i]

demands_data = np.random.randint(0, 5, C_C_matrix.shape[0]).tolist()
number_trucks = 10
truck_capacity = 5
base_ID = [20]
str_time_limit = "5"

network = RoadNetwork(C_C_matrix, B_C_matrix, demands_data, number_trucks,
                      truck_capacity, base_ID, str_time_limit)
network.update_demand()
print(network.ccM.shape)
print(network.bcM.shape)
print(len(network.demands_d))

network.system_planning()

print(network.base_list[1].task_list[0][2])
print(network.base_list[1].task_result_list[0][0])
print(network.base_list[1].task_result_list[0][1])
print(len(network.base_list[0].task_result_list))
