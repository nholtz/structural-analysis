## Compiled from MemberLoads.ipynb on Tue Jun  7 15:10:16 2016

## In [1]:
from __future__ import division, print_function

import numpy as np
import sys
from salib import extend

## In [2]:
class EF(object):
    
    """Class EF represents the 6 end forces acting on a 2-D, planar, beam element."""
    
    def __init__(self,c0=0.,v1=0.,m2=0.,c3=0.,v4=0.,m5=0.):
        """Initialize an instance with the 6 end forces.  If the first
        argument is a 6-element array, initialize from a copy of that
        array and ignore any other arguments."""
        if np.isscalar(c0):
            self.fefs = np.matrix([c0,v1,m2,c3,v4,m5],dtype=np.float64).T
        else:
            self.fefs = c0.copy()
        
    def __getitem__(self,ix):
        """Retreive one of the forces by numer.  This allows allows unpacking
        of all 6 end forces into 6 variables using something like:
           c0,v1,m2,c3,v4,m5 = self
        """
        return self.fefs[ix,0]
    
    def __add__(self,other):
        """Add this set of end forces to another, returning the sum."""
        assert type(self) is type(other)
        new = self.__class__(self.fefs+other.fefs)
        return new
    
    def __sub__(self,other):
        """Subtract the other from this set of forces, returning the difference."""
        assert type(self) is type(other)
        new = self.__class__(self.fefs-other.fefs)
        return new
    
    def __mul__(self,scale):
        """Multiply this set of forces by the scalar value, returning the product."""
        if scale == 1.0:
            return self
        return self.__class__(self.fefs*scale)
    
    __rmul__ = __mul__
    
    def __repr__(self):
        return '{}({},{},{},{},{},{})'.format(self.__class__.__name__,*list(np.array(self.fefs.T)[0]))

## In [10]:
@extend
class EF:

    @property
    def c0(self):
        return self.fefs[0,0]
    
    @c0.setter
    def c0(self,v):
        self.fefs[0,0] = v
    
    @property
    def v1(self):
        return self.fefs[1,0]
    
    @v1.setter
    def v1(self,v):
        self.fefs[1,0] = v
    
    @property
    def m2(self):
        return self.fefs[2,0]
    
    @m2.setter
    def m2(self,v):
        self.fefs[2,0] = v
    
    @property
    def c3(self):
        return self.fefs[3,0]
    
    @c3.setter
    def c3(self,v):
        self.fefs[3,0] = v
    
    @property
    def v4(self):
        return self.fefs[4,0]
    
    @v4.setter
    def v4(self,v):
        self.fefs[4,0] = v
    
    @property
    def m5(self):
        return self.fefs[5,0]
    
    @m5.setter
    def m5(self,v):
        self.fefs[5,0] = v

## In [13]:
class MemberLoad(object):
    
    TABLE_MAP = {} # map from load parameter names to column names in table
    
    def fefs(self):
        """Return the complete set of 6 fixed end forces produced by the load."""
        raise NotImplementedError()       
        
    def shear(self,x):
        """Return the shear force that is in equilibrium with that
        produced by the portion of the load to the left of the point at 
        distance 'x'.  'x' may be a scalar or a 1-dimensional array
        of values."""
        raise NotImplementedError()
        
    def moment(self,x):
        """Return the bending moment that is in equilibrium with that
        produced by the portion of the load to the left of the point at 
        distance 'x'.  'x' may be a scalar or a 1-dimensional array
        of values."""
        raise NotImplementedError()

## In [14]:
@extend
class MemberLoad:
    
    @property
    def vpts(self):
        """Return a descriptor of the points at which the shear force must 
        be evaluated in order to draw a proper shear force diagram for this 
        load.  The descriptor is a 3-tuple of the form: (l,r,d) where 'l'
        is the leftmost point, 'r' is the rightmost point and 'd' is the
        degree of the curve between.  One of 'r', 'l' may be None."""
        raise NotImplementedError()
    
    @property
    def mpts(self):
        """Return a descriptor of the points at which the moment must be 
        evaluated in order to draw a proper bending moment diagram for this 
        load.  The descriptor is a 3-tuple of the form: (l,r,d) where 'l'
        is the leftmost point, 'r' is the rightmost point and 'd' is the
        degree of the curve between.  One of 'r', 'l' may be None."""
        raise NotImplementedError()

