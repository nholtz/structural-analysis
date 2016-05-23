## Compiled from Tables.py on Mon May 23 10:49:54 2016

## In [1]:
from __future__ import print_function

import pandas as pd
import os.path
import StringIO
import hashlib
from IPython.core.magic import register_cell_magic
import re

## In [4]:
f = pd.DataFrame(columns=('One','Two'))
f

## In [ ]:


## In [52]:
class Table(object):
    
    DSNAME = None     # default data set name
    DSTYPE = 'dir'    # someday we will allow 'zip' for zip archives
    #DSTYPE = 'cell'
    CELLDATA = {}
    
    def __init__(self,table_name,ds_name=None,columns=None,index_col=None,optional=False):
        if ds_name is None and self.DSNAME is not None:
            ds_name = self.DSNAME
        self.ds_name = ds_name
        self.table_name = table_name
        self.prefix = None
        self.file_name = None
        self.columns = columns
        self.index_col = index_col
        self.optional = optional
        self.data = pd.DataFrame(columns=columns)
        
    def _file_name(self,prefix=None):
        self.prefix = prefix
        if prefix:
            n = prefix + '-' + self.table_name
        else:
            n = self.table_name
        return self.ds_name + '.d/' + n + '.csv'
        
    def read(self,file_name=None,optional=None):
        if optional is None:
            optional = self.optional
        if self.DSTYPE == 'dir':
            if not file_name:
                file_name = self._file_name()
            self.file_name = file_name
            if optional:
                if not os.path.exists(file_name):
                    return self.data
            stream = file(file_name,'r')
        elif self.DSTYPE == 'cell':
            if optional:
                if self.table_name not in self.CELLDATA:
                    return self.data
            stream = StringIO.StringIO(self.CELLDATA[self.table_name])
        else:
            raise ValueError("Invalid DS Type: {}".format(self.DSTYPE))
        try:
            self.data = pd.read_csv(stream,usecols=self.columns,index_col=self.index_col)
        except ValueError as err:
            msg = err.args[0]
            if msg.endswith('is not in list'):
                c = msg.split("'")[1]
                raise ValueError("'{}' is not in the set of columns in file '{}'".format(c,file_name))
            if msg.startswith('Index') and msg.endswith('invalid'):
                raise ValueError("Index column '{}' is not in the set of columns in file '{}'".format(self.index_col,file_name))
            raise
        stream.close()
        return self.data
    
    def write(self,file_name=None,precision=None,index=False,prefix=None):
        if not file_name and prefix is None:
            file_name = self.file_name
        if not file_name:
            file_name = self._file_name(prefix=prefix)
        self.file_name = file_name
        float_format = None
        if precision is not None:
            float_format = '%.{:d}g'.format(precision)
        self.data.to_csv(file_name,index=index,float_format=float_format)
        
    def basename(self,file_name=None):
        if file_name is None:
            file_name = self.file_name
        return os.path.basename(file_name)
    
    def signature(self):
        file_name = self.file_name
        return (self.basename(),signature(file_name))
    
def signature(file_name):
    f = open(file_name,mode='rb')
    m = hashlib.sha256(f.read())
    f.close()
    return m.hexdigest()

## In [61]:
@register_cell_magic('Table')
def cell_table(line,cell):
    mo = re.match(r'\s*(\S+)\s*$',line)
    if not mo:
        raise ValueError('Usage: %%Table tablename')
    table_name = mo.group(1)
    global Table
    Table.DSTYPE = 'cell'
    Table.CELLDATA[table_name] = cell
