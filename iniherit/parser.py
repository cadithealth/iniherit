# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: Philip J Grabner <grabner@cadit.com>
# date: 2013/08/20
# copy: (C) Copyright 2013 Cadit Health Inc., All Rights Reserved.
#------------------------------------------------------------------------------

import io, os.path, urllib
try:
  import ConfigParser
except ImportError:
  import configparser as ConfigParser

# TODO: PY3 added a `ConfigParser.read_dict` that should probably
#       be overridden as well...
# TODO: should `ConfigParser.set()` be checked for option==INHERITTAG?...

__all__ = (
  'Loader', 'IniheritMixin', 'IniheritRawConfigParser',
  'IniheritConfigParser', 'IniheritSafeConfigParser',
  )

#------------------------------------------------------------------------------
class Loader(object):
  def load(self, name, encoding=None):
    if encoding is None:
      return open(name)
    return open(name, encoding=encoding)

_real_RawConfigParser  = ConfigParser.RawConfigParser
_real_ConfigParser     = ConfigParser.ConfigParser
_real_SafeConfigParser = ConfigParser.SafeConfigParser

DEFAULT_INHERITTAG = '%inherit'

#------------------------------------------------------------------------------
class IniheritMixin(object):

  #----------------------------------------------------------------------------
  def __init__(self, *args, **kw):
    self.loader = kw.get('loader', None) or Loader()
    self.IM_INHERITTAG  = DEFAULT_INHERITTAG
    self.IM_DEFAULTSECT = getattr(self, 'default_section', ConfigParser.DEFAULTSECT)

  #----------------------------------------------------------------------------
  def read(self, filenames, encoding=None):
    if isinstance(filenames, basestring):
      filenames = [filenames]
    read_ok = []
    for filename in filenames:
      try:
        fp = self._load(filename, encoding=encoding)
      except IOError:
        continue
      self._read(fp, filename, encoding=encoding)
      fp.close()
      read_ok.append(filename)
    return read_ok

  #----------------------------------------------------------------------------
  def _load(self, filename, encoding=None):
    return self.loader.load(filename, encoding=encoding)

  #----------------------------------------------------------------------------
  def _read(self, fp, fpname, encoding=None):
    raw = self._readRecursive(fp, fpname, encoding=encoding)
    self._apply(raw, self)

  #----------------------------------------------------------------------------
  def _makeParser(self):
    ret = _real_RawConfigParser()
    ## TODO: any other configurations that need to be copied into `ret`??...
    ret.optionxform = self.optionxform
    return ret

  #----------------------------------------------------------------------------
  def _readRecursive(self, fp, fpname, encoding=None):
    ret = self._makeParser()
    ret.readfp(fp, fpname)
    dirname = os.path.dirname(fpname)
    if ret.has_option(self.IM_DEFAULTSECT, self.IM_INHERITTAG):
      inilist = ret.get(self.IM_DEFAULTSECT, self.IM_INHERITTAG)
      ret.remove_option(self.IM_DEFAULTSECT, self.IM_INHERITTAG)
      tmp = self._makeParser()
      for curname in inilist.split():
        optional = curname.startswith('?')
        if optional:
          curname = curname[1:]
        curname = os.path.join(dirname, urllib.unquote(curname))
        try:
          curfp = self._load(curname, encoding=encoding)
        except IOError:
          if optional:
            continue
          raise
        self._apply(self._readRecursive(curfp, curname, encoding=encoding), tmp)
      self._apply(ret, tmp)
      ret = tmp
    for section in ret.sections():
      if not ret.has_option(section, self.IM_INHERITTAG):
        continue
      inilist = ret.get(section, self.IM_INHERITTAG)
      ret.remove_option(section, self.IM_INHERITTAG)
      retorig = dict(ret.items(section))
      for curname in inilist.split():
        optional = curname.startswith('?')
        if optional:
          curname = curname[1:]
        fromsect = section
        if '[' in curname and curname.endswith(']'):
          curname, fromsect = curname.split('[', 1)
          fromsect = urllib.unquote(fromsect[:-1])
        curname = os.path.join(dirname, urllib.unquote(curname))
        try:
          curfp = self._load(curname, encoding=encoding)
        except IOError:
          if optional:
            continue
          raise
        self._apply(self._readRecursive(curfp, curname, encoding=encoding), ret,
                    sections={fromsect: section})
      for k, v in retorig.items():
        ret.set(section, k, v)
    return ret

  #----------------------------------------------------------------------------
  def _apply(self, src, dst, sections=None):
    # todo: this does not detect the case that a section overrides
    #       the default section with the exact same value... ugh.
    if sections is None:
      for option, value in src.items(self.IM_DEFAULTSECT):
        dst.set(self.IM_DEFAULTSECT, option, value)
    if sections is None:
      sections = {s: s for s in src.sections()}
    for srcsect, dstsect in sections.items():
      if not dst.has_section(dstsect):
        dst.add_section(dstsect)
      for option, value in src.items(srcsect):
        if src.has_option(self.IM_DEFAULTSECT, option) \
            and value == src.get(self.IM_DEFAULTSECT, option):
          continue
        dst.set(dstsect, option, value)

  #----------------------------------------------------------------------------
  def write(self, *args, **kw):
    # todo: this limitation *could* be lifted by keeping track of
    #       which values are inherited, and not writing those back.
    raise TypeError('IniheritMixin values cannot be written')

#------------------------------------------------------------------------------
# todo: i'm a little worried about the diamond inheritance here...
class IniheritRawConfigParser(IniheritMixin, _real_RawConfigParser):
  def __init__(self, *args, **kw):
    loader = kw.pop('loader', None)
    IniheritMixin.__init__(self, loader=loader)
    _real_RawConfigParser.__init__(self, *args, **kw)
class IniheritConfigParser(IniheritRawConfigParser, _real_ConfigParser):
  def __init__(self, *args, **kw):
    loader = kw.pop('loader', None)
    IniheritRawConfigParser.__init__(self, loader=loader)
    _real_ConfigParser.__init__(self, *args, **kw)
class IniheritSafeConfigParser(IniheritConfigParser, _real_SafeConfigParser):
  def __init__(self, *args, **kw):
    loader = kw.pop('loader', None)
    IniheritConfigParser.__init__(self, loader=loader)
    _real_SafeConfigParser.__init__(self, *args, **kw)

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