## In [15]:
class PL(MemberLoad):
    
    TABLE_MAP = {'P':'W1','a':'A'}
    
    def __init__(self,L,P,a):
        self.L = L
        self.P = P
        self.a = a
        
    def fefs(self):
        P = self.P
        L = self.L
        a = self.a
        b = L-a
        m2 = -P*a*b*b/(L*L)
        m5 = P*a*a*b/(L*L)
        v1 = (m2 + m5 - P*b)/L
        v4 = -(m2 + m5 + P*a)/L
        return EF(0.,v1,m2,0.,v4,m5)
    
    def shear(self,x):
        return -self.P*(x>self.a)
    
    def moment(self,x):
        return self.P*(x-self.a)*(x>self.a)
        
    def __repr__(self):
        return '{}(L={},P={},a={})'.format(self.__class__.__name__,self.L,self.P,self.a)

## In [17]:
@extend
class MemberLoad:
    
    EPSILON = 1.0E-6

@extend
class PL:
    
    @property
    def vpts(self):
        return (self.a-self.EPSILON,self.a+self.EPSILON,0)
    
    @property
    def mpts(self):
        return (self.a,None,1)

## In [20]:
class PLA(MemberLoad):
    
    TABLE_MAP = {'P':'W1','a':'A'}
    
    def __init__(self,L,P,a):
        self.L = L
        self.P = P
        self.a = a
        
    def fefs(self):
        P = self.P
        L = self.L
        a = self.a
        c0 = -P*(L-a)/L
        c3 = -P*a/L
        return EF(c0=c0,c3=c3)
    
    def shear(self,x):
        return 0.
    
    def moment(self,x):
        return 0.
        
    def __repr__(self):
        return '{}(L={},P={},a={})'.format(self.__class__.__name__,self.L,self.P,self.a)

## In [23]:
@extend
class PLA:
    
    @property
    def vpts(self):
        return (0.,self.L,0)
    
    @property
    def mpts(self):
        return (0.,self.L,0)

## In [24]:
class UDL(MemberLoad):
    
    TABLE_MAP = {'w':'W1'}
    
    def __init__(self,L,w):
        self.L = L
        self.w = w
        
    def __repr__(self):
        return '{}(L={},w={})'.format(self.__class__.__name__,self.L,self.w)
    
    def fefs(self):
        L = self.L
        w = self.w
        return EF(0.,-w*L/2., -w*L*L/12., 0., -w*L/2., w*L*L/12.)
    
    def shear(self,x):
        l = x*(x>0.)*(x<=self.L) + self.L*(x>self.L)    # length of loaded portion
        return -(l*self.w)
    
    def moment(self,x):
        l = x*(x>0.)*(x<=self.L) + self.L*(x>self.L)   # length of loaded portion
        d = (x-self.L)*(x>self.L)   # distance from loaded portion to x: 0 if x <= L else x-L
        return self.w*l*(l/2.+d)
    
    @property
    def vpts(self):
        return (0.,self.L,1)
    
    @property
    def mpts(self):
        return (0.,self.L,2)

