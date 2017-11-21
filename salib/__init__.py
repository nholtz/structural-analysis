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


def extend(newcls):
    
    """A class decorator to 'extend' class definitions
    EG:

        class Foo:
            def __init__(...):
                . . .
            def meth1(...):
                . . .
            . . .
        . . .
        @extend
        class Foo:
            def meth2(...):
            . . .

    will result in one class Foo (the original one) containing all methods, 
    eg, meth1, meth2, etc. All methods with names beginning and
    ending with '__' must be defined in the original, unextended, definition."""

    clsname = newcls.__name__
    oldcls = getattr(sys.modules[newcls.__module__],clsname,None)
    if oldcls is None:
        raise TypeError("Class '{}' not previously defined; therefore cannot be extended."
                        .format(clsname))

    if len(newcls.__bases__) > 1 or (len(newcls.__bases__) == 1 and newcls.__bases__[0] is not object):
        raise TypeError("Class '{}' extension cannot have any base classes."
                        .format(clsname))

    for a,v in newcls.__dict__.items():
        if not a.startswith('__') or not a.endswith('__'):
            ## print(a,v,type(v))
            if hasattr(oldcls,a):
                raise TypeError("Attribute '{}' in extended class '{}' already exists. Cannot be redefined."
                               .format(a,clsname))
            setattr(oldcls,a,v)
            
    return oldcls