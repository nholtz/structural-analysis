## Compiled from Members.py on Sun May 22 18:12:09 2016

## In [1]:
import salib as sl

## In [2]:
class Member(object):
    
    RELEASES = {'MZJ':2, 'MZK':5}
    
    E = 200000.
    G = 77000.
    
    def __init__(self,ident,nodej,nodek):
        self.id = ident
        self.nodej = nodej
        self.nodek = nodek
        self.dcx,self.dcy,self.L = nodej.to(nodek)
        self.KL = None           # stiffness matrix, local coords
        self.KG = None           # stiffness matrix, global coords
        self.releases = set()
        self.Ix = None
        self.A = None
        self.Tm = None           # transformation matrix, global to local
        self.fefsl = None        # fixed end forces, local coordinates
        self.mefs = None         # member end forces, local coordinates
        
    def add_release(self,rel):
        r = rel.upper()
        if r not in self.RELEASES:
            raise Exception('Invalid release name: {}'.format(rel))
        self.releases.add(r)
        
    def __repr__(self):
        return '{}("{}","{}","{}")'.format(self.__class__.__name__,self.id,self.nodej,self.nodek)
    
    def localK(self):
        """Return the member stiffness matrix in local coordinates"""
        L = self.L
        E = self.E
        A = self.A
        I = self.Ix
        k0 = E*A/L
        k12 = 12.*E*I/L**3
        k6 = 6.*E*I/L**2
        k4 = 4.*E*I/L
        k2 = 2.*E*I/L
        KL = np.mat([[ k0,  0,    0,   -k0,   0,    0],
                     [ 0,   k12,  k6,   0,   -k12,  k6],
                     [ 0,   k6,   k4,   0,   -k6,   k2],
                     [-k0,  0,    0,    k0,   0,    0],
                     [ 0,  -k12, -k6,   0,    k12, -k6],
                     [ 0,   k6,   k2,   0,   -k6,   k4]])
        for r in self.releases:
            KL = self.releaseK(KL,self.RELEASES[r])
        self.Kl = KL
        return KL
            
    def releaseK(self,Kl,rel):
        """Return a modified stiffness matrix to account for a moment release
        at one of the ends.  Kl is the original matrix, dx, dy are projections of the
        member, and 'rel' is 2 or 5 to identify the local dof # of the released dof.
        Both KL and KG are returned if the transformation matrix, T, is provided"""
        L = self.L
        if rel == 2:
            if Kl[5,5] == 0.:   # is other end also pinned?
                em = np.mat([1.,0.]).T    # corrective end moments, far end pinned
            else:
                em = np.mat([1.,0.5]).T   # corrective end moments, far end fixed
        elif rel == 5:
            if Kl[2,2] == 0.:
                em = np.mat([0.,1.]).T
            else:
                em = np.mat([0.5,1.]).T
        else:
            raise ValueError("Invalid release #: {}".format(rel))
        Tf = np.mat([[0.,0.],[1./L,1./L],[1.,0.],[0.,0.],[-1./L,-1./L],[0.,1.]])
        M = Tf*em

        K = Kl.copy()    
        K[:,1] -= M*K[rel,1]  # col 1 - forces for unit vertical displacment at j-end
        K[:,2] -= M*K[rel,2]  # col 2 - forces for unit rotation at j-end
        K[:,4] -= M*K[rel,4]  # col 4 - forces for unit vertical displacment at k-end
        K[:,5] -= M*K[rel,5]  # col 5 - forces for unit rotation at k-end
        return K

    def transform(self):
        """Return a transformation matrix to transform forces and displacements
        in global coordinates to local coordinates for the 2-d frame member.
        This is called the member transformation matrix, Tm"""
        cx = self.dcx
        cy = self.dcy
        self.Tm = np.mat([[ cx,  cy,  0,   0,   0,   0],
                          [-cy,  cx,  0,   0,   0,   0],
                          [ 0,   0,   1,   0,   0,   0],
                          [ 0,   0,   0,   cx,  cy,  0],
                          [ 0,   0,   0,  -cy,  cx,  0],
                          [ 0,   0,   0,   0,   0,   1]])
        return self.Tm
    
    def fefs(self,loads):
        if loads:
            fef = loads[0].fefs()
            for load in loads[1:]:
                fef += load.fefs()
            for r in self.releases:
                fef = self.releaseFEF(fef,self.RELEASES[r])
        else:
            fef = zerofefs()
        self.fefsl = fef            
        return fef
    
    def vm(self,loads,mefs=None):
        """Return shear and moment 'diagrams'.  Return (xv,v,xm,m) -
        xv and xm are positions along span, and v and m are shears and
        moments at those points.  Use normal sign convention (not beam sign 
        convention) - on left FBD, moments +ive CCW, shear +ive upwards.
        """
        def _getx(self,loads,attr):
            degree = 0
            pts = [0.,self.L]
            for load in loads:
                pt1,pt2,d = getattr(load,attr)
                for p in pt1,pt2:
                    if p is not None:
                        pts.append(p)
                if d > degree:
                    degree = d
            ptsv = np.array(pts)
            if degree > 1:
                ptsv = np.concatenate((ptsv,np.linspace(0,self.L)))
            ptsv.sort()
            return np.unique(ptsv)
        
        xv = _getx(self,loads,'vpts')
        xm = _getx(self,loads,'mpts')
        return xv,None,xm,None
    
    def releaseFEF(self,fef,rel):
        """Return a modified fixed end force vector to account for a moment release
        at one of the ends.  fef is the original matrix, 'rel' is 2 or 5 to identify 
        the local dof # of the released moment."""
        L = self.L
        if rel == 2:
            if fef[5,0] == 0.:   # is other end also pinned?
                em = np.mat([1.,0.]).T    # corrective end moments, far end pinned
            else:
                em = np.mat([1.,0.5]).T   # corrective end moments, far end fixed
        elif rel == 5:
            if fef[2,0] == 0.:
                em = np.mat([0.,1.]).T
            else:
                em = np.mat([0.5,1.]).T
        else:
            raise ValueError("Invalid release #: {}".format(rel))
        Tf = np.mat([[0.,0.],[1./L,1./L],[1.,0.],[0.,0.],[-1./L,-1./L],[0.,1.]])
        M = Tf*em

        return fef - M*fef[rel,0]

## In [ ]:

