=========
ChangeLog
=========


v0.3.9
======

* Added support for SafeConfigParser in global_install
* Added support for recursive evaluation of "%(ENV:...)s" expansions


v0.3.8
======

* Fixed interpolated "%inherit" values for Python pre-2.7.12


v0.3.7
======

* Added interpolation support for "%inherit" targets, e.g.::

    %inherit = %(target)s.ini %(ENV:OTHER_TARGET)s.ini
    target   = some-value


v0.3.6
======

* Added compatibility Python 3 of SUPER/ENV support
* Fixed issue #6


v0.3.5
======

* Added support for ``%(SUPER)s`` inherited value expansion
* Added support for ``%(ENV:VARNAME)s`` environment variable value
  expansion


v0.3.4
======

* Removed `distribute` dependency


v0.3.3
======

* Preserved order of sections during application of inherited sections


v0.3.2
======

* Corrected egg packaging to include .txt and .rst files
* Corrected `distribute` dependency for py2 vs. py3


v0.2.0
======

* Fixed issue #2
* Added python 3 compatibility
* First tagged release
