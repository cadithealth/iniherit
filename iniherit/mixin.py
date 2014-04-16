# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: Philip J Grabner <grabner@cadit.com>
# date: 2013/08/20
# copy: (C) Copyright 2013 Cadit Health Inc., All Rights Reserved.
#------------------------------------------------------------------------------

import six
from six.moves import configparser as CP

from .parser import IniheritMixin

#------------------------------------------------------------------------------

# todo: should this perhaps use the `stub` package instead?...

attrs = [attr for attr in dir(IniheritMixin) if not attr.startswith('__')]

#------------------------------------------------------------------------------
def install_globally():
  '''
  Installs '%inherit'-enabled processing as the global default. Note
  that this is what one calls "dangerous". Please use with extreme
  caution.
  '''
  if hasattr(CP.RawConfigParser, '_iniherit_installed_'):
    return
  setattr(CP.RawConfigParser, '_iniherit_installed_', True)
  for attr in attrs:
    if hasattr(CP.RawConfigParser, attr):
      setattr(CP.RawConfigParser,
              '_iniherit_' + attr, getattr(CP.RawConfigParser, attr))
    meth = getattr(IniheritMixin, attr)
    if six.callable(meth):
      if six.PY2:
        import new
        meth = new.instancemethod(meth.__func__, None, CP.RawConfigParser)
      else:
        meth = meth.__get__(None, CP.RawConfigParser)
    setattr(CP.RawConfigParser, attr, meth)

#------------------------------------------------------------------------------
def uninstall_globally():
  '''
  Reverts the effects of :func:`install_globally`.
  '''
  if not hasattr(CP.ConfigParser, '_iniherit_installed_'):
    return
  delattr(CP.RawConfigParser, '_iniherit_installed_')
  for attr in attrs:
    if hasattr(CP.RawConfigParser, '_iniherit_' + attr):
      xattr = getattr(CP.RawConfigParser, '_iniherit_' + attr)
      setattr(CP.RawConfigParser, attr, xattr)
    else:
      delattr(CP.RawConfigParser, attr)

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
