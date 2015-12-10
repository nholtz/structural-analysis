"""After this module is imported, the normal python 'import' statement
will import .ipynb notebook files directly.  Of course, cell execution
does not produce any output when this happens.  Some name munging
occurs:

  import foo.bar_zap

will try to import module file 
   "foo/bar_zap.ipynb", or 
   "foo/bar-zap.ipynb", or
   "foo/bar zap.ipynb"
in that order.

"""

import io, os, sys, types, StringIO
from IPython import nbformat, get_ipython

# http://ipython.org/ipython-doc/3/notebook/nbformat.html
# 

def find_notebook(fullname, path=None):
    """find a notebook, given its fully qualified name and an optional path
    
    This turns "foo.bar" into "foo/bar.ipynb"
    and tries turning "Foo_Bar" into "Foo-Bar" and "Foo Bar" 
    if Foo_Bar does not exist.
    """
    parts = fullname.split('.')
    name1 = parts[-1] + '.ipynb'
    pfx = os.path.join(*parts[:-1]) if len(parts) > 1 else ''
    mpaths = [os.path.join(pfx,name1)]
    name2 = name1.replace('_','-')
    if name2 != name1:
        mpaths.append(os.path.join(pfx,name2))
    name2 = name1.replace('_',' ')
    if name2 != name1:
        mpaths.append(os.path.join(pfx,name2))
    
    if not path:
        path = ['']
    for d in path:
        for p in mpaths:
            nb_path = os.path.join(d,p)
            if os.path.isfile(nb_path):
                return nb_path

class NBModuleType(types.ModuleType):
    
    def __init__(self,fullname,doc=None):
        types.ModuleType.__init__(self,fullname,doc)
        self.__loader__ = None
        self.__ccode__  = None
        self.__loaded__ = False
        
    def __runcode__(self,after=None,silent=False):
        user_ns = get_ipython().user_ns
        try:
            del user_ns['__execution_count__']
        except KeyError:
            pass
        stdout = sys.stdout
        stderr = sys.stderr
        if silent:
            sys.stdout = sys.stderr = StringIO.StringIO()
        try:
            for execution_count,code in self.__ccode__:
                ##print execution_count,code
                if after is not None:
                    if execution_count == after:
                        after = None
                    continue
                if not self.__loaded__:
                    user_ns['__execution_count__'] = execution_count
                    print 'Exec:',code,user_ns['__execution_count__'],execution_count
                exec(code,self.__dict__)
        finally:
            sys.stdout = stdout
            sys.stderr = stderr
        try:
            del user_ns['__execution_count__']
        except KeyError:
            pass

class NotebookLoader(object):
    
    """Module Loader for IPython Notebooks"""
    
    NBVERSION = 4
    
    def __init__(self, path=None):
        self.shell = get_ipython()
        self.path = path
    
    def load_module(self, fullname):
        """import a notebook as a module"""
        path = find_notebook(fullname, self.path)
        
        ##print ("importing IPython notebook from %s" % path)
                                       
        # load the notebook object
        with io.open(path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f,self.NBVERSION)
        
        
        # create the module and add it to sys.modules
        mod = NBModuleType(fullname)
        mod.__file__ = path
        mod.__loader__ = self
        sys.modules[fullname] = mod
        
        # extra work to ensure that magics that would affect the user_ns
        # actually affect the notebook module's ns
        save_user_ns = self.shell.user_ns
        self.shell.user_ns = mod.__dict__
        
        _code = []
        try:
          for cell in nb['cells']:
            if cell['cell_type'] == 'code':
                # transform the input to executable Python
                ##print ("Source",cell['source'])
                ec = cell['execution_count']
                code = self.shell.input_transformer_manager.transform_cell(cell['source'])
                if code.startswith('## Test Section:'):
                    break
                ccode = compile(code,'<file: {0} cell {1}>'.format(path,ec),'exec')
                _code.append((ec,ccode))
        finally:
            self.shell.user_ns = save_user_ns
        mod.__ccode__ = _code
        mod.__runcode__(after=None,silent=True)
        mod.__loaded__ = True
        return mod

class NotebookFinder(object):
    """Module finder that locates IPython Notebooks"""
    def __init__(self):
        self.loaders = {}
    
    def find_module(self, fullname, path=None):
        nb_path = find_notebook(fullname, path)
        if not nb_path:
            return
        
        key = path
        if path:
            # lists aren't hashable
            key = os.path.sep.join(path)
        
        if key not in self.loaders:
            self.loaders[key] = NotebookLoader(path)
        return self.loaders[key]


sys.meta_path.append(NotebookFinder())


