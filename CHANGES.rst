.. |Changes|

Version 0.7.4
-------------------

Release 2023-12-10

- [.github] mess with development one (`725005e <https://github.com/autumnjolitz/instruct/commit/725005ec0363e83857d1e308937e95e29cbe4d18>`_ by Autumn Jolitz).
- [*] refactor build, add invoke interface as my makefile (`fd8e724 <https://github.com/autumnjolitz/instruct/commit/fd8e7245cddb2aa8c6f93f27a515a2c0ca5f0649>`_ by Autumn Jolitz).
- [README] add badges (`b30a7bc <https://github.com/autumnjolitz/instruct/commit/b30a7bcd7344393a7c7fd94a383f30d5a85b4a6e>`_ by Autumn).
- [release] test before upload (`4431408 <https://github.com/autumnjolitz/instruct/commit/44314086aeb1be094a2bdd2ef7fff7f645abaede>`_ by Autumn).
- [0.7.3.post1] bump version for pypi (`ade6cd8 <https://github.com/autumnjolitz/instruct/commit/ade6cd882d2771f4abe9927e78614886f7f01ad6>`_ by Autumn).
- [*] Port instruct to newer Python versions (#3) (`19c30b2 <https://github.com/autumnjolitz/instruct/commit/19c30b278c23cc63fadbbaeadc30409c15bce098>`_ by Autumn Jolitz).


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
