# -*- coding: utf-8 -*-
"""
Created on Tue Dec 21 23:19:41 2021

@author: adrie
"""

import numpy as np
import pynapple as nap

def butter_bandpass(lowcut, highcut, fs, order=5):
	from scipy.signal import butter
	nyq = 0.5 * fs
	low = lowcut / nyq
	high = highcut / nyq
	b, a = butter(order, [low, high], btype='band')
	return b, a

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
	from scipy.signal import lfilter
	b, a = butter_bandpass(lowcut, highcut, fs, order=order)
	y = lfilter(b, a, data)
	return y

def downsample(tsd, up, down):
	import scipy.signal
	
	dtsd = scipy.signal.resample_poly(tsd.values, up, down)
	dt = tsd.as_units('s').index.values[np.arange(0, tsd.shape[0], down)]
	if len(tsd.shape) == 1:		
		return nap.Tsd(dt, dtsd, time_units = 's')
	elif len(tsd.shape) == 2:
		return nap.TsdFrame(dt, dtsd, time_units = 's', columns = list(tsd.columns))

def getPeaksandTroughs(lfp, min_points):
	"""	 
		At 250Hz (1250/5), 2 troughs cannont be closer than 20 (min_points) points (if theta reaches 12Hz);		
	"""
	import scipy.signal
	if isinstance(lfp, nap.time_series.Tsd):
		troughs 		= nap.Tsd(lfp.as_series().iloc[scipy.signal.argrelmin(lfp.values, order =min_points)[0]], time_units = 'us')
		peaks 			= nap.Tsd(lfp.as_series().iloc[scipy.signal.argrelmax(lfp.values, order =min_points)[0]], time_units = 'us')
		tmp 			= nap.Tsd(troughs.realign(peaks, align = 'next').as_series().drop_duplicates('first')) # eliminate double peaks
		peaks			= peaks[tmp.index]
		tmp 			= nap.Tsd(peaks.realign(troughs, align = 'prev').as_series().drop_duplicates('first')) # eliminate double troughs
		troughs 		= troughs[tmp.index]
		return (peaks, troughs)
	elif isinstance(lfp, nap.time_series.TsdFrame):
		peaks 			= nap.TsdFrame(lfp.index.values, np.zeros(lfp.shape))
		troughs			= nap.TsdFrame(lfp.index.values, np.zeros(lfp.shape))
		for i in lfp.keys():
			peaks[i], troughs[i] = getPeaksandTroughs(lfp[i], min_points)
		return (peaks, troughs)

def getPhase(lfp, fmin, fmax, nbins, fsamp, power = False):
	""" Continuous Wavelets Transform
		return phase of lfp in a Tsd array
	"""
	from Wavelets import MyMorlet as Morlet
	if isinstance(lfp, nap.time_series.TsdFrame):
		allphase 		= nap.TsdFrame(lfp.index.values, np.zeros(lfp.shape))
		allpwr 			= nap.TsdFrame(lfp.index.values, np.zeros(lfp.shape))
		for i in lfp.keys():
			allphase[i], allpwr[i] = getPhase(lfp[i], fmin, fmax, nbins, fsamp, power = True)
		if power:
			return allphase, allpwr
		else:
			return allphase			

	elif isinstance(lfp, nap.time_series.Tsd):
		cw 				= Morlet(lfp.values, fmin, fmax, nbins, fsamp)
		cwt 			= cw.getdata()
		cwt 			= np.flip(cwt, axis = 0)
		wave 			= np.abs(cwt)**2.0
		phases 			= np.arctan2(np.imag(cwt), np.real(cwt)).transpose()	
		cwt 			= None
		index 			= np.argmax(wave, 0)
		# memory problem here, need to loop
		phase 			= np.zeros(len(index))	
		for i in range(len(index)) : phase[i] = phases[i,index[i]]
		phases 			= None
		if power: 
			pwrs 		= cw.getpower()		
			pwr 		= np.zeros(len(index))		
			for i in range(len(index)):
				pwr[i] = pwrs[index[i],i]	
			return nap.Tsd(lfp.index.values, phase), nap.Tsd(lfp.index.values, pwr)
		else:
			return nap.Tsd(lfp.index.values, phase)