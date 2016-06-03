import inspect
try:
    inspect.signature   # if this exists, then we are using Python 3.0
    import collections
    def getArgSpec(fn):
        """Simulate inpect.getargspec from Python 2.7 for Python 3.0, because the
        inpect module thats been backported to 2.7 isn't easily or automatically
        available in 2.7.  So we forward port old getargspec to 3.0 to circumvent
        the deprecation warning messages at run time."""
        sig = inspect.signature(fn)
        aspec = collections.namedtuple('ArgSpec','args,varargs,keywords,defaults')
        args = [k for k,p in sig.parameters.items() if p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD]
        va = [k for k,p in sig.parameters.items() if p.kind == inspect.Parameter.VAR_POSITIONAL]
        varargs = va[0] if len(va) >= 1 else None
        kw =[k for k,p in sig.parameters.items() if p.kind == inspect.Parameter.VAR_KEYWORD]
        keywords = kw[0] if len(kw) >= 1 else None
        defaults = [p.default for k,p in sig.parameters.items() if p.default != inspect._empty]
        return aspec(args,varargs,keywords,defaults)
except:
    getArgSpec = inspect.getargspec  # use the one from 2.7 as is

def extend(old):
    """A decorator to extend class definitions.  Caution, only
    works with normal methods; does not work with properties,
    class mewthods or static methods in the new class fragment."""
    def _fn(new,old=old):
        for a,v in inspect.getmembers(new):
            if not a.startswith('_'):
                setattr(old,a,v)
        return old
    return _fn