#!/usr/bin/env python
# Plot the suppression of a mass function wrt that of another
import pandas as pd
import os
import matplotlib.pyplot as plt
from haloPropertyAnalysis.comparisons import Sim, CompareSims

datastar = '/Users/rbiswas/data/datastar'
M000n1dir = os.path.join(datastar, 'clustering')
M000dir = os.path.join(datastar, 'Testing_z2')

print('For M000', os.listdir(M000dir))
print('For M000n1', os.listdir(M000n1dir))

LCDM = Sim(simulationDir=M000dir, name='M000')
nLCDM = Sim(simulationDir=M000n1dir, name='M000n1')
print('Simulations Loaded')
cmpLCDMnLCDM = CompareSims(LCDM, nLCDM)
df = cmpLCDMnLCDM.comparisons
df.to_csv('M000M000n1comparisons.csv', index=None)
fig = cmpLCDMnLCDM.plotSuppression()
fig.savefig('M000n1M000suppression.pdf')
plt.show()
