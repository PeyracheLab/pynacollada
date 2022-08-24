# -*- coding: utf-8 -*-
# @Author: gviejo
# @Date:   2022-08-24 15:16:57
# @Last Modified by:   gviejo
# @Last Modified time: 2022-08-24 17:03:58


import numpy as np
from matplotlib.pyplot import *
from scipy.io import loadmat
import pynapple as nap
from numba import jit

# LOAD THE DATA
stim = np.squeeze(loadmat('data_RGCs/Stim.mat')['Stim']) # contains stimulus value at each frame
stim_times = np.squeeze(loadmat('data_RGCs/stimtimes.mat')['stimtimes']) # contains time in seconds at each frame (120 Hz)
all_spike_times = [np.squeeze(x) for x in np.squeeze(loadmat('data_RGCs/SpTimes.mat')['SpTimes'])] # time of spikes for 4 neurons (in units of stim frames)


# Putting the data into pynapple
dt = stim_times[1] - stim_times[0]

main_ep = nap.IntervalSet(start=0, end=(stim.size)*dt)
stimulus = nap.Tsd(t = stim_times, d = stim, time_support = main_ep)
spikes = nap.TsGroup(
    {i:nap.Ts(t = all_spike_times[i]) for i in range(len(all_spike_times))},
    time_support = main_ep,
    num_spikes = np.array([len(spk) for spk in all_spike_times])
    )


regressors, offset, p = nap.compute_1d_poisson_glm(spikes, stimulus, dt, 0.2, ep = main_ep)


count = spikes.count(dt)


figure()
plot(count[2])
plot(p[2])