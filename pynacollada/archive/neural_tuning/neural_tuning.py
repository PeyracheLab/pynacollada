# -*- coding: utf-8 -*-
# @Author: gviejo
# @Date:   2022-01-17 14:10:40
# @Last Modified by:   gviejo
# @Last Modified time: 2022-01-18 17:40:08
import pynapple as nap
import pandas as pd
import numpy as np

def computePlaceFields(spikes, position, ep, nb_bins = 100, frequency = 120.0, smoothing = 2):
    place_fields = {}
    position_tsd = position.restrict(ep)
    xpos = position_tsd.iloc[:,0]
    ypos = position_tsd.iloc[:,1]
    xbins = np.linspace(xpos.min(), xpos.max()+1e-6, nb_bins+1)
    ybins = np.linspace(ypos.min(), ypos.max()+1e-6, nb_bins+1)    
    for n in spikes:
        position_spike = position_tsd.realign(spikes[n].restrict(ep))
        spike_count,_,_ = np.histogram2d(position_spike.iloc[:,1].values, position_spike.iloc[:,0].values, [ybins,xbins])
        occupancy, _, _ = np.histogram2d(ypos, xpos, [ybins,xbins])
        mean_spike_count = spike_count/(occupancy+1)
        place_field = mean_spike_count*frequency    
        place_fields[n] = pd.DataFrame(index = ybins[0:-1][::-1],columns = xbins[0:-1], data = place_field)
        
    extent = (xbins[0], xbins[-1], ybins[0], ybins[-1]) # USEFUL FOR MATPLOTLIB
    return place_fields, extent

def computeOccupancy(position, ep, nb_bins = 100):
    xpos = position.restrict(ep).iloc[:,0]
    ypos = position.restrict(ep).iloc[:,1]    
    xbins = np.linspace(xpos.min(), xpos.max()+1e-6, nb_bins+1)
    ybins = np.linspace(ypos.min(), ypos.max()+1e-6, nb_bins+1)
    occupancy, _, _ = np.histogram2d(ypos, xpos, [ybins,xbins])
    return occupancy

def findHDCells(tuning_curves, z = 50, p = 0.0001 , m = 1):
	"""
		Peak firing rate larger than 1
		and Rayleigh test p<0.001 & z > 100
	"""
	cond1 = tuning_curves.max()>m
	from pycircstat.tests import rayleigh
	stat = pd.DataFrame(index = tuning_curves.columns, columns = ['pval', 'z'])
	for k in tuning_curves:
		stat.loc[k] = rayleigh(tuning_curves[k].index.values, tuning_curves[k].values)
	cond2 = np.logical_and(stat['pval']<p,stat['z']>z)
	tokeep = stat.index.values[np.where(np.logical_and(cond1, cond2))[0]]
	hd = pd.Series(index = tuning_curves.columns, data = 0)
	hd.loc[tokeep] = 1
	return hd, stat

def computeAngularVelocityTuningCurves(spikes, angle, ep, nb_bins = 61, bin_size = 10000, norm=True):
	tmp 			= pd.Series(index = angle.index.values, data = np.unwrap(angle.values))
	tmp2 			= tmp.rolling(window=100,win_type='gaussian',center=True,min_periods=1).mean(std=10.0)
	time_bins		= np.arange(tmp.index[0], tmp.index[-1]+bin_size, bin_size) # assuming microseconds
	index 			= np.digitize(tmp2.index.values, time_bins)
	tmp3 			= tmp2.groupby(index).mean()
	tmp3.index 		= time_bins[np.unique(index)-1]+bin_size/2
	tmp3 			= nap.Tsd(tmp3)
	tmp4			= np.diff(tmp3.values)/np.diff(tmp3.as_units('s').index.values)
	tmp2 			= nap.Tsd(tmp2)
	tmp4			= np.diff(tmp2.values)/np.diff(tmp2.as_units('s').index.values)	
	velocity 		= nap.Tsd(t=tmp2.index.values[1:], d = tmp4)
	velocity 		= velocity.restrict(ep)	
	bins 			= np.linspace(-2*np.pi, 2*np.pi, nb_bins)
	idx 			= bins[0:-1]+np.diff(bins)/2
	velo_curves		= pd.DataFrame(index = idx, columns = list(spikes.keys()))

	for k in spikes:
		spks 		= spikes[k]
		spks 		= spks.restrict(ep)
		speed_spike = velocity.realign(spks)
		spike_count, bin_edges = np.histogram(speed_spike, bins)
		occupancy, _ = np.histogram(velocity.restrict(ep), bins)
		spike_count = spike_count/(occupancy+1)
		velo_curves[k] = spike_count*(1/(bin_size*1e-6))
		# normalizing by firing rate 
		if norm:
			velo_curves[k] = velo_curves[k]/(len(spikes[k].restrict(ep))/ep.tot_length('s'))

	return velo_curves



#seems there are 2 functions with the same name (see above)
def smoothAngularTuningCurves(tuning_curves, window = 20, deviation = 3.0):
    for i in tuning_curves.columns:
        tcurves = tuning_curves[i]
        padded     = pd.Series(index = np.hstack((tcurves.index.values-(2*np.pi),
                                                tcurves.index.values,
                                                tcurves.index.values+(2*np.pi))),
                            data = np.hstack((tcurves.values, tcurves.values, tcurves.values)))
        smoothed = padded.rolling(window=window,win_type='gaussian',center=True,min_periods=1).mean(std=deviation)        
        tuning_curves[i] = smoothed[tcurves.index]

    return tuning_curves
def smoothAngularTuningCurves(tuning_curves, window = 20, deviation = 3.0):
	new_tuning_curves = {}	
	for i in tuning_curves.columns:
		tcurves = tuning_curves[i]
		offset = np.mean(np.diff(tcurves.index.values))
		padded 	= pd.Series(index = np.hstack((tcurves.index.values-(2*np.pi)-offset,
												tcurves.index.values,
												tcurves.index.values+(2*np.pi)+offset)),
							data = np.hstack((tcurves.values, tcurves.values, tcurves.values)))
		smoothed = padded.rolling(window=window,win_type='gaussian',center=True,min_periods=1).mean(std=deviation)		
		new_tuning_curves[i] = smoothed.loc[tcurves.index]

	new_tuning_curves = pd.DataFrame.from_dict(new_tuning_curves)

	return new_tuning_curves



def computeSpeedTuningCurves(spikes, position, ep, bin_size = 0.1, nb_bins = 20, speed_max = 0.4):
	time_bins 	= np.arange(position.index[0], position.index[-1]+bin_size*1e6, bin_size*1e6)
	index 		= np.digitize(position.index.values, time_bins)
	tmp 		= position.groupby(index).mean()
	tmp.index 	= time_bins[np.unique(index)-1]+(bin_size*1e6)/2
	distance	= np.sqrt(np.power(np.diff(tmp['x']), 2) + np.power(np.diff(tmp['z']), 2))
	speed 		= nap.Tsd(t = tmp.index.values[0:-1]+ bin_size/2, d = distance/bin_size)
	speed 		= speed.restrict(ep)
	bins 		= np.linspace(0, speed_max, nb_bins)
	idx 		= bins[0:-1]+np.diff(bins)/2
	speed_curves = pd.DataFrame(index = idx,columns = np.arange(len(spikes)))
	for k in spikes:
		spks 	= spikes[k]
		spks 	= spks.restrict(ep)
		speed_spike = speed.realign(spks)
		spike_count, bin_edges = np.histogram(speed_spike, bins)
		occupancy, _ = np.histogram(speed, bins)
		spike_count = spike_count/(occupancy+1)
		speed_curves[k] = spike_count/bin_size

	return speed_curves


