import pandas as pd
import numpy as np
from SDVRP import SDVRP
import sys
import math
import os

class RoadNetwork:
    def __init__(self, C_C_Matrix, B_C_Matrix, demands, number_trucks, 
                 truck_capacity, base_ID_list, str_time_limit):
        # will not changed by demand clean
        self.C_C_matrix = C_C_Matrix
        self.B_C_matrix = B_C_Matrix

        # changed by demand clean
        self.ccM = self.C_C_matrix
        self.bcM = self.B_C_matrix

        self.demands = demands
        self.demands_d = []

        self.Customer_IDs = list(range(C_C_Matrix.shape[0]))
        
        self.Base_IDs = list(range(B_C_Matrix.shape[0]))

        self.number_trucks = number_trucks
        self.truck_capacity = truck_capacity
        self.str_time_limit = str_time_limit
        self.clean_matrixes()

        self.ccM = self.C_C_matrix
        self.bcM = self.B_C_matrix
        self.CIDs = self.Customer_IDs
        self.baseID = [self.Base_IDs.index(b) for b in base_ID_list]

        self.update_base()
    
    def update_base(self):
        self.base_list = []
        for i in range(len(self.baseID)):
            ID = self.baseID[i]
            bcM = self.bcM[ID]
            b = base(ID, self.number_trucks, self.truck_capacity, bcM, self.Customer_IDs)
            self.base_list.append(b)
    
    def clean_matrixes(self):
        # Clean road segments that are not connected to the road networks
        records = []
        for i in range(self.C_C_matrix.shape[0]):
            row = self.C_C_matrix[i]
            ave = row.sum()/(self.C_C_matrix.shape[0] - 1)
            if ave > 100000000.0:
                records.append(i)

        self.C_C_matrix = np.delete(self.C_C_matrix, records, axis=0)
        self.C_C_matrix = np.delete(self.C_C_matrix, records, axis=1)
        self.B_C_matrix = np.delete(self.B_C_matrix, records, axis=1)

        print(len(self.Base_IDs))
        for i in sorted(records, reverse=True):
            print(i)
            del self.Customer_IDs[i]
            del self.demands[i]
            # del self.Base_IDs[i]

    def clean_demands(self):
        remove = []
        for i in range(len(self.demands_d)):
            if self.demands_d[i] == 0:
                remove.append(i)
                
        self.ccM = np.delete(self.ccM, remove, axis=0)
        self.ccM = np.delete(self.ccM, remove, axis=1)
        self.bcM = np.delete(self.bcM, remove, axis=1)

        for i in sorted(remove, reverse=True):
            del self.CIDs[i]
            del self.demands_d[i]

    def route_planning(self, demand, cc, bc, customer_id, str_time_limit, number_trucks):
        # route planning for each base

        customer_list, quantity_list, total_distance = SDVRP(self, 
                                                             demand,
                                                             cc,
                                                             bc,
                                                             customer_id,
                                                             str_time_limit,
                                                             number_trucks)

        return customer_list, quantity_list, total_distance

    def update_demand(self):
        
        self.CIDs = self.Customer_IDs

        self.demands_d = []
        for d in self.demands:
            # random_d = np.random.normal(d, d/2)
            random_d = round(d)
            self.demands_d.append(abs(int(random_d)))
        self.clean_demands()
        self.update_base()

    def system_planning(self):
        served_list = []
        while len(served_list) <= len(self.demands_d):
            for base in self.base_list:
                print("***************************************************")
                print("baseID", base.ID)
                c = base.select(served_list)
                if c == None: 
                    print('add tasks')
                    base.add_task(self.ccM)
                    print(base.ccM.shape)
                    if base.ccM.shape[0] == 0:
                        return 0
                    base.add_task_result(base.demands, base.ccM, base.bcM, base.cID, self.str_time_limit, base.NumRobots)
                    base.base_init()
                if not c == None:
                    add, self.demands_d = base.add_customer(c, self.demands_d)
                if not add:
                    print('add tasks')
                    base.add_task(self.ccM)
                    print(base.ccM.shape)
                    if base.ccM.shape[0] == 0:
                        return 0
                    base.add_task_result(base.demands, base.ccM, base.bcM, base.cID, self.str_time_limit, base.NumRobots)
                    base.base_init()
                else:
                    # print('not adding')
                    served_list.append(c)

