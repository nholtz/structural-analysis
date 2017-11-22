## Compiled from Frame2D_Output.ipynb on Tue Nov 21 20:29:44 2017

## In [1]:
from __future__ import print_function

## In [2]:
from salib import extend, import_notebooks
from .Tables import Table, DataSource

## In [3]:
from .Frame2D_Base import Frame2D
from . import Frame2D_Input

## In [5]:
@extend
class Frame2D:
    
    def write_table(self,tablename,dsname=None,prefix=None,record=True,precision=None,args=(),makedir=False):
        t = getattr(self.rawdata,tablename,None)
        if t is None:
            methodname = 'list_'+tablename
            method = getattr(self,methodname,None)
            if method and callable(method):
                data = method(*args)
                t = Table(data=data,tablename=tablename,columns=getattr(self,'COLUMNS_'+tablename))
        if t is None:
            raise ValueError("Unable to find table '{}'".format(tablename))
        DataSource.write_table(t,dsname=dsname,prefix=prefix,tablename=tablename,precision=precision,makedir=makedir)
        if record:
            setattr(self.rawdata,tablename,t)
        return t            

## In [7]:
@extend
class Frame2D:
   
   def list_nodes(self):
       return [(n.id,n.x,n.y) for n in self.nodes.values()]

## In [12]:
@extend
class Frame2D:
    
    def list_supports(self):
        ans = []
        for node in self.nodes.values():
            if node.constraints:
                cl = tuple(node.constraints)
                if len(cl) < 3:
                    cl = cl + ('',)*(3-len(cl))
                ans.append((node.id,)+cl)
        return ans

## In [18]:
@extend
class Frame2D:
    
    def list_members(self):
        return [(m.id,m.nodej.id,m.nodek.id) for m in self.members.values()]

## In [21]:
@extend
class Frame2D:
    
    def list_releases(self):
        return [(m.id,)+tuple(m.releases) for m in self.members.values() if m.releases]

## In [24]:
@extend
class Frame2D:
    
    def list_properties(self):
        return [(m.id,m.size,m.Ix,m.A) for m in self.members.values()]

## In [27]:
@extend
class Frame2D:
    
    def list_node_loads(self):
        ans = []
        dirns = ['FX','FY','FZ']
        for loadid,node,nload in self.nodeloads:
            for i in [0,1,2]:
                if nload[i]:
                    ans.append((loadid,node.id,dirns[i],nload[i]))
        return ans

## In [30]:
@extend    
class Frame2D:
    
    def list_support_displacements(self):
        ans = []
        dirns = ['DX','DY','RZ']
        for loadid,node,nload in self.nodedeltas:
            for i in [0,1,2]:
                if nload[i]:
                    ans.append((loadid,node.id,dirns[i],nload[i]))
        return ans        

## In [33]:
from MemberLoads import unmakeMemberLoad

@extend
class Frame2D:
    
    def list_member_loads(self):
        ans = []
        for loadid,memb,mload in self.memberloads:
            ml = unmakeMemberLoad(mload)
            ml['MEMBERID'] = memb.id
            ml['LOAD'] = loadid
            ans.append(ml)
        return ans

## In [37]:
@extend
class Frame2D:
    
    def list_load_combinations(self):
        return [(case,load,factor) for case,load,factor in self.loadcombinations]

## In [41]:
@extend
class Frame2D:
    
    COLUMNS_signatures = ['NAME','PATH','SIGNATURE']
    
    def list_signatures(self):
        return [t.signature() for tn,t in vars(self.rawdata).items() if type(t) is Table]

## In [44]:
import os, os.path

@extend
class Frame2D:
    
    def write_all(self,dsname,makedir=False):
        self.write_table('nodes',dsname=dsname,makedir=makedir)
        self.write_table('supports',dsname=dsname)
        self.write_table('members',dsname=dsname)
        self.write_table('releases',dsname=dsname)
        self.write_table('properties',dsname=dsname)
        self.write_table('node_loads',dsname=dsname)
        self.write_table('support_displacements',dsname=dsname)
        self.write_table('member_loads',dsname=dsname)
        self.write_table('load_combinations',dsname=dsname)
        self.write_table('signatures',dsname=dsname,record=False)

## In [48]:
@extend
class Frame2D:
    
    COLUMNS_node_displacements = ['NODEID','DX','DY','RZ']
    
    def list_node_displacements(self,rs):
        if not hasattr(rs,'node_displacements'):
            return []
        ans = []
        D = rs.node_displacements
        for node in self.nodes.values():
            d = D[node.dofnums]
            ans.append((node.id,d[0,0],d[1,0],d[2,0]))
        return ans

## In [51]:
@extend
class Frame2D:
    
    COLUMNS_reaction_forces = ['NODEID','FX','FY','MZ']
    
    def list_reaction_forces(self,rs):
        if not hasattr(rs,'reaction_forces'):
            return []
        R = rs.reaction_forces
        ans = []
        for node in self.nodes.values():
            if node.constraints:
                l = [node.id,None,None,None]
                for dirn in node.constraints:
                    i = node.DIRECTIONS[dirn]
                    j = node.dofnums[i]
                    val = R[j-self.nfree,0]
                    l[i+1] = val
                ans.append(l)
        return ans

## In [54]:
@extend
class Frame2D:
    
    COLUMNS_member_end_forces = 'MEMBERID,FXJ,FYJ,MZJ,FXK,FYK,MZK'.split(',')
    
    def list_member_end_forces(self,rs):
        if not hasattr(rs,'member_efs'):
            return []
        mefs = rs.member_efs
        ans = []
        for memb in self.members.values():
            efs = mefs[memb].fefs
            ans.append((memb.id,efs[0,0],efs[1,0],efs[2,0],efs[3,0],efs[4,0],efs[5,0]))
        return ans

## In [57]:
@extend
class Frame2D:
    
    def write_results(self,dsname,rs):
        self.write_table('node_displacements',dsname=dsname,prefix=rs.loadcase,record=False,
                         precision=15,args=(rs,),makedir=True)
        self.write_table('reaction_forces',dsname=dsname,prefix=rs.loadcase,record=False,
                         precision=15,args=(rs,))
        self.write_table('member_end_forces',dsname=dsname,prefix=rs.loadcase,record=False,
                         precision=15,args=(rs,))
        if rs.pdelta:
            self.write_table('pdelta_forces',dsname=dsname,prefix=rs.loadcase,record=False,
                             precision=15,args=(rs,))
