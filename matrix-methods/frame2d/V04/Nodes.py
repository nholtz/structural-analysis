## Compiled from Nodes.py on Sun May 22 17:01:09 2016

## In [2]:
import salib as sl
import math

## In [1]:
class Node(object):
    
    DIRECTIONS = {'FX':0, 'FY':1, 'MZ':2}
    
    def __init__(self,ident,x,y):
        self.id = ident
        self.x = x
        self.y = y
        self.constraints = set()
        self.dofnums = [None] * 3
        
    def add_constraint(self,cname):
        c = cname.upper()
        if c not in self.DIRECTIONS:
            raise Exception('Invalid constraint name: {}'.format(cname))
        self.constraints.add(c)
        
    def to(self,other):
        """Return the directional cosines and distance to the other node."""
        dx = other.x-self.x
        dy = other.y-self.y
        L = math.sqrt(dx*dx + dy*dy)
        return dx/L,dy/L,L
        
    def __repr__(self):
        return '{}("{}",{},{})'.format(self.__class__.__name__,self.id,self.x,self.y)

## In [ ]:

