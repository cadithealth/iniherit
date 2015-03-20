# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: Philip J Grabner <grabner@cadit.com>
# date: 2013/08/20
# copy: (C) Copyright 2013 Cadit Health Inc., All Rights Reserved.
#------------------------------------------------------------------------------

import unittest
import io
import six

from iniherit.parser import Loader, ConfigParser, SafeConfigParser

#------------------------------------------------------------------------------
class ByteLoader(Loader):
  def __init__(self, *args, **kw):
    self.items = dict()
    self.items.update(*args, **kw)
  def load(self, name, encoding=None):
    if name not in self.items:
      raise IOError(2, 'No such file or directory', name)
    ret = six.StringIO(self.items[name])
    ret.name = name
    return ret

#------------------------------------------------------------------------------
class TestIniherit(unittest.TestCase):

  #----------------------------------------------------------------------------
  def test_iniherit(self):
    files = [
      ('base.ini', '''\
[DEFAULT]
kw1 = base-kw1
kw2 = base-kw2
[section]
test1 = only in base, the value "%(kw1)s" should be "base-kw1"
test2 = the value "%(kw2)s" should be "base-kw2"
'''),
      ('extend.ini', '''\
[DEFAULT]
%inherit = base.ini
kw1 = extend-kw1
'''),
    ]
    parser = ConfigParser(loader=ByteLoader(dict(files)))
    parser.read('extend.ini')
    self.assertEqual(parser.get('DEFAULT', 'kw1'), 'extend-kw1')
    self.assertEqual(parser.get('DEFAULT', 'kw2'), 'base-kw2')
    self.assertEqual(parser.get('section', 'test1'),
                     'only in base, the value "extend-kw1" should be "base-kw1"')
    self.assertEqual(parser.get('section', 'test2'),
                     'the value "base-kw2" should be "base-kw2"')
    self.assertFalse(parser.has_option('DEFAULT', '%inherit'))

  #----------------------------------------------------------------------------
  def test_iniherit_multiple(self):
    files = [
      ('base.ini', '''\
[DEFAULT]
kw1 = base-kw1
kw2 = base-kw2
kw3 = base-kw3
kw4 = base-kw4
'''),
      ('override.ini', '''\
[DEFAULT]
kw2 = override-kw2
kw3 = override-kw3
kw5 = override-kw5
'''),
      ('extend.ini', '''\
[DEFAULT]
%inherit = base.ini ?no-such-ini.ini override.ini
kw1 = extend-kw1
kw3 = extend-kw3
kw6 = extend-kw6
'''),
    ]
    parser = ConfigParser(loader=ByteLoader(dict(files)))
    parser.read('extend.ini')
    self.assertEqual(parser.get('DEFAULT', 'kw1'), 'extend-kw1')
    self.assertEqual(parser.get('DEFAULT', 'kw2'), 'override-kw2')
    self.assertEqual(parser.get('DEFAULT', 'kw3'), 'extend-kw3')
    self.assertEqual(parser.get('DEFAULT', 'kw4'), 'base-kw4')
    self.assertEqual(parser.get('DEFAULT', 'kw5'), 'override-kw5')
    self.assertEqual(parser.get('DEFAULT', 'kw6'), 'extend-kw6')

  #----------------------------------------------------------------------------
  def test_iniherit_noSuchFile(self):
    files = [
      ('base.ini',   '[DEFAULT]\nkw1 = base-kw1\n'),
      ('extend.ini', '[DEFAULT]\n%inherit = base.ini no-such-ini.ini\nkw2 = extend-kw2\n'),
    ]
    parser = ConfigParser(loader=ByteLoader(dict(files)))
    self.assertRaises(IOError, parser.read, 'extend.ini')

  #----------------------------------------------------------------------------
  def test_iniherit_relativePath(self):
    files = [
      ('dir/base.ini', '[section]\nkw1 = base-kw1\n'),
      ('dir/mid.ini',  '[DEFAULT]\n%inherit = base.ini\n[section]\nkw2 = mid-kw2\n'),
      ('extend.ini',   '[DEFAULT]\n%inherit = dir/mid.ini\n[section]\nkw3 = extend-kw3\n'),
    ]
    parser = ConfigParser(loader=ByteLoader(dict(files)))
    parser.read('extend.ini')
    self.assertEqual(parser.get('section', 'kw1'), 'base-kw1')
    self.assertEqual(parser.get('section', 'kw2'), 'mid-kw2')
    self.assertEqual(parser.get('section', 'kw3'), 'extend-kw3')

  #----------------------------------------------------------------------------
  def test_iniherit_nameWithSpace(self):
    files = [
      ('base + space.ini', '[DEFAULT]\nkw=word\n'),
      ('config.ini',       '[DEFAULT]\n%inherit = base%20%2b%20space.ini\n'),
    ]
    parser = ConfigParser(loader=ByteLoader(dict(files)))
    parser.read('config.ini')
    self.assertEqual(parser.get('DEFAULT', 'kw'), 'word')

  #----------------------------------------------------------------------------
  def test_iniherit_sectionInherit(self):
    files = [
      ('base.ini',   '[DEFAULT]\nkw1=word\n[s]\nfoo=bar\nx=y\n'),
      ('other.ini',  '[DEFAULT]\nkw2=word\n[so]\nzig=zag\n'),
      ('config.ini', '[s]\n%inherit = base.ini other.ini[so]\nx=z\n'),
    ]
    parser = ConfigParser(loader=ByteLoader(dict(files)))
    parser.read('config.ini')
    self.assertEqual(parser.items('DEFAULT'), [])
    self.assertEqual(sorted(parser.items('s')),
                     sorted(dict(foo='bar', zig='zag', x='z').items()))

  #----------------------------------------------------------------------------
  def test_iniherit_interpolation(self):
    files = [
      ('config.ini', '[app]\noutput = %(tmpdir)s/var/result.log\n'),
    ]
    parser = SafeConfigParser(
      defaults={'tmpdir': '/tmp'}, loader=ByteLoader(dict(files)))
    parser.read('config.ini')
    self.assertEqual(parser.get('app', 'output'), '/tmp/var/result.log')
    self.assertEqual(parser.get('app', 'output', raw=True), '%(tmpdir)s/var/result.log')

  #----------------------------------------------------------------------------
  def test_iniherit_invalidInterpolationValues(self):
    files = [
      ('config.ini', '[logger]\ntimefmt=%H:%M:%S\n'),
    ]
    parser = SafeConfigParser(loader=ByteLoader(dict(files)))
    parser.read('config.ini')
    self.assertEqual(parser.items('DEFAULT'), [])
    self.assertEqual(parser.get('logger', 'timefmt', raw=True), '%H:%M:%S')

  #----------------------------------------------------------------------------
  def test_install_globally(self):
    from iniherit.parser import CP
    from iniherit.mixin import install_globally, uninstall_globally

    files = [
      ('base.ini',   '[DEFAULT]\nkw = base-kw\n'),
      ('config.ini', '[DEFAULT]\n%inherit = base.ini\n'),
    ]
    loader = ByteLoader(dict(files))

    def do_the_test():
      # first test that inheritance doesn't work
      parser = CP.ConfigParser()
      parser.loader = loader
      parser.readfp(loader.load('config.ini'))
      with self.assertRaises(CP.NoOptionError):
        parser.get('DEFAULT', 'kw')
      # then monkey-patch and test that inheritance does work
      install_globally()
      parser = CP.ConfigParser()
      parser.loader = loader
      parser.readfp(loader.load('config.ini'))
      self.assertEqual(parser.get('DEFAULT', 'kw'), 'base-kw')
      uninstall_globally()

    do_first_test = do_second_test = do_the_test
    do_first_test()
    do_second_test()

  #----------------------------------------------------------------------------
  def test_output_order_ascending(self):
    files = [
      ('base.ini', '[s1]\ns1v = b1\n[s2]\ns2v = b2\n[s3]\ns3v = b3\n'),
      ('extend.ini', '[DEFAULT]\n%inherit = base.ini\n[s2]\ns2v = o2'),
    ]
    parser = ConfigParser(loader=ByteLoader(dict(files)))
    parser.read('extend.ini')
    output = six.StringIO()
    parser.write(output)
    self.assertMultiLineEqual(
      output.getvalue(),
      '[s1]\ns1v = b1\n\n[s2]\ns2v = o2\n\n[s3]\ns3v = b3\n\n')

  #----------------------------------------------------------------------------
  def test_output_order_descending(self):
    files = [
      ('base.ini', '[s3]\ns3v = b3\n[s2]\ns2v = b2\n[s1]\ns1v = b1\n'),
      ('extend.ini', '[DEFAULT]\n%inherit = base.ini\n[s2]\ns2v = o2'),
    ]
    parser = ConfigParser(loader=ByteLoader(dict(files)))
    parser.read('extend.ini')
    output = six.StringIO()
    parser.write(output)
    self.assertMultiLineEqual(
      output.getvalue(),
      '[s3]\ns3v = b3\n\n[s2]\ns2v = o2\n\n[s1]\ns1v = b1\n\n')

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
