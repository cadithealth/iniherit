====================
INI File Inheritance
====================

Adds INI-file inheritance to ConfigParser. Note that although it
effectively behaves very similarly to passing multiple files to
ConfigParser's `read()` method, that requires changing the code at
that point. If that is not feasible, or the INI files should dictate
inheritance themselves, then the iniherit package is a better
alternative.


Project Info
============

* Project Page: https://github.com/cadithealth/iniherit
* Bug Tracking: https://github.com/cadithealth/iniherit/issues


TL;DR
=====

Given the following two files:

.. code-block:: ini

  ## file "base.ini"

  [app:main]
  name = My Application Name

.. code-block:: ini

  ## file "config.ini"

  [DEFAULT]
  # the following will cause both "base.ini" and "override.ini" to be
  # inherited. the "?" indicates that "override.ini" will be ignored
  # if not found; otherwise an error would occur.
  %inherit = base.ini ?override.ini

Then the following code will pass the assert:

.. code-block:: python

  import iniherit
  cfg = iniherit.IniheritSafeConfigParser()
  cfg.read('config.ini')

  assert cfg.get('app:main', 'name') == 'My Application Name'

Alternatively, the global ConfigParser can be altered to
support inheritance:

.. code-block:: python

  import iniherit
  iniherit.mixin.install_globally()

  import ConfigParser
  cfg = ConfigParser.SafeConfigParser()
  cfg.read('config.ini')

  assert cfg.get('app:main', 'name') == 'My Application Name'

Note that the call to `install_globally()` must be invoked **before**
any other module imports ConfigParser for the global override to have
an effect.


Installation
============

Install iniherit via your favorite PyPI package manager works as
follows:

.. code-block:: shell

  $ pip install iniherit


Inheritance Mechanism
=====================

INI file inheritance with the `iniherit` package:

* To add inheritance to an INI file, add an ``%inherit`` option to the
  "DEFAULT" section of the INI file to inherit all sections of the
  specified files. Example:

  .. code-block:: ini

    [DEFAULT]
    %inherit  = base.ini
    def_var   = Overrides the "def_var" setting, if present,
      in the "DEFAULT" section of "base.ini".

    [my-app]
    sect_var  = Overrides the "sect_var" setting, if present,
      in the "my-app" section of "base.ini". Other sections in
      "base.ini" will also be inherited, even if not specified
      here.

* The ``%inherit`` option points to a space-separated, URL-encoded,
  list of files to inherit values from, whose values are loaded
  depth-first, left-to-right. For example:

  .. code-block:: ini

    [DEFAULT]
    %inherit = base.ini file-with%20space.ini

* To inherit only a specific section, add the ``%inherit`` option
  directly to the applicable section. By default, the section by the
  same name will be loaded from the other files, unless the filename
  is suffixed with square-bracket enclosed ("[" ... "]"), URL-encoded,
  section name. Example:

  .. code-block:: ini

    [section]
    %inherit = base.ini override.ini[other%20section]

  In this case, the "section" section in "base.ini" will be inherited,
  followed by the "other section" from "override.ini".

  Note that if the inherited section includes interpolation references
  to the DEFAULT section, these will **NOT** be carried over! In other
  words, inheritance currently ONLY inherits the actual values, not
  the interpreted values. Be warned, as this can lead to surprising
  results!

  If a filename has "[" in the actual name, it can be URL-encoded.

* Filenames, if specified relatively, are taken to be relative to the
  current INI file.

* If a filename is prefixed with "?", then it will be loaded
  optionally: i.e. if the file does not exist, it will be silently
  ignored. If the file does NOT have a "?" prefixed and cannot be
  found, then an ``IOError`` will be raised. Note that this is unlike
  standard ConfigParser.read() behavior, which silently ignores any
  files that cannot be found.

  If a filename has "?" as its first character, it can be URL-encoded.

* Note that the actual name of the inherit option can be changed by
  changing either ``iniherit.parser.DEFAULT_INHERITTAG`` for a global
  effect, or ``ConfigParser.IM_INHERITTAG`` for a per-instance effect.


Gotchas
=======

* Because of how the INI files are loaded and manipulated, the
  IniheritConfigParser's `write` method is disabled. This is because
  the parser cannot know in which inherited file to save any value
  changes. For writing INI files, you should use other ConfigParser
  subclasses, such as `ConfigParser.RawConfigParser`.

.. _ConfigParser: http://docs.python.org/2/library/configparser.html
