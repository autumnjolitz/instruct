|Changes|
Unreleased Version
-------------------

Release YYYY-MM-DD

- attempting to improve build infrastructure through investigation of `pawamoy/git-changelog<https://github.com/pawamoy/git-changelog>`_

|Changes|

Version 0.7.4
-----------------

Release 2023-12-09

- Supported more Python versions and implementations:
    - Tier 1 support: CPython 3.8, 3.9, 3.10, 3.11, 3.12
    - Tier 2 support: PyPy 3.7, 3.8, 3.9
    - Tier 3 support: PyPy 3.10
- Switched to a tag based release model
- Add infrastructure for running tests

Version 0.7.3
-----------------

Release 2023-07-18

- add notes on use of ``Range`` and friends
- Export ``RangeFlags`` from ``__init__``
- Unlock ``typing-extensions`` range

Version 0.7.2
-----------------

Release 2022-05-13

- Add dummy ``__iter__`` to ``SimpleBase`` which addresses principal of least astonishment for an empty class

Version 0.7.1
-----------------

Release 2022-05-13

- Add ``devel`` to setup extras
- export ``clear``, ``reset_to_defaults``
- make ``_set_defaults`` first call the zero-init version, then cascade through the inheritance tree for any overrides
- add default functions for empty classes, use ``__public_class__`` for ``public_class`` calls
- Remove ``fast_new`` in favor of using ``_set_defaults``
- Allow ``__public_class__`` to be overridden in rare cases


Version 0.7.0
-----------------

Release 2022-05-12

- Add change log
- Correct README example (it works!)
- Correct bug where ``_asdict``, ``_astuple``, ``_aslist`` were not added to an empty class
- Allow use of ``Annotation[type, ...others...]`` in type definitions
    + Support use of ``Range`` in a type ``Annotation`` to restrict the range of values allowed for a type
    + Support use of ``NoPickle``, ``NoJSON``, ``NoIterable`` to skip fields from pickling, JSON dumping and ``__iter__`` respectively
        - ``_asdict``/``_astuple``/``_aslist`` will still return **ALL** values within an instruct-class.
    + The field ``_annotated_metadata`` on a class contains a mapping of ``field_name -> (...others...)``
- Correct a bug where ``Literal[Enum.Value]`` would erroneously allow a matching non-Enum value if the ``__eq__`` on the Enum was overridden to allow it
    + We now check via ``is`` and on ``__eq__`` checks we check the type as well to reject the wrong types
- Upgrade to Jinja2 for the 3.x series!
- Upgrade typing-extensions to 4.2.0
- Mark support as Python 3.7+
