## Compiled from Frame2D_v04.py on Wed May 25 09:43:22 2016

## In [4]:
from __future__ import print_function

## In [5]:
from salib import extend, import_notebooks
import_notebooks()
from Tables import Table
from Nodes import Node
from Members import Member
from LoadSets import LoadSet, LoadCombination
from NodeLoads import makeNodeLoad
from MemberLoads import makeMemberLoad
from collections import OrderedDict, defaultdict
import numpy as np

## In [6]:
class Object(object):
    pass

class Frame2D(object):
    
    def __init__(self,dsname=None):
        self.dsname = dsname
        if dsname is not None:
            Table.set_source(dsname)
        self.clear()
        
    def clear(self):
        self.rawdata = Object()
        self.nodes = OrderedDict()
        self.members = OrderedDict()
        self.nodeloads = LoadSet()
        self.memberloads = LoadSet()
        self.loadcombinations = LoadCombination()
        #self.dofdesc = []
        #self.nodeloads = defaultdict(list)
        #self.membloads = defaultdict(list)
        self.ndof = 0
        self.nfree = 0
        self.ncons = 0
        self.R = None
        self.D = None
        self.PDF = None    # P-Delta forces
        
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

## In [8]:
@extend
class Frame2D:
    
    COLUMNS_nodes = ('NODEID','X','Y')
        
    def install_nodes(self):
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

## In [14]:
def isnan(x):
    if x is None:
        return True
    try:
        return np.isnan(x)
    except TypeError:
        return False

## In [15]:
@extend
class Frame2D:
    
    COLUMNS_supports = ('NODEID','C0','C1','C2')
    
    def install_supports(self):
        table = self.get_table('supports')
        for ix,row in table.data.iterrows():
            node = self.get_node(row.NODEID)
            for c in [row.C0,row.C1,row.C2]:
                if not isnan(c):
                    node.add_constraint(c)
        self.rawdata.supports = table

## In [19]:
@extend
class Frame2D:
    
    COLUMNS_members = ('MEMBERID','NODEJ','NODEK')
    
    def install_members(self):
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

## In [23]:
@extend
class Frame2D:
    
    COLUMNS_releases = ('MEMBERID','RELEASE')
    
    def install_releases(self):
        table = self.get_table('releases',optional=True)
        for ix,r in table.data.iterrows():
            memb = self.get_member(r.MEMBERID)
            memb.add_release(r.RELEASE)
        self.rawdata.releases = table

## In [26]:
try:
    from sst import SST
    __SST = SST()
    get_section = __SST.section
except ImportError:
    def get_section(dsg,fields):
        raise ValueError('Cannot lookup property SIZE because SST is not available.  SIZE = {}'.format(dsg))
        ##return [1.] * len(fields.split(',')) # in case you want to do it that way

## In [28]:
@extend
class Frame2D:
    
    COLUMNS_properties = ('MEMBERID','SIZE','IX','A')
    
    def install_properties(self):
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

## In [32]:
@extend
class Frame2D:
    
    COLUMNS_node_loads = ('LOAD','NODEID','DIRN','F')
    
    def install_node_loads(self):
        table = self.get_table('node_loads')
        dirns = ['FX','FY','FZ']
        for ix,row in table.data.iterrows():
            n = self.get_node(row.NODEID)
            if row.DIRN not in dirns:
                raise ValueError("Invalid node load direction: {} for load {}, node {}; must be one of '{}'"
                                .format(row.DIRN, row.LOAD, row.NODEID, ', '.join(dirns)))
            l = makeNodeLoad({row.DIRN:row.F})
            self.nodeloads.append(row.LOAD,n,l)
        self.rawdata.node_loads = table

## In [36]:
@extend
class Frame2D:
    
    COLUMNS_member_loads = ('LOAD','MEMBERID','TYPE','W1','W2','A','B','C')
    
    def install_member_loads(self):
        table = self.get_table('member_loads')
        for ix,row in table.data.iterrows():
            m = self.get_member(row.MEMBERID)
            l = makeMemberLoad(m.L,row)
            self.memberloads.append(row.LOAD,m,l)
        self.rawdata.member_loads = table

## In [40]:
@extend
class Frame2D:
    
    COLUMNS_load_combinations = ('CASE','LOAD','FACTOR')
    
    def install_load_combinations(self):
        table = self.get_table('load_combinations',optional=True)
        if len(table) > 0:
            for ix,row in table.data.iterrows():
                self.loadcombinations.append(row.CASE,row.LOAD,row.FACTOR)
        else:
            all = self.nodeloads.names.union(self.memberloads.names)
            for l in all:
                self.loadcombinations.append('all',l,1.0)
        self.rawdata.load_combinations = table

## In [43]:
@extend
class Frame2D:

    def iter_nodeloads(self,casename):
        for o,l,f in self.loadcombinations.iterloads(casename,self.nodeloads):
            yield o,l,f
    
    def iter_memberloads(self,casename):
        for o,l,f in self.loadcombinations.iterloads(casename,self.memberloads):
            yield o,l,f

## In [46]:
@extend
class Frame2D:
    
    def install_all(self):
        self.install_nodes()
        self.install_supports()
        self.install_members()
        self.install_releases()
        self.install_properties()
        self.install_node_loads()
        self.install_member_loads()
        self.install_load_combinations()

## In [48]:
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
def prhead(txt,ul='='):
    """Print a heading and underline it."""
    print()
    print(txt)
    if ul:
        print(ul*(len(txt)//len(ul)))
    print()

## In [52]:
@extend
class Frame2D:

    def print_nodes(self,precision=0,printdof=False):
        prhead('Nodes:')
        print('Node          X         Y  Constraints  DOF #s')
        print('----      -----     -----  -----------  ------')
        for nid,node in self.nodes.items():
            ct = ','.join(sorted(node.constraints,key=lambda t: Node.DIRECTIONS[t]))
            dt = ','.join([str(x) for x in node.dofnums])
            print('{:<5s}{:>10.{precision}f}{:>10.{precision}f}  {:<11s}  {}'                  .format(nid,node.x,node.y,ct,dt,precision=precision))
        if not printdof:
            return
        print()
        print('DOF#   Node  Dirn')
        print('----   ----  ----')
        for i in range(len(self.dofdesc)):
            node,dirn = self.dofdesc[i]
            print('{:>4d}   {:<4s}  {}'.format(i,node.id,dirn))

## In [54]:
@extend
class Frame2D:
    
    def print_members(self,precision=1):
        prhead('Members:')
        print('Member   Node-J  Node-K    Length       dcx       dcy  Size                Ix           A  Releases')
        print('------   ------  ------    ------   -------   -------  --------      --------       -----  --------')
        for mid,memb in self.members.items():
            nj = memb.nodej
            nk = memb.nodek
            rt = ','.join(sorted(memb.releases,key=lambda t: Member.RELEASES[t]))
            print('{:<7s}  {:<6s}  {:<6s}  {:>8.{precision}f}  {:>8.5f}  {:>8.5f}  {:<10s}  {:>10g}  {:>10g}  {}'                  .format(memb.id,nj.id,nk.id,memb.L,memb.dcx,memb.dcy,str(memb.size),memb.Ix,memb.A,rt,precision=precision))

## In [56]:
@extend
class Frame2D:
    
    def print_loads(self,precision=0):
        
        prhead('Node Loads:')
        if self.nodeloads:
            print('Type  Node      FX          FY          MZ')
            print('----  ----  ----------  ----------  ----------')
            for lname,node,load in self.nodeloads:
                print('{:<4s}  {:<4s}  {:>10.{precision}f}  {:>10.{precision}f}  {:>10.{precision}f}'
                      .format(lname,node.id,load.fx,load.fy,load.mz,precision=precision))
        else:
            print(" - - - none - - -")

        prhead('Member Loads:')
        if self.memberloads:
            print('Type  Member  Load')
            print('----  ------  ----------------')
            for lname,memb,load in self.memberloads:
                print("{:<4s}  {:<6s}  {}".format(lname,memb.id,load))
        else:
            print(" - - - none - - -")

        prhead("Load Combinations:")
        if self.loadcombinations:
            print('Case   Type  Factor')
            print('-----  ----  ------')
            prev = None
            for cname,lname,f in self.loadcombinations:
                cn = ' '*(len(prev)//2)+'"' if cname == prev else cname
                print("{:<5s}  {:<4s}  {:>6.2f}".format(cn,lname,f))
                prev = cname
        else:
            print(" - - - none - - -")

## In [58]:
@extend
class Frame2D:
    
    def print_input(self):
        
        prhead('Frame '+str(self.dsname)+':')
        print()
        print('              # of nodal degrees of freedom:',self.ndof)
        print('  # of constrained nodal degrees of freedom:',self.ncons)
        print('# of unconstrained nodal degrees of freedom:',self.nfree,' (= degree of kinematic indeterminacy)')
        m = len(self.members)
        r = self.ncons
        j = len(self.nodes)
        c = len(self.rawdata.releases)
        print()
        print('                               # of members:',m)
        print('                             # of reactions:',r)
        print('                                 # of nodes:',j)
        print('                            # of conditions:',c)
        print('             degree of static indeterminacy:',(3*m+r)-(3*j+c))
        print('\n')

        self.print_nodes()
        print('\n')
        self.print_members()
        print('\n')
        self.print_loads()

## In [ ]:

