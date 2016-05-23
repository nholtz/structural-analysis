## Compiled from LoadSets.py on Sun May 22 21:01:19 2016

## In [6]:
from collections import OrderedDict

## In [11]:
class LoadSet(object):
    
    def __init__(self):
        self.loadlist = []
        self.names = set()
        
    def append(self,name,obj,load):
        self.loadlist.append((name,obj,load))
        self.names.add(name)
        
    def iterloads(self,name):
        ##if name not in self.names:
        ##    raise ValueError("Invalid load name: {}.  Must be one of: {}"
        ##                    .format(name,', '.join(sorted(list(self.names)))))
        for n,o,l in self.loadlist:
            if n == name:
                yield (o,l,1.0)

## In [10]:
class LoadCombination(object):

    def __init__(self):
        self.combos = OrderedDict()
        
    def append(self,combo_name,load_name,factor):
        if combo_name not in self.combos:
            self.combos[combo_name] = OrderedDict()
        d = self.combos[combo_name]
        if load_name in d:
            raise ValueError("Load '{}' is multiply defined on combo '{}'".format(load_name.combo_name))
        d[load_name] = factor
        
    def iterloads(self,name,loadset):
        if name not in self.combos:
            raise ValueError("Invalid load combination name: {}; must be one of '{}'"
                            .format(name,', '.join(sorted(self.combos.keys()))))
        for load_name,factor in self.combos[name].items():
            for obj,load,f in loadset.iterloads(load_name):
                yield obj,load,f*factor

## In [ ]:

