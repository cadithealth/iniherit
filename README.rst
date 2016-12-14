====================
INI File Inheritance
====================

Adds INI-file inheritance to ConfigParser. Note that although it
effectively behaves very similarly to passing multiple files to
ConfigParser's `read()` method, that requires changing the code at
that point. If that is not feasible, or the INI files should dictate
inheritance themselves, then the `iniherit` package is a better
alternative.

Oh, `iniherit` also adds support for environment variable expansion
via ``%(ENV:VARNAME)s``. This really shouldn't be here, but since
`iniherit` supports the ``%(SUPER)s`` expansion, it was "just too
easy" to add envvar expansion as well...


Project Info
============

* Project Page: https://github.com/cadithealth/iniherit
* Bug Tracking: https://github.com/cadithealth/iniherit/issues


TL;DR
=====

Given the following two files, ``base.ini``:

.. code:: ini

  [app:main]
  name = My Application Name

and ``config.ini``:

.. code:: ini

  [DEFAULT]
  # the following will cause both "base.ini" and "override.ini" to be
  # inherited. the "?" indicates that "override.ini" will be ignored
  # if not found; otherwise an error would occur.
  %inherit = base.ini ?override.ini

Then the following code will pass the assert:

.. code:: python

  import iniherit
  cfg = iniherit.SafeConfigParser()
  cfg.read('config.ini')

  assert cfg.get('app:main', 'name') == 'My Application Name'

Alternatively, the global ConfigParser can be altered to
support inheritance:

.. code:: python

  import iniherit
  iniherit.mixin.install_globally()

  import ConfigParser
  cfg = ConfigParser.SafeConfigParser()
  cfg.read('config.ini')

  assert cfg.get('app:main', 'name') == 'My Application Name'

Note that the call to `install_globally()` must be invoked **before**
any other module imports ConfigParser for the global override to have
an effect.

The command-line program `iniherit` allows flattening of INI files
(i.e. collapsing all inheritance rules), optionally in "watch" mode:

.. code:: bash

  $ iniherit --watch --interval 2 --verbose input.ini output.ini
  INFO:iniherit.cli:"source.ini" changed; updating output...
  INFO:iniherit.cli:"inherited-file.ini" changed; updating output...
  ^C


Installation
============

Install iniherit via your favorite PyPI package manager works as
follows:

.. code:: bash

  # if using python 3+, upgrade your `distribute` package *first*
  $ pip install "distribute>=0.7.3"

  # then istall with pip:
  $ pip install iniherit


Inheritance Mechanism
=====================

INI file inheritance with the `iniherit` package:

* To add inheritance to an INI file, add an ``%inherit`` option to the
  "DEFAULT" section of the INI file to inherit all sections of the
  specified files. Example:

  .. code:: ini

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

  .. code:: ini

    [DEFAULT]
    %inherit = base.ini file-with%20space.ini

* To inherit only a specific section, add the ``%inherit`` option
  directly to the applicable section. By default, the section by the
  same name will be loaded from the other files, unless the filename
  is suffixed with square-bracket enclosed ("[" ... "]"), URL-encoded,
  section name. Example:

  .. code:: ini

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


Substitutions
=============

The `iniherit` package adds the following additional substitution
options:

* ``%(SUPER[:-DEFAULT])s``

  Evaluates to the inherited value of the current section/key value.
  If the inherited INI does not specify a value and no default is
  provided, then an `InterpolationMissingSuperError` is raised. The
  "inherited value" is evaluated depth-first. Note that "SUPER" must
  be all upper case.

  For example, given the following INI files:

  .. code:: ini

    # base.ini
    [loggers]
    keys = root, app


  .. code:: ini

    # config.ini
    [DEFAULT]
    %inherit = base.ini
    [loggers]
    keys = %(SUPER)s, auth
    wdef = %(SUPER:-more)s or less
    nada = %(SUPER)s boom!


  Then the following Python will result:

  .. code:: python

    import iniherit
    iniherit.mixin.install_globally()
    import ConfigParser
    cfg = ConfigParser.SafeConfigParser()
    cfg.read('config.ini')

    cfg.get('loggers', 'keys')  # ==> 'root, app, auth'
    cfg.get('loggers', 'wdef')  # ==> 'more or less'
    cfg.get('loggers', 'nada')  # ==> raises InterpolationMissingSuperError


  As with standard interpolation errors, the
  InterpolationMissingSuperError exception is only raised if/when the
  value is requested from the config (with `raw` set to falsy).


* ``%(ENV:VARNAME[:-DEFAULT])s``

  Evaluates to the value of the environment variable name "VARNAME".
  If the environment variable is not defined and no default is
  provided, then an `InterpolationMissingEnvError` is raised. Note
  that environment variable names are always case sensitive.

  For example, given the following INI file:

  .. code:: ini

    # config.ini
    [section]
    home = %(ENV:HOME)s
    rdir = %(ENV:RDIR:-/var/run)s
    nada = %(ENV:RDIR)s


  Then the following Python will result:

  .. code:: python

    import iniherit
    iniherit.mixin.install_globally()
    import ConfigParser
    cfg = ConfigParser.SafeConfigParser()
    cfg.read('config.ini')

    import os
    os.environ['home'] = '/home/user'  # ensure "HOME" envvar exists
    os.environ.pop('RDIR', None)       # ensure "RDIR" envvar does NOT exist

    cfg.get('section', 'home')  # ==> '/home/user'
    cfg.get('section', 'rdir')  # ==> '/var/run'
    cfg.get('section', 'nada')  # ==> raises InterpolationMissingEnvError


  As with standard interpolation errors, the
  InterpolationMissingEnvError exception is only raised if/when the
  value is requested from the config (with `raw` set to falsy).


Gotchas
=======

* After an inherit-enabled INI file is loaded, the ConfigParser no
  longer has knowledge of where a particular option was loaded from or
  how it was derived. For this reason, when the `write` method is
  called, the ConfigParser generates an INI file without inheritance.
  In other words, it flattens the inheritance tree.

.. _ConfigParser: http://docs.python.org/2/library/configparser.html
