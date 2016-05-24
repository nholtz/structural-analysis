## Compiled from LoadSets.py on Tue May 24 10:34:14 2016

## In [1]:
from __future__ import print_function

## In [2]:
from collections import OrderedDict

## In [8]:
class LoadSet(object):
    
    def __init__(self):
        self.loadlist = []
        self.names = set()
        
    def append(self,name,obj,load):
        name = name.lower()
        self.loadlist.append((name,obj,load))
        self.names.add(name)
        
    def iterloads(self,name):
        name = name.lower()
        ##if name not in self.names:
        ##    raise ValueError("Invalid load name: {}.  Must be one of: {}"
        ##                    .format(name,', '.join(sorted(list(self.names)))))
        for n,o,l in self.loadlist:
            if n == name:
                yield (o,l,1.0)
                
    def __len__(self):
        return len(self.names)
    
    def __iter__(self):
        return iter(self.loadlist)

## In [11]:
class LoadCombination(object):

    def __init__(self):
        self.combos = OrderedDict()
        
    def append(self,combo_name,load_name,factor):
        combo_name = combo_name.lower()
        load_name = load_name.lower()
        if combo_name not in self.combos:
            self.combos[combo_name] = OrderedDict()
        d = self.combos[combo_name]
        if load_name in d:
            raise ValueError("Load '{}' is multiply defined on combo '{}'".format(load_name.combo_name))
        d[load_name] = factor
        
    def iterloads(self,name,loadset):
        name = name.lower()
        if name not in self.combos:
            raise ValueError("Invalid load combination name: {}; must be one of '{}'"
                            .format(name,', '.join(sorted(self.combos.keys()))))
        for load_name,factor in self.combos[name].items():
            for obj,load,f in loadset.iterloads(load_name):
                yield obj,load,f*factor
                
    def __len__(self):
        return len(self.combos)
    
    def __iter__(self):
        for cname,llist in self.combos.items():
            for lname,factor in llist.items():
                yield cname,lname,factor

## In [ ]:

