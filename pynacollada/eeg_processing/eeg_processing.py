# -*- coding: utf-8 -*-
# @Author: gviejo
# @Date:   2022-01-17 14:10:40
# @Last Modified by:   gviejo
# @Last Modified time: 2022-04-11 17:57:39
import numpy as np
import pynapple as nap
from scipy.signal import butter, lfilter, filtfilt

def _butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def _butter_bandpass_filter(data, lowcut, highcut, fs, order=4):
    b, a = _butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

def bandpass_filter(data, lowcut, highcut, fs, order=4):
    """
    Bandpass filtering the LFP.
    
    Parameters
    ----------
    data : Tsd/TsdFrame
        Description
    lowcut : TYPE
        Description
    highcut : TYPE
        Description
    fs : TYPE
        Description
    order : int, optional
        Description
    
    Raises
    ------
    RuntimeError
        Description
    """
    time_support = data.time_support
    time_index = data.as_units('s').index.values
    if type(data) is nap.TsdFrame:
        tmp = np.zeros(data.shape)
        for i,c in enumerate(data.columns):
            tmp[:,i] = bandpass_filter(data[c], lowcut, highcut, fs, order)

        return nap.TsdFrame(
            t = time_index,
            d = tmp,
            time_support = time_support,
            time_units = 's',
            columns = data.columns)

    elif type(data) is nap.Tsd:
        flfp = _butter_bandpass_filter(data.values, lowcut, highcut, fs, order)
        return nap.Tsd(
            t=time_index,
            d=flfp,
            time_support=time_support,
            time_units='s')

    else:
        raise RuntimeError("Unknow format. Should be Tsd/TsdFrame")

def detect_oscillatory_events(lfp, epoch, freq_band, thres_band, duration_band, min_inter_duration, wsize=51):
    """
    Simple helper for detecting oscillatory events (e.g. ripples, spindles)
    
    Parameters
    ----------
    lfp : Tsd
        Should be a single channel raw lfp
    epoch : IntervalSet
        The epoch for restricting the detection
    freq_band : tuple
        The (low, high) frequency to bandpass the signal
    thres_band : tuple
        The (min, max) value for thresholding the normalized squared signal after filtering
    duration_band : tuple
        The (min, max) duration of an event in second
    min_inter_duration : float
        The minimum duration between two events otherwise they are merged (in seconds)
    wsize : int, optional
        The size of the window for digitial filtering
    
    Returns
    -------
    IntervalSet
        The intervalSet detected
    Tsd
        Timeseries containing the peaks of the oscillations
    """
    lfp = lfp.restrict(epoch)
    frequency = lfp.rate
    signal = bandpass_filter(lfp, freq_band[0], freq_band[1], frequency)
    squared_signal = np.square(signal.values)
    window = np.ones(wsize)/wsize
    nSS = filtfilt(window, 1, squared_signal)
    nSS = (nSS - np.mean(nSS))/np.std(nSS)
    nSS = nap.Tsd(t = signal.index.values, d=nSS, time_support=epoch)

    # Round1 : Detecting Oscillation Periods by thresholding normalized signal
    nSS2 = nSS.threshold(thres_band[0], method='above')
    nSS3 = nSS2.threshold(thres_band[1], method='below')

    # Round 2 : Excluding oscillation whose length < min_duration and greater than max_duration
    osc_ep = nSS3.time_support
    osc_ep = osc_ep.drop_short_intervals(duration_band[0], time_units = 's')
    osc_ep = osc_ep.drop_long_intervals(duration_band[1], time_units = 's')

    # Round 3 : Merging oscillation if inter-oscillation period is too short
    osc_ep = osc_ep.merge_close_intervals(min_inter_duration, time_units = 's')
    osc_ep = osc_ep.reset_index(drop=True)

    # Extracting Oscillation peak
    osc_max = []
    osc_tsd = []
    for s, e in osc_ep.values:
        tmp = nSS.loc[s:e]
        osc_tsd.append(tmp.idxmax())
        osc_max.append(tmp.max())

    osc_max = np.array(osc_max)
    osc_tsd = np.array(osc_tsd)

    osc_tsd = nap.Tsd(t=osc_tsd, d=osc_max, time_support=epoch)

    return osc_ep, osc_tsd



