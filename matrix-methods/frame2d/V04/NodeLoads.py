## Compiled from NodeLoads.py on Tue May 24 17:49:49 2016

## In [1]:
import numpy as np
from salib import extend

## In [2]:
class NodeLoad(object):
    
    def __init__(self,fx=0.,fy=0.,mz=0.):
        if type(fx) is np.ndarray and fx.size == 3:
            self.forces= fx.copy()
            return
        self.forces = np.array([fx,fy,mz],dtype=np.float64)
        
    def __mul__(self,scale):
        if scale == 1.0:
            return self
        return self.__class__(self.forces*scale)
    
    __rmul__ = __mul__
        
    def __repr__(self):
        return "{}({},{},{})".format(self.__class__.__name__,*list(self.forces))

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
        return self.forces[ix]

## In [11]:
@extend
class NodeLoad:
    
    @property
    def fx(self):
        return self.forces[0]
    
    @fx.setter
    def fx(self,v):
        self.forces[0] = v
        
    @property
    def fy(self):
        return self.forces[1]
    
    @fy.setter
    def fy(self,v):
        self.forces[1] = v
        
    @property
    def mz(self):
        return self.forces[2]
    
    @mz.setter
    def mz(self,v):
        self.forces[2] = v   

## In [ ]:

