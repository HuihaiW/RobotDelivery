import pandas as pd
import numpy as np
from SDVRP import SDVRP
import sys
import math

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
            bcM = self.bcM[i]
            b = base(ID, self.number_trucks, self.truck_capacity, bcM)
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

        for i in sorted(records, reverse=True):
            del self.Customer_IDs[i]
            del self.demands[i]
            del self.Base_IDs[i]

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
            random_d = np.random.normal(d, d/2)
            self.demands_d.append(int(random_d))
        self.clean_demands()
        self.update_base()

    def system_planning(self):
        served_list = []
        while len(served_list) < len(self.demands_d):
            for base in self.base_list:
                c = base.select(served_list)
                if not c == None:
                    add = base.add_customer(c, self.demands_d)
                if not add or c == None:
                    print('add tasks')
                    base.add_task(self.ccM)
                    if base.ccM.shape[0] == 0:
                        return 0
                    base.add_task_result(base.demands, base.ccM, base.bcM, base.cID, self.str_time_limit, base.NumRobots)
                    base.base_init()
                else:
                    # print('not adding')
                    served_list.append(c)

class base():
    def __init__(self, ID, NumRobots, robot_capacity, bcM):
        self.ID = ID
        self.NumRobots = NumRobots
        self.robot_capacity = robot_capacity
        self.distance_sorted = sorted(bcM.tolist())
        self.distance = bcM.tolist()
        self.task_list = []
        self.task_result_list = []
        self.base_init()

    def select(self, selected):
        while True:
            if len(self.distance_sorted) == 0:
                return None
            c = self.distance.index(self.distance_sorted[0])
            if c in selected:
                pop = self.distance_sorted.pop(0)
            else:
                pop = self.distance_sorted.pop(0)
                return c
    
    def add_customer(self, c, demand):
        if (self.weights + demand[c]) > self.robot_capacity * self.NumRobots:
            return False
        # if len(self.distance_sorted) == 0:
        #     self.weights += demand[c]
        #     self.cID.append(c)
        #     self.demands.append(demand[c])
        #     return False
        else:
            self.weights += demand[c]
            self.cID.append(c)
            self.demands.append(demand[c])
            return True

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
        customer_list, quantity_list, total_distance = SDVRP(self.robot_capacity, 
                                                             demand,
                                                             cc,
                                                             bc,
                                                             cID,
                                                             str_time_limit,
                                                             number_trucks)
        self.task_result_list.append([customer_list, quantity_list, total_distance])

    def base_init(self):
        self.bcM = np.empty((0, 0))
        self.ccM = np.empty((0, 0))
        self.cID = []
        # self.cID_O = []
        self.weights = 0
        self.demands = []
        