class base():
    def __init__(self, ID, NumRobots, robot_capacity, bcM, networkIDList):
        self.ID = ID
        self.NumRobots = NumRobots
        self.robot_capacity = robot_capacity
        self.distance_sorted = sorted(bcM.tolist())
        self.distance = bcM.tolist()
        self.task_list = []
        self.task_result_list = []
        self.networkIDList = networkIDList
        self.base_init()

    def select(self, selected):
        while True:
            if len(self.distance_sorted) == 0:
                return None
            c = self.distance.index(self.distance_sorted[0])
            # print(self.distance_sorted)
            if c in selected:
                self.distance_sorted.pop(0)
                continue
            else:
                return c
        
    def add_customer(self, c, demand):
        print("adding customers ...")
        if (self.weights + demand[c]) > self.robot_capacity * self.NumRobots:
            add_weight = self.robot_capacity * self.NumRobots - self.weights
            networkDemand = demand
            if add_weight > 0:
                self.weights += add_weight
                self.cID.append(c)
                self.demands.append(add_weight)
                networkDemand[c] = networkDemand[c] - add_weight
            return False, networkDemand
        # if len(self.distance_sorted) == 0:
        #     self.weights += demand[c]
        #     self.cID.append(c)
        #     self.demands.append(demand[c])
        #     return False
        else:
            self.distance_sorted.pop(0)
            self.weights += demand[c]
            self.cID.append(c)
            self.demands.append(demand[c])
            return True, demand

    def add_task(self, ccM):
        self.bcM = np.zeros((len(self.cID),))
        self.ccM = np.zeros((len(self.cID), len(self.cID)))
        for i in range(len(self.cID)):
            self.bcM[i] = self.distance[self.cID[i]]
        for i in range(len(self.cID)):
            for j in range(len(self.cID)):
                self.ccM[i][j] = ccM[i][j]
        
        task = [self.bcM, self.ccM, self.cID, self.demands]
        self.task_list.append(task)

    def add_task_result(self, demand, cc, bc, cID, str_time_limit, number_trucks):
        print("adding task results ...")
        customer_list, quantity_list, total_distance = SDVRP(self.robot_capacity, 
                                                             demand,
                                                             cc,
                                                             bc,
                                                             cID,
                                                             str_time_limit,
                                                             number_trucks)
        self.task_result_list.append([customer_list, quantity_list, total_distance])
        print("result adding correctly")

    def base_init(self):
        print("init base ... ")
        self.bcM = np.empty((0, 0))
        self.ccM = np.empty((0, 0))
        self.cID = []
        # self.cID_O = []
        self.weights = 0
        self.demands = []
        print("base initialized")
    def save_result(self, saveFolderPath, network):
        baseName = str(self.ID) + '.csv'
        baseResultPath = os.path.join(saveFolderPath, baseName)
        result = self.task_result_list
        round = []
        customer = []
        weight = []
        length = []
        for i in range(len(result)):
            for j in range(len(result[i][0])):
                round.append(i)
                base_c = result[i][0][j]
                customer.append(base_c)
                weight.append(result[i][1][j])            
                l = 0
                if len(base_c) > 1:
                    l = network.B_C_matrix[self.ID][base_c[0]] + network.B_C_matrix[self.ID][base_c[-1]]
                    for c in range(len(base_c), len(base_c) - 1):
                        l += network.C_C_matrix[base_c[c][c+1]]
                elif len(base_c) > 0:
                    l = network.B_C_matrix[self.ID][base_c[0]] + network.B_C_matrix[self.ID][base_c[-1]]
                length.append(l)

        base_data = {'customer': customer, 'weight' : weight, 'round': round, 'length': length}
        df = pd.DataFrame(base_data)
        print("data result shape is: ", df.shape)
        print(baseResultPath)
        df.to_csv(baseResultPath)
    def optTasks(self, resultfolder, save_path):
        name = str(self.ID) + '.csv'
        dpath = os.path.join(resultfolder, name)
        df = pd.read_csv(dpath)
        rounds = list(set(df['round'].values.tolist()))
        lengthLL = []
        # get length for each task in each round
        for round in rounds:
            l = df[df['round'] == round]['length'].values.tolist()
            lengthLL.append(l)
        # get number of robots for each base
        num_robots = len(lengthLL[0])
        
        # deploy tasks for each robot, task are numbered as the order of origin tasks
        optT = []
            # init robot tasks
        for i in range(num_robots):
            optT.append([i])
        robot_distance = [d for d in lengthLL[0]]

            # optimize length
        if len(rounds) > 1:
            for r_i in range(1, len(rounds)):
                task_distance = lengthLL[r_i]
                sort = task_distance.copy()
                sort.sort(reverse=True)
                distances = robot_distance.copy()
                distances.sort()
                for j in range(num_robots):
                    robot_id = robot_distance.index(distances[j])
                    task_id = task_distance.index(sort[j])
                    robot_distance[robot_id] = robot_distance[robot_id] + task_distance[task_id]
                    optT[robot_id].append(num_robots*r_i + task_id)
        df_opt = pd.DataFrame({'task': optT, 'distance': robot_distance})
        new_name = 'optTask_' + str(self.ID) + '.csv'
        new_path = os.path.join(save_path, new_name)
        df_opt.to_csv(new_path)
        

        



        
                

        

        



