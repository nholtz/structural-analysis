## Compiled from NodeLoads.ipynb on Tue Jun  7 15:10:17 2016

## In [1]:
import numpy as np
from salib import extend

## In [2]:
class NodeLoad(object):
    
    def __init__(self,fx=0.,fy=0.,mz=0.):
        if np.isscalar(fx):
            self.forces = np.matrix([fx,fy,mz],dtype=np.float64).T
        else:
            self.forces= fx.copy()
        
    def __mul__(self,scale):
        if scale == 1.0:
            return self
        return self.__class__(self.forces*scale)
    
    __rmul__ = __mul__
        
    def __repr__(self):
        return "{}({},{},{})".format(self.__class__.__name__,*list(np.array(self.forces.T)[0]))

## In [4]:
def makeNodeLoad(data):
    G = data.get
    return NodeLoad(G('FX',0),G('FY',0),G('MZ',0))

## In [6]:
id(NodeLoad)

## In [7]:
@extend
class NodeLoad:
    
    def __getitem__(self,ix):
        return self.forces[ix,0]

## In [11]:
@extend
class NodeLoad:
    
    @property
    def fx(self):
        return self.forces[0,0]
    
    @fx.setter
    def fx(self,v):
        self.forces[0,0] = v
        
    @property
    def fy(self):
        return self.forces[1,0]
    
    @fy.setter
    def fy(self,v):
        self.forces[1,0] = v
        
    @property
    def mz(self):
        return self.forces[2,0]
    
    @mz.setter
    def mz(self,v):
        self.forces[2,0] = v   

## In [ ]:

