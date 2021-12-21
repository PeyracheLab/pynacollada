# -*- coding: utf-8 -*-
"""
Created on Wed Dec 15 19:11:53 2021

@author: Adrien Peyrache

This script shows how to use pynapple to compute sleep reactivation, step by step.
See pynacollada_replayExample for a real case example

"""

import pynapple as nap
import pandas as pd
import numpy as np
import seaborn as sns; sns.set_theme()
import matplotlib.pyplot as plt

from scipy import stats

from neuralensemble import assemblyPCA

recDuration = 2000.; #recording duration in secs
sessionEpoch = nap.IntervalSet(start = 0, end = recDuration, time_units = 's')
wakeEpoch = nap.IntervalSet(start = 0, end = 999, time_units = 's')
sleepEp = nap.IntervalSet(start = 1000, end = recDuration, time_units = 's')

# Let's imagine we have done some sleep scoring identifying NREM sleep episodes
nremEp = nap.IntervalSet(start = [1100, 1500], end = [1200, 1700], time_units = 's')

# We just create fake spike trains
spikes =  {}

for s in range(50):
    random_rate = 10 * np.random.rand(1)
    random_times = np.random.uniform(0, recDuration, int(np.rint(recDuration * random_rate)))
    random_times = np.sort(random_times)
    my_spike = nap.Ts(random_times, time_units = 's')
    spikes[s] = my_spike
    
#Now we define pynapple's TsGroup (perfectly suited for spike trains)    
spikeGrp = nap.TsGroup(data = spikes, time_support = sessionEpoch)

#We can immediately bin the spike trains (here in 100ms bins)
binnedSpk = spikeGrp.count(0.1)

epochTest = [];
epochTest.append(nap.IntervalSet(start = [1100,1300], end = [1200,1350], time_units = 's'))
epochTest.append(sleepEp.intersect(nremEp))

### Nw using the neuralensemble module
reactPCA, comp = assemblyPCA(binnedSpk, wakeEpoch, epochTest = epochTest, method = None, numComp = 3)

fig, axes = plt.subplots(2, 1, figsize=(10, 10))
sns.lineplot(ax = axes[0], data=reactPCA[0].as_units('s'))
sns.lineplot(ax = axes[1], data=reactPCA[1].as_units('s'))