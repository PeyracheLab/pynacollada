# -*- coding: utf-8 -*-
"""
Created on Tue Dec 21 14:53:21 2021

@author: adrie
"""


import pynapple as nap
import pandas as pd
from sklearn.preprocessing import StandardScaler
import numpy as np

def bayesian_decoder_1d(spike_counts, bin_size, tuning_curves):
    
    spike_counts_array = spike_counts.values
    proba_angle = np.zeros((spike_counts.shape[0], tuning_curves.shape[0]))

    part1 = np.exp(-(bin_size/1000)*tcurves_array.sum(1))    
    part2 = px
    
    for i in range(len(proba_angle)):
        part3 = np.prod(tcurves_array**spike_counts_array[i], 1)
        p = part1 * part2 * part3
        proba_angle[i] = p/p.sum() # Normalization process here

    proba_angle  = pd.DataFrame(index = spike_counts.index.values, columns = tuning_curves.index.values, data= proba_angle)    

    decoded = nts.Tsd(t = proba_angle.index.values, d = proba_angle.idxmax(1).values, time_units = 'ms')

    return decoded, proba_angle

def latent_decoder_ring(spike_counts, method='isomap', count_nor = 'sqrt'):
    
    from numpy import linalg as LA
    
    spk = spike_counts.values

    match count_norm:
        case 'sqrt':            
            spk = np.sqrt(spk)
        case 'zscore'
            spk = StandardScaler().fit_transform(spk)
        
        
    match method:
        case 'isomap':
            from sklearn.manifold import Isomap
            embedding = Isomap(n_components=2)
            
    spk_transformed = embedding.fit_transform(X)
    
    theta = np.arctan2(spk_transformed[1,:], spk_transformed[0,:])
    rho = LA.norm(spk_transformed, axis=0)          
    
    return theta, rho, embeddings 