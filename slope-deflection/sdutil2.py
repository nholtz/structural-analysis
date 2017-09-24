from __future__ import division

class EF(object):
    
    """Instances store the four End Forces for a segment, and allow
    two sets of end forces to be added together and multiplied
    by a scalar.  m0 is left end moment, m1 is right end moment. 
    v0, v1 are left and right end shears. 
    SD sign convention: moments and rotations +ive clockwise, 
    end shears and displacements causing +ive rotation of the 
    segment are +ive. """
    
    def __init__(self,L,m0,m1,v0,v1):
        self.L = L
        self.efs = [m0,m1,v0,v1]
        self.loads = []

    @property
    def m0(self):
        return self.efs[0]

    @property
    def m1(self):
        return self.efs[1]

    @property
    def v0(self):
        return self.efs[2]

    @property
    def v1(self):
        return self.efs[3]
        
    def __add__(self,other):
        """Implement the addition operator."""
        assert self.L == other.L, "Lengths must match: {} != {}".format(self.L,other.L)
        return EF(self.L,self.m0+other.m0,self.m1+other.m1,self.v0+other.v0,self.v1+other.v1)
    
    def __mul__(self,f):
        """Implement the scalar multiplcation operation."""
        return EF(self.L,self.m0*f,self.m1*f,self.v0*f,self.v1*f)
    
    def __rmul__(self,f):
        """Implement the left scalar multiplcation operation."""
        return EF(self.L,self.m0*f,self.m1*f,self.v0*f,self.v1*f)
    
    def __getitem__(self,ix):
        """Return end forces accessed by subscript 0 to 3."""
        return self.efs[ix]
    
    def __repr__(self):
        return "{}({},{},{},{},{})".format(self.__class__.__name__,self.L,*self.efs)

class FEF(object):
    
    """Methods to calculate the fixed end forces, (moments and shears), 
    due to loads of various types.  All methods here return an EF object,
    which contains the span length, the moments at either end, and the shears
    at either end."""

    @staticmethod
    def udl(L,w):
        """Return FEMs and shears due to a full-span UDL.  Distributed load intensity = w.
        Span = L"""
        return EF(L,-w*L*L/12,w*L*L/12,w*L/2,-w*L/2)

    @staticmethod
    def p(L,P,a):
        """Return FEMs and shears due to a single concentrated force, P, a distance, a,
        from the left end.  Span = L."""
        b = L - a
        m0 = -P*a*b*b/(L*L)
        m1 = P*a*a*b/(L*L)
        v1 = -(m0 + m1 + P*a)/L
        v0 = -(m0 + m1 - P*b)/L
        return EF(L,m0,m1,v0,v1)
 
    @staticmethod
    def lvl(L,w1,w2=None,a=None,b=None,c=None):
        """Return the FEMs and shears due to a linearly varying distributed load over
        a portion of the span.  Usage:
        
          FEF.lvl(L,w1,w2,a,b,c)
          
        L = span, w1 = intensity at left, w2 = intensity at right, a = distance from
        left end to left edge of load, b = length of load, c = distance from right 
        edge of load to right end of span."""
        
        if a is not None and b is not None and c is not None and L != (a+b+c):
            raise ValueError('Cannot specify all of a, b & c')
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
            
        m0 = -b*(15*a*b**2*w1 + 5*a*b**2*w2 + 40*a*b*c*w1 + 20*a*b*c*w2 + 30*a*c**2*w1 + 
                 30*a*c**2*w2 + 3*b**3*w1 + 2*b**3*w2 + 10*b**2*c*w1 + 10*b**2*c*w2 + 
                 10*b*c**2*w1 + 20*b*c**2*w2)/(60.*(a + b + c)**2)
        m1 = b*(20*a**2*b*w1 + 10*a**2*b*w2 + 30*a**2*c*w1 + 30*a**2*c*w2 + 10*a*b**2*w1 + 
                10*a*b**2*w2 + 20*a*b*c*w1 + 40*a*b*c*w2 + 2*b**3*w1 + 3*b**3*w2 + 
                5*b**2*c*w1 + 15*b**2*c*w2)/(60.*(a + b + c)**2)
        v1 = -(b*w1*(a + b/2.) + b*(a + 2*b/3.)*(-w1 + w2)/2. + m0 + m1)/L
        v0 = b*(w1 + w2)/2. + v1
        return EF(L,m0,m1,v0,v1)
    
    @staticmethod
    def cm(L,M,a):
        """Return the FEMs and shears due to a single concentrated moment of M
        a distance a from the left support."""
        b = L - a
        m0 = b*(2.*a - b)*M/L**2
        m1 = a*(2.*b - a)*M/L**2
        v0 = (M + m0 + m1)/L
        v1 = -v0
        return EF(L,m0,m1,v0,v1)       


def SD(L,EI,t0,t1,d01=0):
    """Return the end moments and shears of a segment as computed by the slope 
    deflection equations.
       L = length, 
       EI = stiffness, 
       t0 = rotation at end 0 (left), 
       t1 = rotation at end 1, 
       d01 = relative lateral displacment end 0 to end 1.  
    SD sign convention: moments and rotation are +ive CW, 
    relative displacement d01 is +ive for CW rotation of chord."""
    m0 = (EI/L)*(4*t0 + 2*t1 - 6*d01/L)
    m1 = (EI/L)*(2*t0 + 4*t1 - 6*d01/L)
    v1 = -(m0 + m1)/L
    v0 = v1
    return EF(L,m0,m1,v0,v1)
