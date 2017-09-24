## Compiled from Frame2D/Nodes.ipynb on Fri Sep 22 15:44:22 2017

## In [1]:
import math

## In [2]:
class Node(object):
    
    DIRECTIONS = {'FX':0, 'FY':1, 'MZ':2}
    
    def __init__(self,ident,x,y):
        """Initialize a new instance with the given identifier and x-
        and y- coordinate values. The set of constraints is set to empty,
        and the 3 dof numbers are unset."""
        self.id = ident
        self.x = x
        self.y = y
        self.constraints = set()
        self.dofnums = [None] * 3
        
    def add_constraint(self,cname):
        """Add a constrained direction to the set of constraints.  The constraint
        name, cname, must be one of the 3 valid directions (FX, FY or MZ)."""
        c = cname.upper()
        if c not in self.DIRECTIONS:
            raise ValueError('Invalid constraint name: {}'.format(cname))
        self.constraints.add(c)
        
    def to(self,other):
        """Return the directional cosines and distance to the other node as
        a 3-tuple."""
        dx = other.x-self.x
        dy = other.y-self.y
        L = math.sqrt(dx*dx + dy*dy)
        return dx/L,dy/L,L
        
    def __repr__(self):
        return '{}("{}",{},{})'.format(self.__class__.__name__,self.id,self.x,self.y)
