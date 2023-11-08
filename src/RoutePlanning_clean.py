import pandas as pd
import numpy as np
from SDVRP import SDVRP
import sys
import math
import os

class RoadNetwork:
    def __init__(self, 
                 dataFolder, 
                 numBase, 
                 number_trucks, 
                 truck_capacity, 
                 str_time_limit):
        
        self.numTrucks = number_trucks
        self.truck_capacity = truck_capacity
        self.strTimeLimit = str_time_limit
        
        # will not changed by demand clean
        self.BCM, self.CCM, self.baseLst, self.initDemd = self.read_data(dataFolder, numBase)


        self.initCIDs = np.array(list(range(self.CCM.shape[0])))

        self.Demd = self.update_demand(self.initDemd)

        self.CIDs = self.getCIDs(self.initCIDs, self.BCM, self.baseLst)

        self.baseInit()

    def baseInit(self):
        self.baseObjLst = []
        for base in self.baseLst:
            newBase = Base(base, self.numTrucks, 
                           self.truck_capacity, 
                           self.CIDs, 
                           self.BCM, 
                           self.CCM, 
                           self.Demd)
            self.baseObjLst.append(newBase)

    def getCIDs(self, initCIDs, initBCM, baseLst):
        # get IDs of customers that served by existing bases
        reference = np.zeros(initBCM[0].shape)
        for base in baseLst:
            reference += initBCM[int(base)]
        reference = reference / len(baseLst)
        removeCIDLst = []
        for i in range(len(reference)):
            if reference[i] == 1000000000:
                removeCIDLst.append(i)
        CIDs = np.delete(initCIDs, removeCIDLst)
        return CIDs
    
    def cleanIsolation(self, initCCM, initBCM, initDem, initCIDs, baseLst):
        reference = np.zeros(initBCM[0].shape)
        for base in baseLst:
            print(base)
            reference += initBCM[int(base)]
        reference = reference / len(baseLst)
        removeCIDLst = []
        for i in range(len(reference)):
            if reference[i] == 1000000000:
                removeCIDLst.append(i)
        ccm = initCCM
        bcm = initBCM
        demand = initDem
        CIDs = initCIDs
        
        #remove customers - customers: by columne and by row
        ccm = np.delete(ccm, removeCIDLst, axis=0)
        ccm = np.delete(ccm, removeCIDLst, axis=1)
        bcm = np.delete(bcm, removeCIDLst, axis=1)
        #remove demands
        demand = np.array(initDem)
        demand = np.delete(demand, removeCIDLst)
        CIDs = np.array(CIDs)
        CIDs = np.delete(CIDs, removeCIDLst)
        print(demand)
        #remove customers in base
        return ccm, bcm, demand, CIDs

    def read_data(self, dataFolder, numBase):
        #get data from data folder
        bcM = np.load(os.path.join(dataFolder, "bcM.npy"))
        ccM = np.load(os.path.join(dataFolder, "ccM.npy"))
        baseLst = pd.read_csv(os.path.join(dataFolder, "Base_" + str(numBase) + "_2.csv"))
        baseLst = baseLst.iloc[0].values[3:] - 1
        baseLst = np.array(baseLst)
        demand = pd.read_csv(os.path.join(dataFolder, "demand.csv"))
        demand = np.array(demand["TTDDemd"].values.tolist())
        return bcM, ccM, baseLst, demand

    def update_demand(self, Demd):
        dynDemd = []
        for d in Demd:
            # random  = np.random.normal(d, d/2)
            random = round(d)
            dynDemd.append(random)
        self.Demd = dynDemd
        return dynDemd
        
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

class Base():
    def __init__(self, baseID, robotNum, robotCapaCty, CIDs, BCM, CCM, Demd):
        self.ID = baseID
        self.robotCapaCty = robotCapaCty
        self.robotNum = robotNum
        self.BCM = BCM
        self.CCM = CCM
        self.Demd = Demd
        self.CIDs = self.sortCID(CIDs)
        self.task = []
        self.taksLst = []
        self.resultLst = []
        self.baseInit()

    def baseInit(self):
        self.sumDemd = 0
        self.task = []
        self.taskDemd = []
        self.active = True

    def sortCID(self, CIDs):
        bcM = np.take(self.BCM, CIDs)
        p = bcM.argsort()
        sortedCID = self.CIDs[p]
        return sortedCID
    
    def selectCustomer(self, selected):
        for i in range(self.CIDs.shape[0]):
            if self.CIDs[i] in selected:
                continue
            else:
                return self.CIDs[i]
        self.active = False
        return 0

    def addTask(self, c, selected, networkDemand):
        if self.active:
            leftCap = self.robotCapaCty * self.robotNum - self.sumDemd
            demand = self.Demd[c]
            if leftCap > demand:
                self.task.append(c)
                self.sumDemd += demand
                self.taskDemd.append(demand)
                selected.append(c)
            elif leftCap == demand:
                self.task.append(c)
                self.sumDemd += demand
                self.taskDemd.append(demand)
                selected.append(c)
                self.active = False
            else:
                self.task.append(c)
                self.taskDemd.append(leftCap)
                networkDemand[c] = demand - leftCap
        return selected, networkDemand

    def getResult(self):
        if not self.active:
            # get ccm
            # get bcm
            # already get demand
            # append to task list
            # result = SDVRP
            # append to result list
            pass

    def saveResult(self):
        if not self.active:
            # save result
            pass

    def optResult(self):
        if not self.active:
            # optimize results
            self.baseInit()

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