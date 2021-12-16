# -*- coding: utf-8 -*-
"""
Created on Wed Dec 15 19:11:53 2021

@author: apeyra4
"""


import pynapple as nap
import pandas as pd
import numpy as np
import seaborn as sns; sns.set_theme()
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from scipy import stats

sessionEpoch = nap.IntervalSet(start = 0, end = 3000, time_units = 's')
wakeEpoch = nap.IntervalSet(start = 1000, end = 1999, time_units = 's')
sleepPre = nap.IntervalSet(start = 0, end = 999, time_units = 's')
sleepPost = nap.IntervalSet(start = 2000, end = 3000, time_units = 's')

spikes =  {}

for s in range(50):
    random_rate = 10 * np.random.rand(1)
    random_times = np.random.uniform(0, 3000, int(np.rint(3000.0 * random_rate)))
    random_times = np.sort(random_times)
    my_spike = nap.Ts(random_times, time_units = 's')
    spikes[s] = my_spike
    
spikeGrp = nap.TsGroup(data = spikes, time_support = sessionEpoch)

binnedSpk = spikeGrp.count(0.1)

binWake = binnedSpk.restrict(wakeEpoch).values
Cwake = np.corrcoef(np.transpose(binWake))

# Let's plot the correlation matrix, excluding the diagonal elements
mask = np.zeros_like(Cwake)
mask[np.diag_indices_from(mask)] = True
ax = sns.heatmap(Cwake, mask=mask)

### Let's start with PCA-based reactivation method
pca = PCA()
zSpkWake = StandardScaler().fit_transform(binWake)
pca.fit(zSpkWake)

# Plot the eigenvalues. Here it's all random, should be distributed around 1
sns.lineplot(data=pca.explained_variance_)

#And the first three eigenvectors (the PCs)
ax = sns.heatmap(pca.components_[:3,:])
ax.set_xlabel("Neurons", fontsize = 15)
ax.set_ylabel("PCs", fontsize = 15)

# Conpute the z-scored binned spike trains durint sleep
binPre = binnedSpk.restrict(sleepPre).values
binPost = binnedSpk.restrict(sleepPost).values
zSpkPre = StandardScaler().fit_transform(binPre)
zSpkPost = StandardScaler().fit_transform(binPost)

# We project onto the first three PCs

reactPCA = np.zeros((zSpkPre.shape[0],3))
    
for n in range(3):
    pc = pca.components_[n,:]
    proj = np.dot(zSpkPre,pc)
    #yes, some maths tricks here
    diagTerm = zSpkPre*np.tile(pc,(zSpkPre.shape[0],1))
    tmp = np.square(proj) - np.sum(np.square(diagTerm),axis=1)
    reactPCA[:,n] = np.transpose(tmp);

# Here, it is time to transform the data back into tsdFrame.
reactPCA = pd.DataFrame(data=reactPCA, index=binnedSpk.restrict(sleepPre).index)

####### THIS WORKS BUT HOW TO DISPLAY TIME IN SEC??
x = sns.lineplot(data=reactPCA)
ax.set_ylabel("Reactivation Strength", fontsize = 15)


reactPCA = nap.TsdFrame(reactPCA)

####### THIS DOES NOT WORKS, WHY???
ax = sns.lineplot(data=reactPCA.as_dataframe)
ax.set_ylabel("Reactivation Strength", fontsize = 15)








