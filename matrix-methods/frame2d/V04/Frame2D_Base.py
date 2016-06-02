## Compiled from Frame2D_Base.py on Wed Jun  1 14:17:21 2016

## In [2]:
from __future__ import print_function

## In [3]:
from collections import OrderedDict, defaultdict
from LoadSets import LoadSet, LoadCombination
from Tables import Table

## In [4]:
class Object(object):
    pass

class Frame2D(object):
    
    def __init__(self,dsname=None):
        self.dsname = dsname
        if dsname is not None:
            Table.set_source(dsname)
        self.reset()
        
    def reset(self):
        self.rawdata = Object()
        self.nodes = OrderedDict()
        self.members = OrderedDict()
        self.nodeloads = LoadSet()
        self.nodedeltas = LoadSet()
        self.memberloads = LoadSet()
        self.loadcombinations = LoadCombination()
        self.dofdesc = []
        self.loadcase_fefs = {}
        self.ndof = 0
        self.nfree = 0
        self.ncons = 0
        self.R = None
        self.D = None
        self.PDF = None    # P-Delta forces

## In [1]:
class ResultSet(object):
    
    """Instances of class ResultSet gather together all of the results from
    one complete structural analysis of one load case."""
    
    def __init__(self,loadcase):
        self.loadcase = loadcase
        self.node_P = None       # applied node loads
        self.memb_P = None       # applied fixed end member forces
        self.memb_fefs = {}      # fixed end member forces, indexed by member
        self.node_displacements = None  # all node displacements
        self.reaction_displacements = None # constrained node displacements
        self.reaction_forces = None        # constrained node reactions
        self.memb_efs = {}                 # member end forces, indexed by member

## In [ ]:
