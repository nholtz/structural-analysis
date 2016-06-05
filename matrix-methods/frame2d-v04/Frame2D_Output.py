## Compiled from Frame2D_Output.py on Sat Jun  4 22:34:41 2016

## In [1]:
from __future__ import print_function

## In [2]:
from salib import extend, import_notebooks
from Tables import Table

## In [3]:
from Frame2D_Base import Frame2D
import Frame2D_Input

## In [4]:
#test:
f = Frame2D('frame-1')
f.input_all()

## In [5]:
@extend
class Frame2D:
    
    def write_table(self,table_name,ds_name=None,prefix=None,record=True,precision=None,args=(),makedir=False):
        t = getattr(self.rawdata,table_name,None)
        if t is None:
            methodname = 'list_'+table_name
            method = getattr(self,methodname,None)
            if method and callable(method):
                data = method(*args)
                t = Table(table_name,data=data,columns=getattr(self,'COLUMNS_'+table_name))
        if t is None:
            raise ValueError("Unable to find table '{}'".format(table_name))
        t.write(ds_name=ds_name,prefix=prefix,precision=precision,makedir=makedir)
        if record:
            setattr(self.rawdata,table_name,t)
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
    
    def write_all(self,ds_name,mkdir=False):
        if mkdir:
            dname = ds_name + '.d'
            if not os.path.exists(dname):
                os.mkdir(dname)
        self.write_table('nodes',ds_name)
        self.write_table('supports',ds_name)
        self.write_table('members',ds_name)
        self.write_table('releases',ds_name)
        self.write_table('properties',ds_name)
        self.write_table('node_loads',ds_name)
        self.write_table('support_displacements',ds_name)
        self.write_table('member_loads',ds_name)
        self.write_table('load_combinations',ds_name)
        self.write_table('signatures',ds_name,record=False)

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
    
    def write_results(self,ds_name,rs):
        self.write_table('node_displacements',ds_name=ds_name,prefix=rs.loadcase,record=False,
                         precision=15,args=(rs,),makedir=True)
        self.write_table('reaction_forces',ds_name=ds_name,prefix=rs.loadcase,record=False,
                         precision=15,args=(rs,))
        self.write_table('member_end_forces',ds_name=ds_name,prefix=rs.loadcase,record=False,
                         precision=15,args=(rs,))

## In [ ]:

