
# coding: utf-8

# ## Notebook Importer
# Importing the module created from this notebook allows you to 
# directly import other notebooks.  This is done by translating
# the notebook file to a Python (.py) file (only if necessary) 
# and letting the normal import mechanism handle that.
# #### Instructions
# This notebook file must be manually downloaded as a .py file and 
# copied to the correct location (because it can't be directly
# imported until it has been imported :-)).

# In[48]:

from __future__ import print_function

import sys
import os, os.path
from IPython import get_ipython
import nbformat
import io
import time


# In[74]:

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
            pyf.write(u'## Compiled from {} on {}\n'.format(py_path,time.ctime()))
            for cell in nb['cells']:
                if cell['cell_type'] == 'code':
                    # transform the input to executable Python
                    ##print ("Source",cell['source'])
                    ec = cell['execution_count']
                    code = shell.input_transformer_manager.transform_cell(cell['source'])
                    if code.startswith('## Test Section:'):
                        pyf.write(u'\n## Import ended by "## Test Section:"\n')
                        break
                    if code.startswith('#### End Import ####'):
                        pyf.write(u'\n## Import ended by "#### End Import ####"\n')
                        break

                    pyf.write(u'\n')
                    pyf.write(u'## In [{}]:\n'.format(' ' if ec is None else ec))
                    pyf.write(code)


# In[75]:

sys.meta_path.append(NotebookImporter())


# In[ ]:



