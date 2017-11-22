#!/usr/bin/env python3

import sys
import os, os.path
from IPython import get_ipython
import nbformat
import io
import time

NBVERSION = 4

def _compile_to_py(nb_path,py_path):

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

if __name__ == '__main__':

    for inf in sys.argv[1:]:
        if inf.endswith('.ipynb'):
            outf = inf[:-6] + '.py'
        else:
            outf = inf + '.py'
        print('Compiling {} => {}'.format(inf,outf))
        _compile_to_py(inf,outf)
        
