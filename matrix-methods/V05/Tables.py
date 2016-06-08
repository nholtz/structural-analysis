## Compiled from Tables.ipynb on Wed Jun  8 12:03:41 2016

## In [1]:
from __future__ import print_function

import pandas as pd
import os, os.path
import StringIO
import hashlib
from IPython.core.magic import register_cell_magic
import re

## In [2]:
class Table(pd.DataFrame):
    
    _internal_names = pd.DataFrame._internal_names + ['filename']
    _internal_names_set = set(_internal_names)
    
    _metadata = ['tablename','dsname']
            
    def __init__(self,*args,**kwargs):
        dsname = kwargs.pop('dsname',None)
        tablename = kwargs.pop('tablename',None)
        filename = kwargs.pop('filename',None)
        super(self.__class__,self).__init__(*args,**kwargs)
        if dsname is not None:
            self.dsname = dsname
        if tablename is not None:
            self.tablename = tablename
        if filename is not None:
            self.filename = filename
        
    @property
    def _constructor(self):
        return self.__class__

## In [3]:
class DataSet(object):    
    
    ROOT = 'data'
    DSNAME = None     # default data set name
    DSTYPE = 'dir'    # someday we will allow 'zip' for zip archives
    #DSTYPE = 'cell'  # for CSV data provided via %%Table cell magic
    #DSTYPE = 'data'  # for dataframe data provided directly
    CELLDATA = {}     # csv text from %%Table magic cells, indexed by table name
    DATATABLES = {}   # dataframes directly provided by client, indexed by table name
    
    def __init__(self):
        raise NotImplementedError("Cannot create instance of class '{}'".format(self.__class__.__name__))
    
    @classmethod
    def set_root(cls,root):
        assert os.path.exists(root)
        cls.ROOT = root
    
    @classmethod
    def set_source(cls,dsname,dstype=None):
        if dstype is None:
            dirname = self.root + '/' + dsname + '.d'
            if os.path.exists(dirname):
                dstype = 'dir'
            else:
                dstype = 'unknown'
        assert dstype in ['dir','cell','data']
        cls.DSNAME = dsname
        cls.DSTYPE = dstype
        cls.CELLDATA = {}
        cls.DATATABLES = {}
        
    @classmethod
    def set_data(cls,tablename,table):
        cls.DATATABLES[tablename] = table
        if tablename in cls.CELLDATA:
            del cls.CELLDATA[tablename]
            
    @classmethod
    def set_cell(cls,tablename,celltext):
        cls.CELLDATA[tablename] = celltext
        if tablename in cls.DATATABLES:
            del cls.DATATABLES[tablename]
            
    @classmethod
    def _file_name(cls,tablename,prefix=None):
        n = tablename
        if prefix:
            n = prefix + '/' + tablename
        return cls.ROOT + '/' + cls.DSNAME + '.d/' + n + '.csv'
    
    @classmethod
    def get_table(cls,tablename,optional=False,prefix=None,columns=None,extrasok=True):
        stream = None
        filename = None
        t = None
        if tablename in cls.DATATABLES:
            t = cls.DATATABLES[tablename]
        else:
            if tablename in cls.CELLDATA:
                stream = StringIO.StringIO(cls.CELLDATA[tablename])
            else:
                filename = cls._file_name(tablename,prefix=prefix)
                if os.path.exists(filename):
                    stream = file(filename,'r')
            if stream is None:
                if optional:
                    d = pd.DataFrame(columns=columns)
                else:
                    raise ValueError("Table '{}' does not exist.".format(tablename))
            else:
                d = pd.read_csv(stream,index_col=None,skipinitialspace=True)
            t = Table(d,dsname=cls.DSNAME,tablename=tablename,filename=filename)

        if columns is None:
            return t
        prov = set(t.columns)
        reqd = set(columns)
        if reqd-prov:
            raise ValueError("Columns missing for table '{}': {}. Required columns are: {}"
                             .format(tablename,list(reqd-prov),columns))
        if prov-reqd:
            if not extrasok:
                raise ValueError("Extra columns for table '{}': {}. Required columns are: '{}'"
                                .format(tablename,list(prov-reqd),columns))
            t = t[columns]
        return t
    
    def write(self,ds_name=None,precision=None,index=False,prefix=None,makedir=False):
        if ds_name is None:
            ds_name = self.ds_name
        dirname = 'data/' + ds_name + '.d'
        if makedir and not os.path.exists(dirname):
            os.mkdir(dirname)
        if prefix is not None:
            dirname = dirname + '/' + prefix
            if makedir and not os.path.exists(dirname):
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

## In [14]:
@register_cell_magic('Table')
def cell_table(line,cell):
    mo = re.match(r'\s*(\S+)\s*$',line)
    if not mo:
        raise ValueError('Usage: %%Table tablename')
    tablename = mo.group(1)
    global DataSet
    DataSet.DSTYPE = 'cell'
    DataSet.set_cell(tablename,cell)

## In [ ]:

