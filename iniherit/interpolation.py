# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: Philip J Grabner <grabner@cadit.com>
# date: 2016/12/14
# copy: (C) Copyright 2016-EOT Cadit Inc., All Rights Reserved.
#------------------------------------------------------------------------------

import re
import os

from six.moves import configparser as CP

#------------------------------------------------------------------------------
class InterpolationMissingEnvError(CP.InterpolationMissingOptionError): pass

#------------------------------------------------------------------------------
_env_cre = re.compile(r'%\(ENV:([^:)]+)(:-([^)]*))?\)s', flags=re.DOTALL)
def interpolate(parser, base_interpolate, section, option, rawval, vars):
  value = rawval
  depth = CP.MAX_INTERPOLATION_DEPTH
  repl  = lambda match: _env_replace(
    match, parser, base_interpolate, section, option, rawval, vars)
  while depth and _env_cre.search(value):
    depth -= 1
    value = _env_cre.sub(repl, value)
  if _env_cre.search(value):
    raise CP.InterpolationDepthError(option, section, rawval)
  if '%(SUPER)s' in value:
    raise InterpolationMissingSuperError(option, section, rawval, 'SUPER')
  return base_interpolate(parser, section, option, value, vars)

#------------------------------------------------------------------------------
def _env_replace(match, parser, base_interpolate, section, option, rawval, vars):
  if match.group(1) in os.environ:
    return os.environ.get(match.group(1))
  if match.group(2) is not None:
    return match.group(3)
  raise InterpolationMissingEnvError(option, section, rawval, match.group(1))

#------------------------------------------------------------------------------
# end of $Id$
# $ChangeLog$
#------------------------------------------------------------------------------
