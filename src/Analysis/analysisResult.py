import pandas as pd
import numpy as np
import os

def getBaseRobot(num):
    base = num // 5 + 1
    robot = num % 5 + 1
    return base, robot

dataFolder = r"Result/"
tractCO2 = os.path.join(dataFolder, "tractCO2Emission.csv")
df = pd.read_csv(tractCO2).drop(columns="Unnamed: 0")


print(df)
