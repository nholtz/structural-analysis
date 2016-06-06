## Compiled from Frame2D_Input.py on Sat Jun  4 17:40:25 2016

## In [1]:
from __future__ import print_function

## In [2]:
from salib import extend, import_notebooks
from Tables import Table
from Nodes import Node
from Members import Member
from LoadSets import LoadSet, LoadCombination
from NodeLoads import makeNodeLoad
from MemberLoads import makeMemberLoad
from collections import OrderedDict, defaultdict
import numpy as np

## In [3]:
from Frame2D_Base import Frame2D

## In [4]:
@extend
class Frame2D:
    
    COLUMNS_xxx = [] # list of column names for table 'xxx'
        
    def get_table(self,tablename,extrasok=False,optional=False):
        columns = getattr(self,'COLUMNS_'+tablename)
        t = Table(tablename,ds_name=self.dsname,columns=columns,optional=optional)
        t.read(optional=optional)
        reqdl= columns
        reqd = set(reqdl)
        prov = set(t.columns)
        if reqd-prov:
            raise Exception('Columns missing {} for table "{}". Required columns are: {}'                            .format(list(reqd-prov),tablename,reqdl))
        if not extrasok:
            if prov-reqd:
                raise Exception('Extra columns {} for table "{}". Required columns are: {}'                               .format(list(prov-reqd),tablename,reqdl))
        return t

## In [6]:
@extend
class Frame2D:
    
    COLUMNS_nodes = ('NODEID','X','Y')
        
    def input_nodes(self):
        node_table = self.get_table('nodes')
        for ix,r in node_table.data.iterrows():
            if r.NODEID in self.nodes:
                raise Exception('Multiply defined node: {}'.format(r.NODEID))
            n = Node(r.NODEID,r.X,r.Y)
            self.nodes[n.id] = n
        self.rawdata.nodes = node_table
            
    def get_node(self,id):
        try:
            return self.nodes[id]
        except KeyError:
            raise Exception('Node not defined: {}'.format(id))

## In [12]:
def isnan(x):
    if x is None:
        return True
    try:
        return np.isnan(x)
    except TypeError:
        return False

## In [13]:
@extend
class Frame2D:
    
    COLUMNS_supports = ('NODEID','C0','C1','C2')
    
    def input_supports(self):
        table = self.get_table('supports')
        for ix,row in table.data.iterrows():
            node = self.get_node(row.NODEID)
            for c in [row.C0,row.C1,row.C2]:
                if not isnan(c):
                    node.add_constraint(c)
        self.rawdata.supports = table

## In [17]:
@extend
class Frame2D:
    
    COLUMNS_members = ('MEMBERID','NODEJ','NODEK')
    
    def input_members(self):
        table = self.get_table('members')
        for ix,m in table.data.iterrows():
            if m.MEMBERID in self.members:
                raise Exception('Multiply defined member: {}'.format(m.MEMBERID))
            memb = Member(m.MEMBERID,self.get_node(m.NODEJ),self.get_node(m.NODEK))
            self.members[memb.id] = memb
        self.rawdata.members = table
            
    def get_member(self,id):
        try:
            return self.members[id]
        except KeyError:
            raise Exception('Member not defined: {}'.format(id))

## In [21]:
@extend
class Frame2D:
    
    COLUMNS_releases = ('MEMBERID','RELEASE')
    
    def input_releases(self):
        table = self.get_table('releases',optional=True)
        for ix,r in table.data.iterrows():
            memb = self.get_member(r.MEMBERID)
            memb.add_release(r.RELEASE)
        self.rawdata.releases = table

## In [24]:
try:
    from sst import SST
    __SST = SST()
    get_section = __SST.section
except ImportError:
    def get_section(dsg,fields):
        raise ValueError('Cannot lookup property SIZE because SST is not available.  SIZE = {}'.format(dsg))
        ##return [1.] * len(fields.split(',')) # in case you want to do it that way

## In [26]:
@extend
class Frame2D:
    
    COLUMNS_properties = ('MEMBERID','SIZE','IX','A')
    
    def input_properties(self):
        table = self.get_table('properties')
        table = self.fill_properties(table)
        for ix,row in table.data.iterrows():
            memb = self.get_member(row.MEMBERID)
            memb.size = row.SIZE
            memb.Ix = row.IX
            memb.A = row.A
        self.rawdata.properties = table
        
    def fill_properties(self,table):
        data = table.data
        prev = None
        for ix,row in data.iterrows():
            nf = 0
            if type(row.SIZE) in [type(''),type(u'')]:
                if isnan(row.IX) or isnan(row.A):
                    Ix,A = get_section(row.SIZE,'Ix,A')
                    if isnan(row.IX):
                        nf += 1
                        data.loc[ix,'IX'] = Ix
                    if isnan(row.A):
                        nf += 1
                        data.loc[ix,'A'] = A
            elif isnan(row.SIZE):
                data.loc[ix,'SIZE'] = '' if nf == 0 else prev
            prev = data.loc[ix,'SIZE']
        table.data = data.fillna(method='ffill')
        return table

