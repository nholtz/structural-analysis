## Compiled from Fred/George/TestModule.py on Wed May 18 19:29:58 2016

## In [ ]:
try:
    get_ipython
except:
    import sys
    def get_ipython():
        class dummy(object):
            def run_cell_magic(*args):
                print "No IPython; therefore no magic!"
            magic = run_cell_magic
        return dummy()

## In [2]:
def foo():
    return 'bar'

## In [3]:
get_ipython().magic(u'ls')

## In [1]:
get_ipython().run_cell_magic(u'test', u'', u'a = 3\nb = 4\na+b')

## In [4]:
get_ipython().magic(u'lsmagic')

## In [4]:
#%%sh
#ls -l *

## In [5]:
get_ipython().run_cell_magic(u'bash', u'', u'ls -l\n/bin/pwd\necho "foo bar"')

## Import ended by "## Test Section:"