def computeAccelerationTuningCurves(spikes, position, ep, bin_size = 0.1, nb_bins = 40):
	time_bins 	= np.arange(position.index[0], position.index[-1]+bin_size*1e6, bin_size*1e6)
	index 		= np.digitize(position.index.values, time_bins)
	tmp 		= position.groupby(index).mean()
	tmp.index 	= time_bins[np.unique(index)-1]+(bin_size*1e6)/2
	distance	= np.sqrt(np.power(np.diff(tmp['x']), 2) + np.power(np.diff(tmp['z']), 2))
	speed 		= nap.Tsd(t = tmp.index.values[0:-1]+ bin_size/2, d = distance/bin_size)
	speed 		= speed.restrict(ep)
	speed 		= speed.as_series()
	speed2 		= speed.rolling(window=10, win_type='gaussian', center= True, min_periods=1).mean(std = 1.0)
	accel 		= nap.Tsd(t = speed2.index.values[0:-1] + np.diff(speed2.index.values)/2, d = np.diff(speed2.values))	
	bins 		= np.linspace(accel.min(), accel.max(), nb_bins)
	idx 		= bins[0:-1]+np.diff(bins)/2
	accel_curves = pd.DataFrame(index = idx,columns = np.arange(len(spikes)))
	for k in spikes:
		spks 	= spikes[k]
		spks 	= spks.restrict(ep)
		accel_spike = accel.realign(spks)
		spike_count, bin_edges = np.histogram(accel_spike, bins)
		occupancy, _ = np.histogram(accel, bins)
		spike_count = spike_count/(occupancy+1)
		accel_curves[k] = spike_count/bin_size

	return accel_curves


def centerTuningCurves(tcurve):
	"""
	center tuning curves by peak
	"""
    
    #Added by Adrien on Dec 21st 2021
    from pycircstat.descriptive import mean as circmean

	peak = pd.Series(index=tcurve.columns,data = np.array([circmean(tcurve.index.values, tcurve[i].values) for i in tcurve.columns]))
	new_tcurve = []
	for p in tcurve.columns:	
		x = tcurve[p].index.values - tcurve[p].index[tcurve[p].index.get_loc(peak[p], method='nearest')]
		x[x<-np.pi] += 2*np.pi
		x[x>np.pi] -= 2*np.pi
		tmp = pd.Series(index = x, data = tcurve[p].values).sort_index()
		new_tcurve.append(tmp.values)
	new_tcurve = pd.DataFrame(index = np.linspace(-np.pi, np.pi, tcurve.shape[0]+1)[0:-1], data = np.array(new_tcurve).T, columns = tcurve.columns)
	return new_tcurve

# copied to neural_tuning
def offsetTuningCurves(tcurve, diffs):
	"""
	offseting tuning curves synced by diff
	"""	
	new_tcurve 		= []
	for p in tcurve.columns:	
		x = tcurve[p].index.values - tcurve[p].index[tcurve[p].index.get_loc(diffs[p], method='nearest')]
		x[x<-np.pi] += 2*np.pi
		x[x>np.pi] -= 2*np.pi
		tmp = pd.Series(index = x, data = tcurve[p].values).sort_index()
		new_tcurve.append(tmp.values)
	new_tcurve = pd.DataFrame(index = np.linspace(-np.pi, np.pi, tcurve.shape[0]+1)[0:-1], data = np.array(new_tcurve).T, columns = tcurve.columns)
	return new_tcurve


def computeSpeed(position, ep, bin_size = 0.1):
	time_bins 	= np.arange(position.index[0], position.index[-1]+bin_size*1e6, bin_size*1e6)
	index 		= np.digitize(position.index.values, time_bins)
	tmp 		= position.groupby(index).mean()
	tmp.index 	= time_bins[np.unique(index)-1]+(bin_size*1e6)/2
	distance	= np.sqrt(np.power(np.diff(tmp['x']), 2) + np.power(np.diff(tmp['z']), 2))
	speed 		= nts.Tsd(t = tmp.index.values[0:-1]+ bin_size/2, d = distance/bin_size)
	speed 		= speed.restrict(ep)
	return speed

#########################################################
# INTERPOLATION
# ########################################################
def interpolate(z, x, y, inter, bbox = None):	
	import scipy.interpolate
	xnew = np.arange(x.min(), x.max()+inter, inter)
	ynew = np.arange(y.min(), y.max()+inter, inter)
	if bbox == None:
		f = scipy.interpolate.RectBivariateSpline(y, x, z)
	else:
		f = scipy.interpolate.RectBivariateSpline(y, x, z, bbox = bbox)
	znew = f(ynew, xnew)
	return (xnew, ynew, znew)

def filter_(z, n):
	from scipy.ndimage import gaussian_filter	
	return gaussian_filter(z, n)