## In [30]:
@extend
class Frame2D:
    
    COLUMNS_node_loads = ('LOAD','NODEID','DIRN','F')
    
    def input_node_loads(self):
        table = self.get_table('node_loads')
        dirns = ['FX','FY','FZ']
        for ix,row in table.data.iterrows():
            n = self.get_node(row.NODEID)
            if row.DIRN not in dirns:
                raise ValueError("Invalid node load direction: {} for load {}, node {}; must be one of '{}'"
                                .format(row.DIRN, row.LOAD, row.NODEID, ', '.join(dirns)))
            if row.DIRN in n.constraints:
                raise ValueError("Constrained node {} {} must not have load applied."
                                .format(row.NODEID,row.DIRN))
            l = makeNodeLoad({row.DIRN:row.F})
            self.nodeloads.append(row.LOAD,n,l)
        self.rawdata.node_loads = table

## In [34]:
@extend
class Frame2D:
    
    COLUMNS_support_displacements = ('LOAD','NODEID','DIRN','DELTA')
    
    def input_support_displacements(self):
        table = self.get_table('support_displacements',optional=True)
        forns = {'DX':'FX','DY':'FY','RZ':'MZ'}
        for ix,row in table.data.iterrows():
            n = self.get_node(row.NODEID)
            if row.DIRN not in forns:
                raise ValueError("Invalid support displacements direction: {} for load {}, node {}; must be one of '{}'"
                                .format(row.DIRN, row.LOAD, row.NODEID, ', '.join(forns.keys())))
            fd = forns[row.DIRN]
            if fd not in n.constraints:
                raise ValueError("Support displacement, load: '{}'  node: '{}'  dirn: '{}' must be for a constrained node."
                                .format(row.LOAD,row.NODEID,row.DIRN))
            l = makeNodeLoad({fd:row.DELTA})
            self.nodedeltas.append(row.LOAD,n,l)
        self.rawdata.support_displacements = table

## In [38]:
@extend
class Frame2D:
    
    COLUMNS_member_loads = ('LOAD','MEMBERID','TYPE','W1','W2','A','B','C')
    
    def input_member_loads(self):
        table = self.get_table('member_loads')
        for ix,row in table.data.iterrows():
            m = self.get_member(row.MEMBERID)
            l = makeMemberLoad(m.L,row)
            self.memberloads.append(row.LOAD,m,l)
        self.rawdata.member_loads = table

## In [42]:
@extend
class Frame2D:
    
    COLUMNS_load_combinations = ('CASE','LOAD','FACTOR')
    
    def input_load_combinations(self):
        table = self.get_table('load_combinations',optional=True)
        if len(table) > 0:
            for ix,row in table.data.iterrows():
                self.loadcombinations.append(row.CASE,row.LOAD,row.FACTOR)
        if 'all' not in self.loadcombinations:
            all = self.nodeloads.names.union(self.memberloads.names)
            all = self.nodedeltas.names.union(all)
            for l in all:
                self.loadcombinations.append('all',l,1.0)
        self.rawdata.load_combinations = table

## In [45]:
@extend
class Frame2D:

    def iter_nodeloads(self,casename):
        for o,l,f in self.loadcombinations.iterloads(casename,self.nodeloads):
            yield o,l,f
    
    def iter_nodedeltas(self,casename):
        for o,l,f in self.loadcombinations.iterloads(casename,self.nodedeltas):
            yield o,l,f
    
    def iter_memberloads(self,casename):
        for o,l,f in self.loadcombinations.iterloads(casename,self.memberloads):
            yield o,l,f

## In [47]:
@extend
class Frame2D:
    
    def number_dofs(self):
        self.ndof = (3*len(self.nodes))
        self.ncons = sum([len(node.constraints) for node in self.nodes.values()])
        self.nfree = self.ndof - self.ncons
        ifree = 0
        icons = self.nfree
        self.dofdesc = [None] * self.ndof
        for node in self.nodes.values():
            for dirn,ix in node.DIRECTIONS.items():
                if dirn in node.constraints:
                    n = icons
                    icons += 1
                else:
                    n = ifree
                    ifree += 1
                node.dofnums[ix] = n
                self.dofdesc[n] = (node,dirn)

## In [51]:
@extend
class Frame2D:
    
    def input_all(self):
        self.input_nodes()
        self.input_supports()
        self.input_members()
        self.input_releases()
        self.input_properties()
        self.input_node_loads()
        self.input_support_displacements()
        self.input_member_loads()
        self.input_load_combinations()
        self.input_finish()
        
    def input_finish(self):
        self.number_dofs()

## In [ ]:

