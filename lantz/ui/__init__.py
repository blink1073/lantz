# -*- coding: utf-8 -*-
"""
    lantz.ui
    ~~~~~~~~

    Implements UI functionality for lantz using Qt.

    You can choose which python bindings to use by setting the
    environmental variable QTBINDINGS to PySide or PyQt4.
    If unset, PyQt4 is tried first, then PySide.

    :copyright: 2012 by Lantz Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

import os
import imp
import sys

from lantz import PY2

class ReplaceImport(object):
    """Hook that replace imports of a package by another.

    :param old: package to be replaced.
    :param new: package to be used.
    """

    def __init__(self, old, new):
        self.old = old
        self.new = new

    def find_module(self, fullname, path=None):
        if fullname.startswith(self.old) and path is None:
            fullname = self.new + fullname[len(self.old):]
            self.mod_data = imp.find_module(fullname)
            return self
        elif PY2 and fullname.startswith(self.old):
            fullname = self.new + fullname[len(self.old):]
            __import__(fullname)
        return None

    def load_module(self, fullname):
        return imp.load_module(fullname, *self.mod_data)

    def register(self):
        if self not in sys.meta_path:
            sys.meta_path.append(self)

    def unregister(self):
        if self in sys.meta_path:
            sys.meta_path.remove(self)

#: Valid QTBINDINGS
_VALID = 'PyQt4', 'PySide'

# Read QTBINDINGS environmental variable, if not found try all valid.
try:
    qtbindings = os.environ['QTBINDINGS']
    if qtbindings not in _VALID:
        raise ImportError('{} is not a valid value for QTBINDINGS {}'.format(qtbindings, _VALID))
except KeyError:
    for qtbindings in _VALID:
        try:
            imp.find_module(qtbindings)
            break
        except ImportError:
            pass
    else:
        raise ImportError('lantz.ui requires {}'.format(_VALID))

# Create hook and register it.
_QtHook = ReplaceImport('Qt', qtbindings)
_QtHook.register()

if PY2:
    import sip
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)

# If PyQt4 bindings are used, patch them.
if qtbindings == 'PyQt4':
    import Qt.QtCore as core
    core.Signal = core.pyqtSignal
    core.Slot = core.pyqtSlot
    core.Property = core.pyqtProperty
    del core
