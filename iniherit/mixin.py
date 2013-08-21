# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: Philip J Grabner <grabner@cadit.com>
# date: 2013/08/20
# copy: (C) Copyright 2013 Cadit Health Inc., All Rights Reserved.
#------------------------------------------------------------------------------

try:
  import ConfigParser as CP
except ImportError:
  import configparser as CP
from .parser import RawConfigParser, ConfigParser, SafeConfigParser

#------------------------------------------------------------------------------
def install_globally():
  '''
  Installs :class:`iniherit.parser.RawConfigParser` as the global
  :class:`ConfigParser.RawConfigParser` (and the standard and safe
  sub-classes). Note that this is what one calls "dangerous". Please
  use with extreme caution.
  '''
  if CP.ConfigParser is ConfigParser:
    return
  CP._real_RawConfigParser  = CP.RawConfigParser
  CP._real_ConfigParser     = CP.ConfigParser
  CP._real_SafeConfigParser = CP.SafeConfigParser
  CP.RawConfigParser        = RawConfigParser
  CP.ConfigParser           = ConfigParser
  CP.SafeConfigParser       = SafeConfigParser

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