# def downsample(tsd, up, down):
#   import scipy.signal
    
#   dtsd = scipy.signal.resample_poly(tsd.values, up, down)
#   dt = tsd.as_units('s').index.values[np.arange(0, tsd.shape[0], down)]
#   if len(tsd.shape) == 1:     
#       return nap.Tsd(dt, dtsd, time_units = 's')
#   elif len(tsd.shape) == 2:
#       return nap.TsdFrame(dt, dtsd, time_units = 's', columns = list(tsd.columns))

# def getPeaksandTroughs(lfp, min_points):
#   """  
#       At 250Hz (1250/5), 2 troughs cannont be closer than 20 (min_points) points (if theta reaches 12Hz);     
#   """
#   import scipy.signal
#   if isinstance(lfp, nap.time_series.Tsd):
#       troughs         = nap.Tsd(lfp.as_series().iloc[scipy.signal.argrelmin(lfp.values, order =min_points)[0]], time_units = 'us')
#       peaks           = nap.Tsd(lfp.as_series().iloc[scipy.signal.argrelmax(lfp.values, order =min_points)[0]], time_units = 'us')
#       tmp             = nap.Tsd(troughs.realign(peaks, align = 'next').as_series().drop_duplicates('first')) # eliminate double peaks
#       peaks           = peaks[tmp.index]
#       tmp             = nap.Tsd(peaks.realign(troughs, align = 'prev').as_series().drop_duplicates('first')) # eliminate double troughs
#       troughs         = troughs[tmp.index]
#       return (peaks, troughs)
#   elif isinstance(lfp, nap.time_series.TsdFrame):
#       peaks           = nap.TsdFrame(lfp.index.values, np.zeros(lfp.shape))
#       troughs         = nap.TsdFrame(lfp.index.values, np.zeros(lfp.shape))
#       for i in lfp.keys():
#           peaks[i], troughs[i] = getPeaksandTroughs(lfp[i], min_points)
#       return (peaks, troughs)

# def getPhase(lfp, fmin, fmax, nbins, fsamp, power = False):
#   """ Continuous Wavelets Transform
#       return phase of lfp in a Tsd array
#   """
#   from Wavelets import MyMorlet as Morlet
#   if isinstance(lfp, nap.time_series.TsdFrame):
#       allphase        = nap.TsdFrame(lfp.index.values, np.zeros(lfp.shape))
#       allpwr          = nap.TsdFrame(lfp.index.values, np.zeros(lfp.shape))
#       for i in lfp.keys():
#           allphase[i], allpwr[i] = getPhase(lfp[i], fmin, fmax, nbins, fsamp, power = True)
#       if power:
#           return allphase, allpwr
#       else:
#           return allphase         

#   elif isinstance(lfp, nap.time_series.Tsd):
#       cw              = Morlet(lfp.values, fmin, fmax, nbins, fsamp)
#       cwt             = cw.getdata()
#       cwt             = np.flip(cwt, axis = 0)
#       wave            = np.abs(cwt)**2.0
#       phases          = np.arctan2(np.imag(cwt), np.real(cwt)).transpose()    
#       cwt             = None
#       index           = np.argmax(wave, 0)
#       # memory problem here, need to loop
#       phase           = np.zeros(len(index))  
#       for i in range(len(index)) : phase[i] = phases[i,index[i]]
#       phases          = None
#       if power: 
#           pwrs        = cw.getpower()     
#           pwr         = np.zeros(len(index))      
#           for i in range(len(index)):
#               pwr[i] = pwrs[index[i],i]   
#           return nap.Tsd(lfp.index.values, phase), nap.Tsd(lfp.index.values, pwr)
#       else:
#           return nap.Tsd(lfp.index.values, phase)