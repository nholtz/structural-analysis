## Compiled from Fred/George/TestModule.py on Mon May 16 11:17:55 2016

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

## In [4]:
#%%sh
#ls -l *

## In [5]:
get_ipython().run_cell_magic(u'bash', u'', u'ls -l\n/bin/pwd\necho "foo bar"')

## Import ended by "## Test Section:"
