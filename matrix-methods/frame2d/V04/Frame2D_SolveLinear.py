## Compiled from Frame2D_SolveLinear.py on Tue May 31 23:08:27 2016

## In [2]:
from __future__ import print_function

## In [19]:
from salib import extend, import_notebooks
import_notebooks()
import numpy as np
from collections import defaultdict

## In [24]:
from Frame2D_Base import Frame2D
import Frame2D_Input
import Frame2D_Display

## In [26]:
@extend
class Frame2D:
    
    def buildK(self):
        K = np.mat(np.zeros((self.ndof,self.ndof)))
        for memb in self.members.values():
            Kl = memb.localK()
            Tm = memb.transform()
            Kg = Tm.T * Kl * Tm
            dofnums = memb.nodej.dofnums + memb.nodek.dofnums
            K[np.ix_(dofnums,dofnums)] += Kg
        return K

## In [28]:
@extend
class Frame2D:
    
    def buildP(self,loadcase='all'):
        P = np.mat(np.zeros((self.ndof,1)))
        for node,load,factor in self.iter_nodeloads(loadcase):
            P[node.dofnums] += load.forces * factor
        for node,load,factor in self.iter_nodedeltas(loadcase):
            P[node.dofnums] += load.forces * factor
        return P

## In [30]:
@extend
class Frame2D:
    
    def calc_fefs(self,loadcase='all'):
        ll = defaultdict(list)
        for memb,load,factor in self.iter_memberloads(loadcase):
            ll[memb].append((load,factor))
        fef = {memb:memb.fefs(loads) for memb,loads in ll.items()}
        #self.loadcase_fefs[loadcase] = fef
        return fef    

    def buildMP(self,memb_fefs):
        MP = np.mat(np.zeros((self.ndof,1)))
        for memb,mfefs in memb_fefs.items():
            gfefs = memb.Tm.T * mfefs.fefs
            dofnums = memb.nodej.dofnums + memb.nodek.dofnums
            MP[dofnums] -= gfefs
        return MP

## In [31]:
class ResultSet(object):
    
    """Instances of class ResultSet gather together all of the results from
    one complete structural analysis of one load case."""
    
    def __init__(self,loadcase):
        self.loadcase = loadcase
        self.node_P = None       # applied node loads
        self.memb_P = None       # applied fixed end member forces
        self.memb_fefs = {}      # fixed end member forces, indexed by member ID
        self.node_displacements = None  # unconstrained node displacements
        self.reaction_displacements = None # constrained node displacements
        self.reaction_forces = None        # constrained node reactions

## In [32]:
@extend
class Frame2D:
    
    def solve(self,loadcase='all'):
        
        self.number_dofs()
        K = self.buildK()

        rs = ResultSet(loadcase)
        rs.memb_fefs = self.calc_fefs(loadcase)
        P = rs.node_P = self.buildP(loadcase)
        MP = rs.memb_P = self.buildMP(rs.memb_fefs)
        P = P + MP
        
        D = np.mat(np.zeros((self.ndof,1)))
        
        N = self.nfree
        Kff = K[:N,:N]  # partition the matrices ....
        Kfc = K[:N,N:]
        Kcf = K[N:,:N]
        Kcc = K[N:,N:]
        
        D[:N] = np.linalg.solve(Kff,P[:N] - Kfc*D[N:])  # displacements
        R = Kcf*D[:N] + Kcc*D[N:] - P[N:]    # reactions at the constrained DOFs
        rs.node_displacements = D
        rs.reaction_forces = R
        return rs

## In [ ]:

