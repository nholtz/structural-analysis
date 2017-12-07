# coding: utf-8

import sys
import importlib
import os.path
from IPython import get_ipython
import nbformat
import io
import time

NBVERSION = 4

def compile_to_py(nb_path,py_path):
    shell = get_ipython()

    # load the notebook object
    with io.open(nb_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f,NBVERSION)

    with io.open(py_path,'w',encoding='utf-8') as pyf:
        pyf.write(u'## Compiled from {} on {}\n'.format(nb_path,time.ctime()))
        for cell in nb['cells']:
            if cell['cell_type'] == 'code':
                # transform the input to executable Python
                ##print ("Source",cell['source'])
                ec = cell['execution_count']
                code = shell.input_transformer_manager.transform_cell(cell['source'])
                if code.startswith('##test:'):
                    continue
                if code.startswith('get_ipython().run_cell_magic('):
                    continue
                if code.startswith('## Test Section:'):
                    pyf.write(u'\n## Import ended by "## Test Section:"\n')
                    break
                if code.startswith('#### End Import ####'):
                    pyf.write(u'\n## Import ended by "#### End Import ####"\n')
                    break

                pyf.write(u'\n')
                pyf.write(u'## In [{}]:\n'.format(' ' if ec is None else ec))
                pyf.write(code)

def must_compile(nb_path,py_path):
    if not os.path.exists(py_path):
        return True
    nbt = os.path.getmtime(nb_path)
    pyt = os.path.getmtime(py_path)
    return pyt < nbt

class NBFinder(importlib.abc.PathEntryFinder):
    
    DEBUG = False
    
    def find_spec(self,fullname,path,target=None):
        if self.DEBUG:
            print('find_spec:',fullname,path,target)
        if path is None:
            path = sys.path
        modname = fullname.split('.')[-1]
        filename = modname + '.ipynb'
        for p in path:
            fullpath = os.path.join(p,filename)
            if os.path.isfile(fullpath):
                if self.DEBUG:
                    print('  found:',fullpath)
                pypath = fullpath[:-5] + 'py'
                if must_compile(fullpath,pypath):
                    if self.DEBUG:
                        print('  compiling to:',pypath)
                    compile_to_py(fullpath,pypath)
                loader = importlib.machinery.SourceFileLoader(fullname,pypath)
                spec = importlib.machinery.ModuleSpec(fullname,loader,origin=pypath)
                return spec
        
        return None
    

__TheNBFinder = NBFinder()

if __TheNBFinder not in sys.meta_path:
    sys.meta_path = [__TheNBFinder] + sys.meta_path

