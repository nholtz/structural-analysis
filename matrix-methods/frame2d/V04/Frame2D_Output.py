## Compiled from Frame2D_Output.py on Fri Jun  3 10:57:49 2016

## In [1]:
from __future__ import print_function

## In [2]:
from salib import extend, import_notebooks
import_notebooks()
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
    
    def write_table(self,table_name,ds_name=None,prefix=None,record=True):
        t = getattr(self.rawdata,table_name,None)
        if t is None:
            methodname = 'list_'+table_name
            method = getattr(self,methodname,None)
            if method and callable(method):
                data = method()
                t = Table(table_name,data=data,columns=getattr(self,'COLUMNS_'+table_name))
        if t is None:
            raise ValueError("Unable to find table '{}'".format(table_name))
        t.write(ds_name=ds_name,prefix=prefix)
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
        dirns = ['DX','DY','TZ']
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
@extend
class Frame2D:
    
    def write_all(self,ds_name):
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

## In [ ]:

