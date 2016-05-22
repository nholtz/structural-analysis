# empty file so salib can be a module

from __future__ import print_function
import sys
import inspect
import types
import os
import os.path
import imghdr

from IPython import display

def __test_svg(bstream,fileobj):
    """Extension for imghdr to detect svg files."""
    if fileobj:
        fileobj.seek(0)
        data = fileobj.read(6)
    else:
        data = bstream.read(6)
    if data == b'<?xml ':  # IFFY!
        return 'svg'
    return None
imghdr.tests.append(__test_svg)

EXTS = ['svg','png','jpeg','jpg']

def showImage(basename,rescan=False):
    """Display an image whose basename is 'basename'.  If an image
    cannot be found, the user is asked to scan an image, which is
    then installed.  Extensions '.jpg', '.png', '.svg' are tried in
    that order.  If rescan is True, scanning a new image is forced."""

    def _display(ifile):
        itype = imghdr.what(ifile)
        img = None
        if itype in ['jpeg','png']:
            img = display.Image(filename=ifile,embed=True)
        elif itype == 'svg':
            with open(ifile,"rb") as inf:
                svgdata = inf.read()
            img = display.SVG(data=svgdata)
        else:
            raise Exception("Invalid image type: {0}".format(itype))
        if img:
            display.display(img)

    if not rescan:
        if os.path.exists(basename):
            _display(basename)
            return
        for ext in EXTS:
            ifile = basename + '.' + ext
            if os.path.exists(ifile):
                _display(ifile)
                return
                
    ifile = basename + '.' + EXTS[-1]
    cmd = "scan-to-file {0}".format(ifile)
    os.system(cmd)
    if os.path.exists(ifile):
        _display(ifile)
    else:
        raise Exception("Unable to find image '{0}'; Tried these extensions: {1}".format(basename,EXTS))

from NBImporter import import_notebooks

def extend(old):
    """This is used as a class decorator to 'extend' class definitions,
    for example, over widely dispersed areas.  EG:

        class Foo(object):
            . . .
        @extend(Foo)
        class Foo:
            def meth2(...):
            . . .

    will result in one class Foo containing all methods, etc."""

    def _extend(new,old=old):
        if new.__name__ != old.__name__:
            raise TypeError("Class names must match: '{}' != '{}'".format(new.__name__,old.__name__))
        if type(new) is not types.ClassType:
            raise TypeError("Extension class must be an old-style class (i.e. not derived from class object)")
        if len(new.__bases__) != 0:
            raise TypeError("Extension class must not have any base classes.")
        ng = ['__doc__','__module__']
        for a,v in inspect.getmembers(new):
            if a not in ng:
                if type(v) is types.MethodType:
                    if v.im_self is None:
                        v =  types.MethodType(v.im_func,None,old)
                    else:
                        v = classmethod(v.im_func)
                elif type(v) is property:
                    v = property(v.fget,v.fset,v.fdel)
                elif type(v) is types.FunctionType:
                    v = staticmethod(types.FunctionType(v.func_code,v.func_globals,v.func_name,v.func_defaults,v.func_closure))
                setattr(old,a,v)
                #print('Set {} in class {} to type {}'.format(a,old.__name__,type(v)))
        return old
    
    return _extend
