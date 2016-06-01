## Compiled from Frame2D_Base.py on Tue May 31 20:14:30 2016

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

## In [ ]:

