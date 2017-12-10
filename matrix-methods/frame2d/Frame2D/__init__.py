from salib import extend, NBImporter

## Because of the idiotic Python 3 import rules, we have to add
## this directory to the path, otherwise we cannot use notebook
## pages both as modules and as scripts.

import sys
try:
    __path = __file__.split('/')[:-1]
    __thisdir = '/'.join(__path)
    if __thisdir not in sys.path:
        sys.path = sys.path[:1] + [__thisdir] + sys.path[1:]
except Exception as e:
    print(__e)
    
import Nodes
import NodeLoads
import Members
import MemberLoads
import LoadSets
from Frame2D_Base import Frame2D, ResultSet
import Frame2D_Input
import Frame2D_Output
import Frame2D_Display
import Frame2D_SolveFirstOrder
import Tables