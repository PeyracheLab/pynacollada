# -*- coding: utf-8 -*-
"""
Created on Tue Dec 21 22:00:09 2021

@author: adrie
"""

import scipy
import pynapple as nap
import numpy as np

def refineSleepFromAccel(acceleration, sleep_ep):
	vl = acceleration[0].restrict(sleep_ep)
	vl = vl.as_series().diff().abs().dropna()	
	a, _ = scipy.signal.find_peaks(vl, 0.025)
	peaks = nap.Tsd(vl.iloc[a])
	duration = np.diff(peaks.as_units('s').index.values)
	interval = nap.IntervalSet(start = peaks.index.values[0:-1], end = peaks.index.values[1:])

	newsleep_ep = interval.iloc[duration>15.0]
	newsleep_ep = newsleep_ep.reset_index(drop=True)
	newsleep_ep = newsleep_ep.merge_close_intervals(100000, time_units ='us')

	newsleep_ep	= sleep_ep.intersect(newsleep_ep)

	return newsleep_ep