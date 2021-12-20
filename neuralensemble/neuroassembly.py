# -*- coding: utf-8 -*-
"""
Created on Thu Dec 16 23:56:35 2021

@author: apeyra4
"""
import pynapple as nap

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

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
    comp = assemblyComp(binRef,method = method, numComp = cumComp)
    numComp = comp.shape[0]

    # Project test data onto Principal Components
    assemblyAct = assemblyProj(comp, binnedSpk, epochTest);
    
    return assemblyAct, comp


def assemblyICA(binnedSpk, epochRef, epochTest = None, method = 'marcenko', numComp = 3):
    
    binRef = binnedSpk.restrict(epochRef).values
    
    # Compute PCA
    comp = assemblyComp(binRef,method = method, numComp = cumComp)
    numComp = comp.shape[0]
    
    #Now compute ICA
    #TODO
    
    return assemblyAct, comp

def assemblyComp(binRef, method = 'marcenko', numComp = None):
    
    pca = PCA()
    zSpkRef = StandardScaler().fit_transform(binRef)
    pca.fit(zSpkRef)
    
    is numcomp is None
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
    
    # Define the DataFram column names
    columnName = []
    for k in range(numComp):
        columnName.append("Comp%d" % k)
    
    # Z-score binned spike train for each test epoch separately
    zSpkTest = [];
    
    if epochTest is None:
        binTest = binnedSpk.values
        zSpkTest.append(StandardScaler().fit_transform(binTest))
        
    else:
        for n in range(len(epochTest)):
            binTest = binnedSpk.restrict(epochTest[n]).values
            zSpkTest.append(StandardScaler().fit_transform(binTest))
    
    for n in range(len(epoch)):
        
        activation = np.zeros((zSpkTest[n].shape[0],numComp));
        zSpk = zSpkTest[n]
        
        for k in range(comp):
            pc = comp[k,:]
            proj = np.dot(zSpk,pc)
            # some maths tricks here
            diagTerm = zSpk*np.tile(pc,(zSpkS.shape[0],1))
            tmp = np.square(proj) - np.sum(np.square(diagTerm),axis=1)
            activation[:,k] = np.transpose(tmp);
        
        # we transform the dataFrame into a TsdFrame for compatibility with pynapple
        activation = nap.TsdFrame(activation)
        
        # we append these assembly activation to assemblyAct
        assemblyAct.append(activation)
        
    return assemblyAct

def explainedVar(binnedSpk, epochRef, epoch1, epoch2):
    
    
    return None

def assemblyGLM(binnedSpk):
    
    return None

def assemblyFA(binnedSpk):
    
    return None



