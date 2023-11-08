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
            newBase = Base(self.strTimeLimit, 
                           base, 
                           self.numTrucks, 
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
    def __init__(self, str_time_limit, baseID, robotNum, robotCapaCty, CIDs, BCM, CCM, Demd):
        self.str_time_limit = str_time_limit
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
            # if leftCap <= 0:
            #     return selected, networkDemand
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
                self.active = False
        return selected, networkDemand

    def getResult(self):
        if not self.active:
            # get ccm from self.task
            # get bcm from self.task
            bcM = np.zeros((len(self.task)))
            ccM = np.zeros((len(self.task), len(self.task)))
            for i in self.task:
                bcM[i] = self.BCM[self.task[i]]
                for j in self.task:
                    ccM[i][j] = self.CCM[self.task[i]][self.task[j]]
            # already get demand
            task = [bcM, ccM, self.task, self.taskDemd]
            # append to task list
            self.taskLst.append(task)
            print("getting results")
            # result = SDVRP
            resultCID, resultQuantity, resultTotDist = SDVRP(self.robotCapaCty,
                                                             self.taskDemd,
                                                             ccM,
                                                             bcM,
                                                             self.task,
                                                             self.str_time_limit,
                                                             self.robotNum)
            # append to result list
            self.resultLst.append([resultCID, resultQuantity, resultTotDist])
            print("result is added correctly")
            self.baseInit()

    def saveResult(self, saveFolderPath):
        if not self.active:
            if len(self.resultLst) == 0:
                return 0
            baseName = str(self.ID) + ".csv"
            baseResultPath = os.path.join(saveFolderPath, baseName)
            result = self.resultLst
            round = []
            customer = []
            weight = []
            length = []
            for i in range(len(result)):
                for j in range(len(result[i][0])):
                    round.append(i)
                    customer.append(result[i][0][j])
                    weight.append(result[i][1][j])
                    c = result[i][0][j]
                    l = 0
                    if len(c) > 1:
                        l = self.BCM[self.ID][c[0]] + self.BCM[self.ID][c[-1]]
                        for ic in range(0, len(c)-1):
                            l += self.CCM[c[i]][c[i+1]]
                    if len(c) == 1:
                        l = self.BCM[self.ID][c[0]] + self.BCM[self.ID][c[-1]]
                    length.append(l)
            baseData = {'customer': customer, 'weight': weight,
                        'round': round, 'length': length}
            df = pd.DataFrame(baseData)
            print("data result shape is: ", df.shape)
            df.to_csv(baseResultPath)

    def optResult(self, resultFolderPath):
        name = str(self.ID) + '.csv'
        dPath = os.path.join(resultFolderPath, name)
        if not os.path.exists(dPath):
            return 0
        df = pd.read_csv(dPath)
        df["taskID"] = list(range(df.shape[0]))
        rounds = list(set(df['round'].values.tolist()))
        roundFirst = df[df["round"] == 0]
        numRobot = roundFirst.shape[0]

        # init robots based on first round of tasks
        optTaskLst = []
        optLenLst = []

        roundTaskLst = roundFirst["taskID"].values.tolist()
        roundLenLst = roundFirst["length"].values.tolist()
        
        optTaskLst = []
        for a in roundTaskLst:
            optTaskLst.append([a])
        optLenLst.append(roundLenLst)

        if len(rounds) > 1:
            for round in rounds:
                roundDF = df[df["round"] == round]
                roundTaskLst = roundDF["taskID"].values
                roundLenLst = roundDF["length"].values
                
                p = roundLenLst.argsort()

                sortedRoundTaskLst = roundTaskLst[p]
                sortedRoundLenLst = roundLenLst[p]
                sortedOptLenLst = sorted(optLenLst, reverse=True)
                for i in range(sortedRoundLenLst.shape[0]):
                    rIndex = optLenLst.index(sortedOptLenLst[i])
                    optTaskLst[rIndex].append(sortedRoundTaskLst[i])
                    optLenLst[rIndex] += sortedRoundLenLst[i]
        
        optDF = pd.DataFrame({'task': optTaskLst, 'distance': optLenLst})
        newName = 'optTask_' + str(self.ID) + '.csv'
        newPath = os.path.join(resultFolderPath, newName)
        optDF.to_csv(newPath)
