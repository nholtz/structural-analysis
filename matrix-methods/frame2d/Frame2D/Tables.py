## Compiled from Tables.ipynb on Sat Jun 11 11:09:19 2016

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

## In [16]:
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
        if dsname is not None:
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

## In [26]:
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
                if self.dsname is not None:
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

## In [37]:
@register_cell_magic('Table')
def cell_table(line,celltext):
    mo = re.match(r'\s*(\S+)\s*$',line)
    if not mo:
        raise ValueError('Usage: %%Table tablename')
    tablename = mo.group(1)
    global DataSource
    DataSource.set_celldata(tablename,celltext)

## In [53]:
@extend
class DataSource:
    
    @classmethod
    def write_table(cls,table,root=None,dsname=None,tablename=None,prefix=None,precision=None,index=False,makedir=False):
        self = cls.DATASOURCE
        if root is None:
            root = self.root
        if dsname is None:
            dsname = self.dsname
        if tablename is None:
            tablename = table.tablename
        dirname = root + '/' + dsname + '.d'
        if makedir and not os.path.exists(dirname):
            os.mkdir(dirname)
        if prefix is not None:
            dirname = dirname + '/' + prefix
            if makedir and not os.path.exists(dirname):
                os.mkdir(dirname)
                
        table.tablename = tablename
        table.dsname = dsname
        table.filename = filename = dirname + '/' + tablename + '.csv'
        
        float_format = None
        if precision is not None:
            float_format = '%.{:d}g'.format(precision)
        table.to_csv(filename,index=index,float_format=float_format)
        return filename

## In [43]:
@extend
class Table:
    
    def signature(self):
        filename = self.filename
        if os.path.exists(filename):
            return (self.tablename,self.filename,signature(filename))
        raise ValueError,"Table {}: filename: {} - does not exist.".format(self.tablename,self.filename)
    
def signature(filename):
    f = open(filename,mode='rb')
    m = hashlib.sha256(f.read())
    f.close()
    return m.hexdigest()

## In [44]:
DataSource.DATASOURCE = None
__ds__ = DataSource()

## In [70]:
DataSource.DATASOURCE = None
__ds__ = DataSource()