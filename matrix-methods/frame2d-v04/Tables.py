## Compiled from Tables.py on Fri Jun  3 12:49:07 2016

## In [1]:
from __future__ import print_function

import pandas as pd
import os, os.path
import StringIO
import hashlib
from IPython.core.magic import register_cell_magic
import re

## In [20]:
class Table(object):
    
    DSNAME = None     # default data set name
    DSTYPE = 'dir'    # someday we will allow 'zip' for zip archives
    #DSTYPE = 'cell'  # for CSV data provided via %%Table cell magic
    #DSTYPE = 'data'  # for dataframe data provided directly
    CELLDATA = {}
    
    @classmethod
    def set_source(cls,ds_name,ds_type=None):
        if ds_type is None:
            dirname = ds_name + '.d'
            if os.path.exists(dirname):
                ds_type = 'dir'
            else:
                ds_type = 'cell'
        assert ds_type in ['dir','cell','data']
        cls.DSNAME = ds_name
        cls.DSTYPE = ds_type
        cls.CELLDATA = {}
        cls.DATAFRAMES = {}
        
    @classmethod
    def set_data(cls,table_name,data):
        assert cls.DSTYPE == 'data'
        cls.DATAFRAMES[table_name] = data
    
    def __init__(self,table_name,ds_name=None,columns=None,index_col=None,optional=False,data=[]):
        if ds_name is None and self.DSNAME is not None:
            ds_name = self.DSNAME
        self.ds_name = ds_name
        self.table_name = table_name
        self.prefix = None
        self.file_name = None
        self.columns = columns
        self.index_col = index_col
        self.optional = optional
        self.data = pd.DataFrame(data,columns=columns)
        
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
        elif self.DSTYPE == 'data':
            if optional:
                if self.table_name not in self.DATAFRAMES:
                    return self.data
            self.data = self.DATAFRAMES[self.table_name]
            return self.data
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
    
    def write(self,ds_name=None,precision=None,index=False,prefix=None):
        if ds_name is None:
            ds_name = self.ds_name
        dirname = ds_name + '.d'
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        if prefix is not None:
            dirname = dirname + '/' + prefix
            if not os.path.exists(dirname):
                os.mkdir(dirname)
        self.file_name = file_name = dirname + '/' + self.table_name + '.csv'
        float_format = None
        if precision is not None:
            float_format = '%.{:d}g'.format(precision)
        self.data.to_csv(file_name,index=index,float_format=float_format)
        return file_name
        
    def basename(self,file_name=None):
        if file_name is None:
            file_name = self.file_name
        return os.path.basename(file_name)
    
    def signature(self):
        file_name = self.file_name
        return (self.table_name,file_name,signature(file_name))
    
    def __len__(self):
        return len(self.data)
    
def signature(file_name):
    f = open(file_name,mode='rb')
    m = hashlib.sha256(f.read())
    f.close()
    return m.hexdigest()

## In [12]:
@register_cell_magic('Table')
def cell_table(line,cell):
    mo = re.match(r'\s*(\S+)\s*$',line)
    if not mo:
        raise ValueError('Usage: %%Table tablename')
    table_name = mo.group(1)
    global Table
    Table.DSTYPE = 'cell'
    Table.CELLDATA[table_name] = cell
