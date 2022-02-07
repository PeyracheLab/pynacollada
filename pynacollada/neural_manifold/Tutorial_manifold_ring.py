# -*- coding: utf-8 -*-
# @Author: gviejo
# @Date:   2022-01-17 23:01:05
# @Last Modified by:   gviejo
# @Last Modified time: 2022-02-07 18:01:14

import numpy as np
import pandas as pd
import pynapple as nap
from matplotlib.pyplot import *
import pynacollada as pyna
from sklearn.manifold import Isomap
from matplotlib.colors import hsv_to_rgb


data_directory = '/home/guillaume/pynapple/data/A2929-200711'

data = nap.load_session(data_directory, 'neurosuite')

spikes = data.spikes.getby_category('location')['adn']
angle = data.position['ry']

tuning_curves = nap.compute_1d_tuning_curves(spikes, angle, 120,  minmax=(0, 2*np.pi))

bin_size = 0.2
count = spikes.count(bin_size, angle.time_support)
count = count.as_dataframe()
rate = np.sqrt(count/bin_size)
rate = rate.rolling(window=50,win_type='gaussian',center=True,min_periods=1, axis = 0).mean(std=2)

projection = Isomap(n_components = 2, n_neighbors = 50).fit_transform(rate.values)


ep = angle.time_support
bins = np.arange(ep.as_units('s').start.iloc[0], ep.as_units('s').end.iloc[-1]+bin_size, bin_size)
tmp = angle.as_units('s').groupby(np.digitize(angle.as_units('s').index.values, bins)-1).mean()

H = tmp.values/(2*np.pi)
HSV = np.vstack((H, np.ones_like(H), np.ones_like(H))).T
RGB = hsv_to_rgb(HSV)


figure()
scatter(projection[:,0], projection[:,1], c = RGB)
show()