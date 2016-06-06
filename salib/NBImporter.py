
# coding: utf-8

# ## Notebook Importer
# Importing the module created from this notebook allows you to 
# directly import other notebooks.
# #### Instructions
# This notebook file must be manually downloaded as a `.py` file and 
# copied to a correct location (because it can't be directly
# imported until it has been imported :-)).
# 
# Then do:
# ```
# from NBImporter import import_notebooks   # or some such
# import_notebooks()                        # to enable the importer
# ```
# 
# Note that ```salib``` has a module that enabales the importer automatically.
# Using that, all you have to do is:
# 
# ```
# from salib import import_notebooks
# ```
# 
# #### Implementation Method
# The basic method is to translate
# the notebook file to a Python (`.py`) file (but only if necessary) 
# and then letting the normal import mechanism handle that (which
# means it can also be compiled to a `.pyc file`).  The `.find_module()`
# does the compiling to `.py` when it locates the proper `.ipynb` file, then returns
# `None` to indicate it didn't find anything.  The importer will then try
# the next import method in the chain.

# In[1]:

from __future__ import print_function

import sys
import os, os.path
from IPython import get_ipython
import nbformat
import io
import time


# In[ ]:

class NotebookImporter(object):
    
    """Module finder that locates IPython Notebooks and
    translates them to Python, then lets the normal import
    mechanism handle them.
    """
    
    NBVERSION = 4

    def __init__(self):
        pass
    
    def find_module(self, fullname, path=None):
        
        nb_path = self._find_notebook(fullname, path)
        if not nb_path:
            ##print('Notebook not found.')
            return None
        
        ##print('Found:', nb_path)
        if nb_path.endswith('.ipynb'):
            py_path = nb_path[:-6] + '.py'
        else:
            py_path = nb_path + '.py'
        if self._must_compile(nb_path,py_path):
            print("Compiling notebook '{}' to '{}'.".format(nb_path,py_path))
            self._compile_to_py(nb_path,py_path)
            
        return None  # punt to normal import mechanism
    
    def _find_notebook(self, fullname, path=None):
        """find a notebook, given its fully qualified name and an optional path

        This turns "foo.bar" into "foo/bar.ipynb"
        and tries turning "Foo_Bar" into "Foo-Bar" and "Foo Bar" 
        if Foo_Bar does not exist.
        """
        ##print('find_notebook args:',fullname,path)
        parts = fullname.split('.')
        name1 = parts[-1] + '.ipynb'
        mpaths = [name1]
        if '_' in name1:
            mpaths.append(name1.replace('_','-'))
            mpaths.append(name1.replace('_',' '))

        if not path:
            path = ['']
        for d in path:
            for p in mpaths:
                nb_path = os.path.join(d,p)
                ##print('find_notebook trying:',nb_path)
                if os.path.isfile(nb_path):
                    return nb_path
                
    def _must_compile(self,nb_path,py_path):
        if not os.path.exists(py_path):
            return True
        nbt = os.path.getmtime(nb_path)
        pyt = os.path.getmtime(py_path)
        return pyt < nbt
    
    def _compile_to_py(self,nb_path,py_path):
        
        shell = get_ipython()
                                       
        # load the notebook object
        with io.open(nb_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f,self.NBVERSION)
        
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


# **NOTE:** It might be possible to have an argument to optionally disable magics, output, etc ...
# It might be necessary to force recompile, but that leads to ugly non-localness ...

# In[3]:

def import_notebooks():
    for x in sys.meta_path:
        if type(x) is NotebookImporter:
            return
    sys.meta_path.append(NotebookImporter())


# #### Ugliness!
# One problem with compile-to-py and `import_notebooks()` is if you forget to call it (or even forget
# to import this module), your import statements may grab old out-of-date .py files and you might
# never know about it ....

# In[ ]:



