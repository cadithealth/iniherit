# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: Philip J Grabner <grabner@cadit.com>
# date: 2013/08/20
# copy: (C) Copyright 2013 Cadit Health Inc., All Rights Reserved.
#------------------------------------------------------------------------------

import ConfigParser
from .parser import RawConfigParser, ConfigParser, SafeConfigParser

#------------------------------------------------------------------------------
def install_globally():
  '''
  Installs :class:`iniherit.parser.RawConfigParser` as the
  global :class:`ConfigParser.RawConfigParser` (and the standard and
  safe sub-classes). Note that this is what one calls
  "dangerous". Please use with extreme caution.
  '''
  if ConfigParser.ConfigParser is ConfigParser:
    return
  ConfigParser._real_RawConfigParser  = ConfigParser.RawConfigParser
  ConfigParser._real_ConfigParser     = ConfigParser.ConfigParser
  ConfigParser._real_SafeConfigParser = ConfigParser.SafeConfigParser
  ConfigParser.RawConfigParser        = RawConfigParser
  ConfigParser.ConfigParser           = ConfigParser
  ConfigParser.SafeConfigParser       = SafeConfigParser

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
