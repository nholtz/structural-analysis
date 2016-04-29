from __future__ import division

class EF(object):
    
    """Instances store the four End Forces for a segment, and allow
    two sets of end forces to be added together.  m0 is left end moment,
    m1 is right end moment. v0, v1 are left and right
    end shears. SD sign convention: moments +ive clockwise, shears
    causing +ive rotation of the segment are +ive. """
    
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
    
    def __getitem__(self,ix):
        """Return end forces accessed by subscript 0 to 3."""
        return self.efs[ix]

class FEF(object):

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
