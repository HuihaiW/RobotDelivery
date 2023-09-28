import pandas as pd
import numpy as np
from SDVRP import SDVRP
import sys
import math

class RoadNetwork:
    def __init__(self, C_C_Matrix, B_C_Matrix, demands, number_trucks, truck_capacity, base_ID, str_time_limit):
        self.C_C_matrix = C_C_Matrix
        self.B_C_matrix = B_C_Matrix

        self.demands = demands

        self.Customer_IDs = list(range(C_C_Matrix.shape[0]))

        self.Base_IDs = list(range(B_C_Matrix.shape[0]))

        self.number_trucks = number_trucks
        self.truck_capacity = truck_capacity
        self.baseID = base_ID
        self.str_time_limit = str_time_limit

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

        # records = []
        # for i in range(B_C_matrix.shape[0]):
        #     row = B_C_matrix[i]
        #     ave = row.sum()/B_C_matrix.shape[1]
        #     if ave > 100000000:
        #         records.append(i)
        # B_C_matrix = np.delete(B_C_matrix, records, axis=0)
        # for i in sorted(records, reverse=True):
        #     del self.Base_IDs[i]
        
        # # update base id


    def clean_demands(self):
        remove = []
        for i in range(len(self.demands)):
            if self.demands[i] == 0:
                remove.append(i)
                
        self.C_C_matrix = np.delete(self.C_C_matrix, remove, axis=0)
        self.C_C_matrix = np.delete(self.C_C_matrix, remove, axis=1)
        self.B_C_matrix = np.delete(self.B_C_matrix, remove, axis=1)

        for i in sorted(remove, reverse=True):
            del self.Customer_IDs[i]
            del self.demands[i]

    def route_planning(self):

        customer_list, quantity_list, total_distance = SDVRP(self, self.demands, 
                                                             self.C_C_matrix, 
                                                             self.B_C_matrix[self.baseID],
                                                             self.Customer_IDs, 
                                                             self.str_time_limit)

        return customer_list, quantity_list, total_distance
    
    def update():
        pass

