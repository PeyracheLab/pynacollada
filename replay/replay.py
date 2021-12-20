# -*- coding: utf-8 -*-
"""
Created on Thu Dec 16 23:56:35 2021

@author: apeyra4
"""
import pynapple as nap

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

def reactPCA(binnedSpk, epochRef, epochTest = None, method = 'marcenko', numComp = 3):
    '''
    Parameters
    ----------
    binSpk : TsdFrame
        DESCRIPTION.
    epochRef : intervalSet
        DESCRIPTION.
    epochTest : array of intervalSets
        DESCRIPTION.
    method : TYPE, optional
        DESCRIPTION. The default is 'marcenko'.
    numComp : TYPE, optional
        DESCRIPTION. The default is 3.

    Returns
    -------
    reactStrength, an array of TsdFrames

    '''
   
    
    binRef = binnedSpk.restrict(epochRef).values
    
    # Compute PCA
    pca = PCA()
    zSpkRef = StandardScaler().fit_transform(binRef)
    pca.fit(zSpkRef)
    
    if method == 'marcenko':
        b,n = zSpkRef.shape
        eigValUp = (1 + np.sqrt(b/n)) ** 2
        numComp = sum(i > eigValUp for i in pca.explained_variance_)
    elif method == 'none':
        pass
    else:
        raise ValueError('unrecognized method')
    
    # Z-score binned spike train for each test epoch separately
    zSpkTest = [];
    
    if epochTest is None:
        binTest = binnedSpk.values
        zSpkTest.append(StandardScaler().fit_transform(binTest))
        
    else:
        for n in range(len(epochTest)):
            binTest = binnedSpk.restrict(epochRef[n]).values
            zSpkTest.append(StandardScaler().fit_transform(binTest))
            
    # We project onto the first three PCs

    reactPCA = np.zeros((zSpkSleep.shape[0],3))
        
    for n in range(3):
        pc = pca.components_[n,:]
        proj = np.dot(zSpkSleep,pc)
        #yes, some maths tricks here
        diagTerm = zSpkSleep*np.tile(pc,(zSpkSleep.shape[0],1))
        tmp = np.square(proj) - np.sum(np.square(diagTerm),axis=1)
        reactPCA[:,n] = np.transpose(tmp);

    # Here, it is time to transform the data back into tsdFrame.
    reactPCA = pd.DataFrame(data=reactPCA, index=binnedSpk.restrict(sleepEp).times(), columns=['PC1','PC2','PC3'])
    # and to pynapple (TsdFrame object) so that time units is a no brainer
    reactPCA = nap.TsdFrame(reactPCA)

    
    return reactStrength