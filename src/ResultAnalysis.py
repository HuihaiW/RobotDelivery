import pandas as pd
import numpy as np
from ast import literal_eval
import os

def readDataRobot(TractFolder, reader = "totalDistance"):
    data = []
    for base in range(1, 6):
        for robot in range(1, 6):
            if reader == "totalDistance":
                dist = 0
                resultFolder = os.path.join(TractFolder, str(base), str(robot))
                optList = os.listdir(resultFolder)
                optList = [f for f in optList if f.split("_")[0] == "optTask"]
                if len(optList) > 0:
                    for opt in optList:
                        optPath = os.path.join(resultFolder, opt)
                        df = pd.read_csv(optPath)
                        dfDist = df["distance"].values.sum()
                        dist += dfDist
                else:
                    dist += 1000000000
                data.append(dist)
            if reader == "CO2 emission":
                dist = 0
                resultFolder = os.path.join(TractFolder, str(base), str(robot))
                optList = os.listdir(resultFolder)
                optList = [f for f in optList if f.split("_")[0] == "optTask"]
                if len(optList) > 0:
                    for opt in optList:
                        optPath = os.path.join(resultFolder, opt)
                        df = pd.read_csv(optPath)
                        dfDist = df["distance"].values.sum()
                        dist += dfDist
                    data.append(dist/3600 * 0.178)
                else:
                    data.append(1000000000)
                
            elif reader == "totalPackagesDelivered":
                resultFolder = os.path.join(TractFolder, str(base), str(robot))
                resultList = os.listdir(resultFolder)
                resultList = [f for f in resultList if ("optTask" not in f)]
                totalWeight = 0
                if len(resultList) > 0:
                    for r in resultList:
                        rPath = os.path.join(resultFolder, r)
                        df = pd.read_csv(rPath)
                        dfCust = df["weight"].values.tolist()
                        for custLst in dfCust:
                            cL = literal_eval(custLst)
                            if len(cL) > 0:
                                totalWeight += sum(cL)
                            

                data.append(totalWeight)

            elif reader == "totalCustmerServed":
                resultFolder = os.path.join(TractFolder, str(base), str(robot))
                resultList = os.listdir(resultFolder)
                resultList = [f for f in resultList if ("optTask" not in f)]
                totalC = []
                if len(resultList) > 0:
                    for r in resultList:
                        rPath = os.path.join(resultFolder, r)
                        df = pd.read_csv(rPath)
                        dfCust = df["customer"].values.tolist()
                        for custLst in dfCust:
                            cL = literal_eval(custLst)
                            for c in cL:
                                totalC.append(c)
                totalC = list(set(totalC))
                data.append(len(totalC))

            elif reader == "longestDistance":
                resultFolder = os.path.join(TractFolder, str(base), str(robot))
                optList = os.listdir(resultFolder)
                optList = [f for f in optList if f.split("_")[0] == "optTask"]
                if len(optList) > 0:
                    for opt in optList:
                        optmax = []
                        optPath = os.path.join(resultFolder, opt)
                        df = pd.read_csv(optPath)
                        dfDist = df["distance"].values.max()
                        optmax.append(dfDist)
                    data.append(max(optmax)/3600.0)
                else:
                    data.append(0)
    return data

def readDataTruck(TractFolder, ccMPath):
    data = os.path.join(TractFolder, "1", "1")
    dataList = os.listdir(data)
    ccM = np.load(ccMPath)
    if len(dataList) == 0:
        return 1000000000
    for d in dataList:
        if "opt" in d:
            continue
        else:
            consumption = 0
            dPath = os.path.join(data, d)
            df = pd.read_csv(dPath)
            customerLst = df["customer"].values.tolist()
            weightLst = df["weight"].values.tolist()

            for i in range(len(customerLst)):
                c = literal_eval(customerLst[i])
                w = literal_eval(weightLst[i])
                totWeight = sum(w)
                for j in range(len(c)-1):
                    dis = ccM[c[j], c[j+1]]
                    # consumption += ((totWeight-w[j])/1000 * dis * 0.000621) * 161.8
                    # by vehicel emission
                    consumption += dis * 0.000621 / 6.5 * 8887
    return consumption

#***************************************************************************
#GET DELIVERY TRUCK C02 EMISSION
# dataFolder = r"Result/TractTruck"
# tractLst = os.listdir(dataFolder)
# tractLst.sort()
# tractRow = []
# for tract in tractLst:
#     print("Analysing Tract: ", tract)
#     tractFolder = os.path.join(dataFolder, tract)
#     ccMPath = os.path.join("Data", "Tract", tract, "ccM.npy")
#     consumption = readDataTruck(tractFolder, ccMPath)
#     tractRow.append(consumption)

# tractDf = pd.DataFrame(tractRow)
# tractDf["Tracts"] = tractLst
# tractDf.to_csv(r"Result/tractTruckCO2_vhicel.csv")


###############################################################################
# GET ROBOT DELIVERY ANALYSIS RESULTS
# "totalDistance"
# "CO2 emission"
# "totalPackagesDelivered"
# "totalCustmerServed"
# "longestDistance"



dataFolder = r"Result/Tract"
tractLst = os.listdir(dataFolder)
tractLst.sort()
tractRow = []
task = "CO2 emission"
for tract in tractLst:
    print("Analysing Tract: ", tract)
    tractFolder = os.path.join(dataFolder, tract)
    data = readDataRobot(tractFolder, task)
    tractRow.append(data)
tractDf = pd.DataFrame(tractRow)
tractDf["Tracts"] = tractLst
tractDf.to_csv(r"Result/tractCO2Emission.csv")
