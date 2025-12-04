# -*- coding: utf-8 -*-
# @Author: gviejo
# @Date:   2022-01-17 15:50:57
# @Last Modified by:   gviejo
# @Last Modified time: 2022-04-11 17:46:22

import numpy as np
import pynapple as nap
from matplotlib.pyplot import *
import pynacollada as pyna

data_directory = '/home/guillaume/pynapple/data/A2929-200711'

data = nap.load_session(data_directory, 'neurosuite')

sleep_ep = data.epochs['sleep']

frequency = 1250.0

lfp = data.load_lfp(channel=15,extension='.eeg',frequency=frequency)

lfpsleep = lfp.restrict(sleep_ep)

signal = pyna.eeg_processing.bandpass_filter(lfpsleep, 100, 300, frequency)


windowLength = 51

from scipy.signal import filtfilt

squared_signal = np.square(signal.values)
window = np.ones(windowLength)/windowLength
nSS = filtfilt(window, 1, squared_signal)
nSS = (nSS - np.mean(nSS))/np.std(nSS)
nSS = nap.Tsd(t = signal.index.values, d = nSS, time_support = signal.time_support)


# Round1 : Detecting Ripple Periods by thresholding normalized signal
low_thres = 1
high_thres = 10

nSS2 = nSS.threshold(low_thres, method='above')
nSS3 = nSS2.threshold(high_thres, method='below')

# Round 2 : Excluding ripples whose length < minRipLen and greater than Maximum Ripple Length
minRipLen = 20 # ms
maxRipLen = 200 # ms

rip_ep = nSS3.time_support
rip_ep = rip_ep.drop_short_intervals(minRipLen, time_units = 'ms')
rip_ep = rip_ep.drop_long_intervals(maxRipLen, time_units = 'ms')

# Round 3 : Merging ripples if inter-ripple period is too short
minInterRippleInterval = 20 # ms


rip_ep = rip_ep.merge_close_intervals(minInterRippleInterval, time_units = 'ms')
rip_ep = rip_ep.reset_index(drop=True)

# Extracting Ripple peak
rip_max = []
rip_tsd = []
for s, e in rip_ep.values:
    tmp = nSS.loc[s:e]
    rip_tsd.append(tmp.idxmax())
    rip_max.append(tmp.max())

rip_max = np.array(rip_max)
rip_tsd = np.array(rip_tsd)

rip_tsd = nap.Tsd(t = rip_tsd, d = rip_max, time_support = sleep_ep)

# Writing for neuroscope the Intervals
data.write_neuroscope_intervals(extension='.rip.evt', isets=rip_ep, name='Ripples')

# Saving ripples time and epochs
data.save_nwb_intervals(rip_ep, 'sleep_ripples')
data.save_nwb_timeseries(rip_tsd, 'sleep_ripples')

# Load ripples times
rip_ep = data.load_nwb_intervals('sleep_ripples')
rip_tsd = data.load_nwb_timeseries('sleep_ripples')



rip_ep1, rip_tsd1 = pyna.eeg_processing.detect_oscillatory_events(
                                            lfp = lfp,
                                            epoch = sleep_ep,
                                            freq_band = (100,300),
                                            thres_band = (1, 10),
                                            duration_band = (0.02,0.2),
                                            min_inter_duration = 0.02
                                            )
