## Compiled from Frame2D_SolveFirstOrder.py on Sun Jun  5 22:12:13 2016

## In [1]:
from __future__ import print_function

## In [2]:
from salib import extend, import_notebooks
import numpy as np
from collections import defaultdict

## In [3]:
from Frame2D_Base import Frame2D, ResultSet
import Frame2D_Input
import Frame2D_Display
from MemberLoads import EF

## In [5]:
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

## In [7]:
@extend
class Frame2D:
    
    def buildP(self,loadcase='all'):
        P = np.mat(np.zeros((self.ndof,1)))
        for node,load,factor in self.iter_nodeloads(loadcase):
            P[node.dofnums] += load.forces * factor
        return P
            
    def buildD(self,loadcase='all'):
        D = np.mat(np.zeros((self.ndof,1)))
        for node,load,factor in self.iter_nodedeltas(loadcase):
            D[node.dofnums] += load.forces * factor
        return D

## In [9]:
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

## In [10]:
@extend
class Frame2D:

    def calculate_mefs(self,rs):
        all_efs = {}
        D = rs.node_displacements
        for memb in self.members.values():
            gn = memb.nodej.dofnums + memb.nodek.dofnums
            med = D[np.ix_(gn)]
            mefs = EF((memb.Kl*memb.Tm)*med)
            fefs = rs.memb_fefs.get(memb,None)
            if fefs is not None:
                mefs += fefs
            all_efs[memb] = mefs
        return all_efs

## In [11]:
@extend
class Frame2D:
    
    def pdelta_forces(self,rs):
        D = rs.node_displacements
        pdf = np.mat(np.zeros((self.ndof,1)))
        for m in self.columns:
            ef = rs.member_efs[m].fefs
            efg = m.Tm.T * ef    # end forces in global coords !!! TOO MUCH CALC !!!!
            P = efg[1,0]
            j = m.nodej.dofnums[0]
            k = m.nodek.dofnums[0]
            Delta = D[k,0]-D[j,0]
            H = m.L
            pdf[k,0] += P*Delta/H
            pdf[j,0] -= P*Delta/H
            ##print(m.id,H,j,k,P,Delta,P*Delta/H)
        return pdf

## In [12]:
@extend
class Frame2D:
    
    def solve(self,loadcase='all',pdelta=False,maxniter=10):
        
        self.number_dofs()
        K = self.buildK()

        rs = ResultSet(loadcase)
        rs.memb_fefs = self.calc_fefs(loadcase)
        P = rs.node_P = self.buildP(loadcase)
        MP = rs.memb_P = self.buildMP(rs.memb_fefs)
        P = P + MP
        
        D = self.buildD(loadcase)
        
        N = self.nfree
        Kff = K[:N,:N]  # partition the matrices ....
        Kfc = K[:N,N:]
        Kcf = K[N:,:N]
        Kcc = K[N:,N:]
        
        D[:N] = np.linalg.solve(Kff,P[:N] - Kfc*D[N:])  # displacements
        R = Kcf*D[:N] + Kcc*D[N:] - P[N:]    # reactions at the constrained DOFs
        rs.node_displacements = D
        rs.reaction_forces = R   
        rs.member_efs = self.calculate_mefs(rs)
        
        if pdelta:
            niter = 0 
            self.columns = [m for m in self.members.values() if abs(m.dcy) >= 0.95]
            rs.pdelta = True
            while True:
                if niter > maxniter:
                    raise Exception('Too many iterations.  Giving up.  Solution not usable.')
                niter += 1
                Dprev = D.copy()
                
                PDF = self.pdelta_forces(rs)
                PDF[N:] = 0.
        
                D[:N] = np.linalg.solve(Kff,P[:N] + PDF[:N] - Kfc*D[N:])
                rs.node_displacements = D
                rs.member_efs = self.calculate_mefs(rs)
                
                maxD = max(abs(D[:N]))[0,0]
                maxChange = max(abs(D[:N]-Dprev[:N]))[0,0]
                maxP = 100.*maxChange/maxD
                print('iter={}, max D={}, max chg={}, max % chg={}'.format(niter,maxD,maxChange,maxP))
                if maxP < .01:
                    break
            R = Kcf*D[:N] + Kcc*D[N:] - P[N:] # reactions at the constrained DOFs (exclude P-delta forces)
            rs.reaction_forces = R
            rs.pdelta_forces = PDF
            print()
            
        return rs
