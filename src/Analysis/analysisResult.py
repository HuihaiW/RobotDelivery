import pandas as pd
import numpy as np
import os

dataFolder = r"Result/"
tractCO2 = os.path.join(dataFolder, "tractCO2.csv")
df = pd.read_csv(tractCO2)
