"""
Created on Thu Dec 16 23:56:35 2021

@author: apeyra4
"""
import pynapple as nap
import numpy as np

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

def assemblyPCA(spike_counts, epochRef, epochTest = None, method = 'marcenko', numComp = None):
    '''
    Parameters
    ----------
    spike_counts : TYPE
        Description
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
    
    Deleted Parameters
    ------------------
    binSpk : TsdFrame
        DESCRIPTION.
    
    '''
   
    binRef = spike_counts.restrict(epochRef).values
    
    # Compute PCA
    comp = assemblyComp(binRef,method = method, numComp = numComp)
    numComp = comp.shape[0]
    print('PCA based assembly activation, using ' + str(numComp) + ' PCs\n')

    # Project test data onto Principal Components
    assemblyAct = assemblyProj(comp, spike_counts, epochTest);
    
    return assemblyAct, comp


def assemblyICA(spike_counts, epochRef, epochTest = None, method = 'marcenko', numComp = 3):
    """Summary
    
    Parameters
    ----------
    spike_counts : TYPE
        Description
    epochRef : TYPE
        Description
    epochTest : None, optional
        Description
    method : str, optional
        Description
    numComp : int, optional
        Description
    
    Returns
    -------
    TYPE
        Description
    """
    binRef = spike_counts.restrict(epochRef).values
    
    # Compute PCA
    comp = assemblyComp(binRef,method = method, numComp = numComp)
    numComp = comp.shape[0]
    
    #Now compute ICA
    #TODO
    assemblyAct = []
    print(type(assemblyAct[0]))
    return assemblyAct, comp

def assemblyComp(spike_counts, method = 'marcenko', numComp = None):
    """Summary
    
    Parameters
    ----------
    spike_counts : TYPE
        Description
    method : str, optional
        Description
    numComp : None, optional
        Description
    
    Returns
    -------
    TYPE
        Description
    
    Raises
    ------
    ValueError
        Description
    """
    pca = PCA()
    zSpkRef = StandardScaler().fit_transform(spike_counts)
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

def assemblyProj(comp, spike_counts, epochTest = None):
    """Summary
    
    Parameters
    ----------
    comp : TYPE
        Description
    spike_counts : TYPE
        Description
    epochTest : None, optional
        Description
    
    Returns
    -------
    TYPE
        Description
    
    Raises
    ------
    ValueError
        Description
    """
    if epochTest is None:
        activation = assemblyProj(comp, spike_counts, epochTest=spike_counts.time_support) 

    elif isinstance(epochTest,list):
        # If epochTest is a list of IntervalSet, it returns a list of TsdFrame
        assemblyAct = []
        for n in range(len(epochTest)):
            # If epochTest is a list of IntervalSet, we call it for each epoch
            activation = assemblyProj(comp, spike_counts.restrict(epochTest[n]), epochTest=epochTest[n]) 
            assemblyAct.append(activation)
            
    else:
        if not isinstance(epochTest,nap.IntervalSet):
            raise ValueError('epochTestis not a pynapple IntervalSet object')
         
        # Define the DataFram column names
        columnName = []
        for k in range(len(comp)):
            columnName.append("Comp%d" % k)
         
        #Z-score binned spike trains    
        binTest = spike_counts.values
        zSpk = StandardScaler().fit_transform(binTest)
        activation = np.zeros((zSpk.shape[0],comp.shape[0]))
        
        # compute projection for each component
        for k in range(comp.shape[0]):
            proj = noDiagProj(comp[k,:], zSpk)
            activation[:,k] = proj
  
        # we transform the dataFrame into a TsdFrame for compatibility with pynapple
        assemblyAct = nap.TsdFrame(t = spike_counts.restrict(epochTest).times(), d = activation, columns = columnName)   
            
    return assemblyAct

def noDiagProj(pc,zSpk):
    """Summary
    
    Parameters
    ----------
    pc : TYPE
        Description
    zSpk : TYPE
        Description
    
    Returns
    -------
    TYPE
        Description
    """
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