## In [26]:
class LVL(MemberLoad):
    
    TABLE_MAP = {'w1':'W1','w2':'W2','a':'A','b':'B','c':'C'}
    
    def __init__(self,L,w1,w2=None,a=None,b=None,c=None):
        if a is not None and b is not None and c is not None and L != (a+b+c):
            raise Exception('Cannot specify all of a, b & c')
        if a is None:
            if b is not None and c is not None:
                a = L - (b+c)
            else:
                a = 0.
        if c is None:
            if b is not None:
                c = L - (a+b)
            else:
                c = 0.
        if b is None:
            b = L - (a+c)
        if w2 is None:
            w2 = w1
        self.L = L
        self.w1 = w1
        self.w2 = w2
        self.a = a
        self.b = b
        self.c = c
        
    def fefs(self):
        """This mess was generated via sympy.  See:
        ../../examples/cive3203-notebooks/FEM-2-Partial-lvl.ipynb """
        L = float(self.L)
        a = self.a
        b = self.b
        c = self.c
        w1 = self.w1
        w2 = self.w2
        m2 = -b*(15*a*b**2*w1 + 5*a*b**2*w2 + 40*a*b*c*w1 + 20*a*b*c*w2 + 30*a*c**2*w1 + 30*a*c**2*w2 + 3*b**3*w1 + 2*b**3*w2 + 10*b**2*c*w1 + 10*b**2*c*w2 + 10*b*c**2*w1 + 20*b*c**2*w2)/(60.*(a + b + c)**2)
        m5 = b*(20*a**2*b*w1 + 10*a**2*b*w2 + 30*a**2*c*w1 + 30*a**2*c*w2 + 10*a*b**2*w1 + 10*a*b**2*w2 + 20*a*b*c*w1 + 40*a*b*c*w2 + 2*b**3*w1 + 3*b**3*w2 + 5*b**2*c*w1 + 15*b**2*c*w2)/(60.*(a + b + c)**2)
        v4 = -(b*w1*(a + b/2.) + b*(a + 2*b/3.)*(-w1 + w2)/2. + m2 + m5)/L
        v1 = -b*(w1 + w2)/2. - v4
        return EF(0.,v1,m2,0.,v4,m5)
    
    def __repr__(self):
        return '{}(L={},w1={},w2={},a={},b={},c={})'               .format(self.__class__.__name__,self.L,self.w1,self.w2,self.a,self.b,self.c)
        
    def shear(self,x):
        c = (x>self.a+self.b)    # 1 if x > A+B else 0
        l = (x-self.a)*(x>self.a)*(1.-c) + self.b*c  # length of load portion to the left of x
        return -(self.w1 + (self.w2-self.w1)*(l/self.b)/2.)*l        
        
    def moment(self,x):
        c = (x>self.a+self.b)    # 1 if x > A+B else 0
        #           note: ~c doesn't work if x is scalar, thus we use 1-c
        l = (x-self.a)*(x>self.a)*(1.-c) + self.b*c  # length of load portion to the left of x
        d = (x-(self.a+self.b))*c                  # distance from right end of load portion to x
        return ((self.w1*(d+l/2.)) + (self.w2-self.w1)*(l/self.b)*(d+l/3.)/2.)*l
    
    @property
    def vpts(self):
        return (self.a,self.a+self.b,1 if self.w1==self.w2 else 2)
    
    @property
    def mpts(self):
        return (self.a,self.a+self.b,2 if self.w1==self.w2 else 3)

## In [27]:
class CM(MemberLoad):
    
    TABLE_MAP = {'M':'W1','a':'A'}
    
    def __init__(self,L,M,a):
        self.L = L
        self.M = M
        self.a = a
        
    def fefs(self):
        L = float(self.L)
        A = self.a
        B = L - A
        M = self.M
        m2 = B*(2.*A - B)*M/L**2
        m5 = A*(2.*B - A)*M/L**2
        v1 = (M + m2 + m5)/L
        v4 = -v1
        return EF(0,v1,m2,0,v4,m5)
    
    def shear(self,x):
        return x*0.
    
    def moment(self,x):
        return -self.M*(x>self.A)
    
    @property
    def vpts(self):
        return (None,None,0)
    
    @property
    def mpts(self):
        return (self.A-self.EPSILON,self.A+self.EPSILON,1)
    
    def __repr__(self):
        return '{}(L={},M={},a={})'.format(self.__class__.__name__,self.L,self.M,self.a)

## In [28]:
def makeMemberLoad(L,data,ltype=None):
    def all_subclasses(cls):
        _all_subclasses = []
        for subclass in cls.__subclasses__():
            _all_subclasses.append(subclass)
            _all_subclasses.extend(all_subclasses(subclass))
        return _all_subclasses

    if ltype is None:
        ltype = data.get('TYPE',None)
    for c in all_subclasses(MemberLoad):
        if c.__name__ == ltype and hasattr(c,'TABLE_MAP'):
            MAP = c.TABLE_MAP
            argv = {k:data[MAP[k]] for k in MAP.keys()}
            return c(L,**argv)
    raise Exception('Invalid load type: {}'.format(ltype))

## In [30]:
def unmakeMemberLoad(load):
    type = load.__class__.__name__
    ans = {'TYPE':type}
    for a,col in load.TABLE_MAP.items():
        ans[col] = getattr(load,a)
    return ans

## In [ ]:

