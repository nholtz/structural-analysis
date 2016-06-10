## Compiled from Tables.ipynb on Thu Jun  9 22:30:14 2016

## In [1]:
from __future__ import print_function

from salib import extend
import pandas as pd
import os, os.path
import StringIO
import hashlib
from IPython.core.magic import register_cell_magic
import re

## In [2]:
class Table(pd.DataFrame):
    
    """A Table is just like a pandas DataFrame except that it has
    a table name, a data set name, and a file name - the latter two describing
    the source of the data."""
    
    _internal_names = pd.DataFrame._internal_names + ['filename','tablename']
    _internal_names_set = set(_internal_names)

    _metadata = ['dsname']
            
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

## In [13]:
class DataSource(object):
    
    ROOT = 'data'
    DSNAME = None     # default data set name
    DSTYPE = 'dir'    # someday we will allow 'zip' for zip archives
    #DSTYPE = 'cell'  # for CSV data provided via %%Table cell magic
    #DSTYPE = 'data'  # for dataframe data provided directly
    CELLDATA = {}     # csv text from %%Table magic cells, indexed by table name
    TABLES = {}       # dataframes directly provided by client, indexed by table name
    
    DATASOURCE = None # the one and only data source
    
    def __init__(self):
        cls = self.__class__
        if cls.DATASOURCE is not None:
            raise ValueError("Can only create one instance of class '{}'".format(cls.__name__))
        self.root = cls.ROOT
        self.dsname = cls.DSNAME
        self.prefix = None
        self.dstype = cls.DSTYPE
        self.celldata = cls.CELLDATA
        self.tables = cls.TABLES
        cls.DATASOURCE = self

## In [26]:
@extend
class DataSource:
    
    @classmethod
    def set_root(cls,newroot):
        self = cls.DATASOURCE
        if not os.path.exists(newroot):
            raise ValueError,"Root '{}' does not exist.".format(newroot)
        self.root = newroot

    @classmethod
    def set_source(cls,dsname,dstype=None):
        self = cls.DATASOURCE
        if dstype is None:
            dirname = self.root + '/' + dsname + '.d'
            if os.path.exists(dirname):
                dstype = 'dir'
            else:
                dstype = 'unknown'
        if dstype not in ['dir','cell','data']:
            raise ValueError,"dstype '{}' is invalid.".format(dstype)
        self.dsname = dsname
        self.dstype = dstype
        self.celldata = {}
        self.tables = {}
        
    @classmethod
    def set_table(cls,tablename,table):
        self = cls.DATASOURCE
        self.tables[tablename] = table
        if tablename in self.celldata:
            del self.celldata[tablename]
    
    @classmethod
    def set_celldata(cls,tablename,celltext):
        self = cls.DATASOURCE
        self.celldata[tablename] = celltext
        if tablename in self.tables:
            del self.tables[tablename]
    
    def _file_name(self,tablename,prefix=None):
        n = tablename
        if prefix:
            n = prefix + '/' + tablename
        return self.root + '/' + self.dsname + '.d/' + n + '.csv'

## In [45]:
@extend
class DataSource:
    
    @classmethod
    def read_table(cls,tablename,optional=False,prefix=None,columns=None,extrasok=True):
        self = cls.DATASOURCE
        stream = None
        filename = None
        t = None
        if tablename in self.tables:
            t = self.tables[tablename]
        else:
            if tablename in self.celldata:
                stream = StringIO.StringIO(self.celldata[tablename])
            else:
                filename = self._file_name(tablename,prefix=prefix)
                if os.path.exists(filename):
                    stream = file(filename,'r')
            if stream is None:
                if optional:
                    d = pd.DataFrame(columns=columns)
                else:
                    raise ValueError("Table '{}' does not exist.".format(tablename))
            else:
                d = pd.read_csv(stream,index_col=None,skipinitialspace=True)
            t = Table(d,dsname=self.dsname,tablename=tablename,filename=filename)

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

## In [62]:
@register_cell_magic('Table')
def cell_table(line,celltext):
    mo = re.match(r'\s*(\S+)\s*$',line)
    if not mo:
        raise ValueError('Usage: %%Table tablename')
    tablename = mo.group(1)
    global DataSource
    DataSource.set_celldata(tablename,celltext)

## In [ ]:
@extend
class DataSource:
    
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
    
def signature(file_name):
    f = open(file_name,mode='rb')
    m = hashlib.sha256(f.read())
    f.close()
    return m.hexdigest()

## In [70]:
DataSource.DATASOURCE = None
__ds__ = DataSource()

## In [ ]:

