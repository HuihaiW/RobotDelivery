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

