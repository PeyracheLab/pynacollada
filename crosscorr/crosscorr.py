# -*- coding: utf-8 -*-
"""
Created on Tue Dec 21 21:53:05 2021

@author: adrie
"""

import numpy as np
import pynapple as nap
import pandas as pd
from itertools import combinations

def compute_AllPairsCrossCorrs(spks, ep, binsize=10, nbins = 2000, norm = False):
	"""
		
	"""	
	neurons = list(spks.keys())
	times = np.arange(0, binsize*(nbins+1), binsize) - (nbins*binsize)/2
	cc = pd.DataFrame(index = times, columns = list(combinations(neurons, 2)))
		
	for i,j in cc.columns:		
		spk1 = spks[i].restrict(ep).as_units('ms').index.values
		spk2 = spks[j].restrict(ep).as_units('ms').index.values		
		tmp = nap.crossCorr(spk1, spk2, binsize, nbins)		
		fr = len(spk2)/ep.tot_length('s')
		if norm:
			cc[(i,j)] = tmp/fr
		else:
			cc[(i,j)] = tmp
	return cc


def compute_CrossCorrs(spks, ep, binsize=10, nbins = 2000, norm = False):
	"""
		
	"""	
	neurons = list(spks.keys())
	times = np.arange(0, binsize*(nbins+1), binsize) - (nbins*binsize)/2
	cc = pd.DataFrame(index = times, columns = list(combinations(neurons, 2)))
		
	for i,j in cc.columns:		
		spk1 = spks[i].restrict(ep).as_units('ms').index.values
		spk2 = spks[j].restrict(ep).as_units('ms').index.values		
		tmp = nap.crossCorr(spk1, spk2, binsize, nbins)		
		fr = len(spk2)/ep.tot_length('s')
		if norm:
			cc[(i,j)] = tmp/fr
		else:
			cc[(i,j)] = tmp
	return cc

def compute_AutoCorrs(spks, ep, binsize = 5, nbins = 200):
	# First let's prepare a pandas dataframe to receive the data
	times = np.arange(0, binsize*(nbins+1), binsize) - (nbins*binsize)/2	
	autocorrs = pd.DataFrame(index = times, columns = list(spks.keys()))
	firing_rates = pd.Series(index = list(spks.keys()))

	# Now we can iterate over the dictionnary of spikes
	for i in spks:
		# First we extract the time of spikes in ms during wake
		spk_time = spks[i].restrict(ep).as_units('ms').index.values
		# Calling the crossCorr function
		autocorrs[i] = nap.crossCorr(spk_time, spk_time, binsize, nbins)
		# Computing the mean firing rate
		firing_rates[i] = len(spk_time)/ep.tot_length('s')

	# We can divide the autocorrs by the firing_rates
	autocorrs = autocorrs / firing_rates

	# And don't forget to replace the 0 ms for 0
	autocorrs.loc[0] = 0.0
	return autocorrs, firing_rates