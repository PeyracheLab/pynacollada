"""
Created on Thu Dec 16 23:56:35 2021

@author: apeyra4
"""
import pynapple as nap
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import numpy as np

def assemblyPCA(binnedSpk, epochRef, epochTest = None, method = 'marcenko', numComp = None):
    '''
    Parameters
    ----------
    binSpk : TsdFrame
        DESCRIPTION.
    epochRef : intervalSet
        DESCRIPTION.
    epochTest : list of intervalSets
        DESCRIPTION.
    method : TYPE, optional
        DESCRIPTION. The default is 'marcenko'.
    numComp : TYPE, optional
        DESCRIPTION. The default is 3.

    Returns
    -------
    assemblyAct, a list of TsdFrames

    '''
   
    binRef = binnedSpk.restrict(epochRef).values
    
    # Compute PCA
    comp = assemblyComp(binRef,method = method, numComp = numComp)
    numComp = comp.shape[0]
    print('PCA based assembly activation, using ' + str(numComp) + ' PCs\n')

    # Project test data onto Principal Components
    assemblyAct = assemblyProj(comp, binnedSpk, epochTest);
    
    return assemblyAct, comp


def assemblyICA(binnedSpk, epochRef, epochTest = None, method = 'marcenko', numComp = 3):
    
    binRef = binnedSpk.restrict(epochRef).values
    
    # Compute PCA
    comp = assemblyComp(binRef,method = method, numComp = numComp)
    numComp = comp.shape[0]
    
    #Now compute ICA
    #TODO
    assemblyAct = []
    print(type(assemblyAct[0]))
    return assemblyAct, comp

def assemblyComp(binRef, method = 'marcenko', numComp = None):
    
    pca = PCA()
    zSpkRef = StandardScaler().fit_transform(binRef)
    pca.fit(zSpkRef)
    
    if numComp is None:
        if method == 'marcenko':
            b,n = zSpkRef.shape
            eigValUp = (1 + np.sqrt(b/n)) ** 2
            numComp = sum(i > eigValUp for i in pca.explained_variance_)
        elif method == 'none':
            pass
        else:
            raise ValueError('unrecognized method')
   
    comp = pca.components_[:numComp,:]
    return comp

def assemblyProj(comp, binnedSpk, epochTest = None):
    
   
    if epochTest is None:
        activation = assemblyProj(comp, binnedSpk, epochTest=binnedSpk.time_support) 

    elif isinstance(epochTest,list):
        # If epochTest is a list of IntervalSet, it returns a list of TsdFrame
        assemblyAct = []
        for n in range(len(epochTest)):
            # If epochTest is a list of IntervalSet, we call it for each epoch
            activation = assemblyProj(comp, binnedSpk.restrict(epochTest[n]), epochTest=epochTest[n]) 
            assemblyAct.append(activation)
            
    else:
        if not isinstance(epochTest,nap.IntervalSet):
            raise ValueError('epochTestis not a pynapple IntervalSet object')
         
        # Define the DataFram column names
        columnName = []
        for k in range(len(comp)):
            columnName.append("Comp%d" % k)
         
        #Z-score binned spike trains    
        binTest = binnedSpk.values
        zSpk = StandardScaler().fit_transform(binTest)
        activation = np.zeros((zSpk.shape[0],comp.shape[0]))
        
        # compute projection for each component
        for k in range(comp.shape[0]):
            proj = noDiagProj(comp[k,:], zSpk)
            activation[:,k] = proj
  
        # we transform the dataFrame into a TsdFrame for compatibility with pynapple
        assemblyAct = nap.TsdFrame(t = binnedSpk.restrict(epochTest).times(), d = activation, columns = columnName)   
            
    return assemblyAct

def noDiagProj(pc,zSpk):
    
    proj = np.dot(zSpk,pc)
    # some maths tricks here
    diagTerm = zSpk*np.tile(pc,(zSpk.shape[0],1))
    proj = np.square(proj) - np.sum(np.square(diagTerm),axis=1)
    
    return proj 

def explainedVar(binnedSpk, epochRef, epoch1, epoch2):
    
    
    return None

def assemblyGLM(binnedSpk):
    
    return None

def assemblyFA(binnedSpk):
    
    return None



