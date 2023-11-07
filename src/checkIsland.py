import numpy as np
import os
island = []
tractLst = os.listdir(r"Data/Tract")
for tract in tractLst:
    tractFolder = os.path.join(r"Data/Tract", tract)
    ccM = np.load(os.path.join(tractFolder, "ccM.npy"))
    bcM = np.load(os.path.join(tractFolder, "bcM.npy"))
    ifIsland = False
    for i in range(ccM.shape[0]):
        for j in range(ccM.shape[1]):
            if ccM[i][j] > 100000:
                ifIsland = True
    if ifIsland:
        island.append(tract)

print("Total islands are: ", len(island))
print(island)