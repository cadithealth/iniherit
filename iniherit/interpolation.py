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
class InterpolationMissingSuperError(CP.InterpolationMissingOptionError): pass

#------------------------------------------------------------------------------
_env_cre = re.compile(r'%\(ENV:([^:)]+)(:-([^)]*))?\)s', flags=re.DOTALL)
_super_cre = re.compile(r'%\(SUPER(:-([^)]*))?\)s', flags=re.DOTALL)
def interpolate(parser, base_interpolate, section, option, rawval, vars):
  value = rawval
  depth = CP.MAX_INTERPOLATION_DEPTH
  erepl = lambda match: _env_replace(
    match, parser, base_interpolate, section, option, rawval, vars)
  srepl = lambda match: _super_replace(
    match, parser, parser, None, section, option, rawval, vars)
  while depth and ( _env_cre.search(value) or _super_cre.search(value) ):
    depth -= 1
    value = _env_cre.sub(erepl, value)
    value = _super_cre.sub(srepl, value)
  if not depth and ( _env_cre.search(value) or _super_cre.search(value) ):
    raise CP.InterpolationDepthError(option, section, rawval)
  if '%(SUPER)s' in value:
    raise InterpolationMissingSuperError(option, section, rawval, 'SUPER')
  return base_interpolate(parser, section, option, value, vars)

#------------------------------------------------------------------------------
def interpolate_super(parser, src, dst, section, option, value):
  srepl = lambda match: _super_replace(
    match, parser, src, dst, section, option, value, None)
  value = _super_cre.sub(srepl, value)
  return value

#------------------------------------------------------------------------------
def _env_replace(match, parser, base_interpolate, section, option, rawval, vars):
  if match.group(1) in os.environ:
    return os.environ.get(match.group(1))
  if match.group(2):
    return match.group(3)
  raise InterpolationMissingEnvError(option, section, rawval, match.group(1))

#------------------------------------------------------------------------------
def _super_replace(match, parser, src, dst, section, option, rawval, vars):
  if dst \
     and ( section == parser.IM_DEFAULTSECT or dst.has_section(section) ) \
     and dst.has_option(section, option):
    try:
      return dst.get(section, option, raw=True, vars=vars)
    except TypeError:
      return dst.get(section, option)
  if dst:
    return match.group(0)
  if match.group(1):
    return match.group(2)
  raise InterpolationMissingSuperError(option, section, rawval, 'SUPER')

#------------------------------------------------------------------------------
# end of $Id$
# $ChangeLog$
#------------------------------------------------------------------------------
