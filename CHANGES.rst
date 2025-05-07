.. |Changes|
Version `v0.8.5 <https://github.com/autumnjolitz/instruct/releases/tag/v0.8.5>`_
----------------------------------------------------------------------------------

Released 2025-05-07

`Compare with v0.8.4 <https://github.com/autumnjolitz/instruct/compare/v0.8.4...v0.8.5>`_ (16 commits since)

Bug Fixes

- satisfy both mypy and ruff for ``TypingDefinition`` (`3e9e34a <https://github.com/autumnjolitz/instruct/commit/3e9e34a518829eebbb5a0d6ec63060ad513532a2>`_ by Autumn).
- apply ``pre-commit`` to all files (`2184824 <https://github.com/autumnjolitz/instruct/commit/21848240dd6d52e0159d5633cc2c27d41267363e>`_ by Autumn).
- satisfy mypy (`51e7320 <https://github.com/autumnjolitz/instruct/commit/51e73202c4b328187d7db2fafc0b2da8f7ca7437>`_ by Autumn).
- ValidationError should operate on ``.errors`` as it is ``list[Exception] | tuple[Exception, ...]`` (`6d544df <https://github.com/autumnjolitz/instruct/commit/6d544dfe4765885e0a5a90efc5ec132566d3ed4d>`_ by Autumn).

Version `v0.8.4 <https://github.com/autumnjolitz/instruct/releases/tag/v0.8.4>`_
----------------------------------------------------------------------------------

Released 2024-07-30

`Compare with v0.8.3 <https://github.com/autumnjolitz/instruct/compare/v0.8.3...v0.8.4>`_ (2 commits since)

Bug Fixes

- adjust ``copy_with`` to attempt to use ``__class_getitem__`` as the fallback (`2117a8d <https://github.com/autumnjolitz/instruct/commit/2117a8d0ca154c86ceedff2a546b5942c56b0301>`_ by Autumn).

Version `v0.8.3 <https://github.com/autumnjolitz/instruct/releases/tag/v0.8.3>`_
----------------------------------------------------------------------------------

Released 2024-07-30

`Compare with v0.8.2 <https://github.com/autumnjolitz/instruct/compare/v0.8.2...v0.8.3>`_ (13 commits since)

Bug Fixes

- correct subtype generation for 3.10+ ``types.UnionType``s (`50a7439 <https://github.com/autumnjolitz/instruct/commit/50a74390e57449e32d9c72eef901f0e8982d651d>`_ by Autumn).
- add ``mode`` to benchmarking, refactor slightly (`1e0e821 <https://github.com/autumnjolitz/instruct/commit/1e0e8216ceb88905224c5370dd52a6622aa58eb8>`_ by Autumn).
- ``fast=True`` now supports all event listener forms (`9bf8489 <https://github.com/autumnjolitz/instruct/commit/9bf84898095d3d2241b94801661811d12dc8ca70>`_ by Autumn).
- ``__main__`` now can run benchmark again (`67d59fd <https://github.com/autumnjolitz/instruct/commit/67d59fd50e466be46d9d4bd80cb9a5df0af2d0c3>`_ by Autumn).

Other

- feature: implement simple ``type alias = hint`` (3.12+) (`e9e0ac7 <https://github.com/autumnjolitz/instruct/commit/e9e0ac782ae48d5f07bc3a68edaea97bb81af322>`_ by Autumn).

Version v0.8.2
-------------------

Release 2024-07-23

Bug Fixes

- handle fixed tuples correctly (`f1ab15f <https://github.com/autumnjolitz/instruct/commit/f1ab15fbf3e2d5819b50c5d8280b50d6f83e4329>`_ by Autumn).
- use ``types.CodeType.replace(...)`` when available (`0930b36 <https://github.com/autumnjolitz/instruct/commit/0930b36b8df4d7dd358792fc74361ce21d6bc3ac>`_ by Autumn).

Version v0.8.1
-------------------

Release 2024-07-16

Bug Fixes

- avoid raising an exception inside testing tuple structure for a custom type (`bd4ce81 <https://github.com/autumnjolitz/instruct/commit/bd4ce818902970ca3c86b3ce272062227d92ed3d>`_ by Autumn).

Version v0.8.0
-------------------

Release 2024-07-10

Version v0.8.0a1
-------------------

Release 2024-06-27

Bug Fixes

- exceptions will not list the stack in a json output (`1981a23 <https://github.com/autumnjolitz/instruct/commit/1981a23478b9ec181c39890978562359a62b3d43>`_ by Autumn).
- utils for 3.7 cannot specialize the ``WeakKeyDictionary``, so guard behind TYPE_CHECKING (`4238fa7 <https://github.com/autumnjolitz/instruct/commit/4238fa79caf12da5631fe6ed8c6b225950b1e61d>`_ by Autumn).
- satisfy type checker for non-3.12 (`2ce45fd <https://github.com/autumnjolitz/instruct/commit/2ce45fde5d1f3afc0937327224257394e93a00e4>`_ by Autumn).
- added type hint for exceptions ``__json__`` method (`86c76ff <https://github.com/autumnjolitz/instruct/commit/86c76ff51b97e744cac60e9a91f317a4c8245a6b>`_ by Autumn).
- ignore mypy error from an attribute test (`9a45b6b <https://github.com/autumnjolitz/instruct/commit/9a45b6b823ccd2c773ee1af89f5191f698f39b17>`_ by Autumn).
- tests post refactor (`516c6ba <https://github.com/autumnjolitz/instruct/commit/516c6ba2cd3e06d5ff5faf846523722a98c4eb33>`_ by Autumn).
- add git changelog helper (`3100d65 <https://github.com/autumnjolitz/instruct/commit/3100d653a196dda4748b6dfc068ea8ae3798cf53>`_ by Autumn Jolitz).

Code Refactoring

- add type hints, restructure to be more specific (`5c56e5c <https://github.com/autumnjolitz/instruct/commit/5c56e5c60862658ed9b2b019581cb4510174756b>`_ by Autumn).

Other

- Merge remote-tracking branch 'origin/master' into prerelease/0.8.0a0 (`addca84 <https://github.com/autumnjolitz/instruct/commit/addca849e3856a6be8dfc678822eebd2c7c37066>`_ by Autumn).
- remove: pytype overlay as it is not used (`d88f86e <https://github.com/autumnjolitz/instruct/commit/d88f86e4b506a38156c99c9081df73c54f953ee6>`_ by Autumn).
- change: ``instruct/about.py`` will be structured for tuple comparisions like ``>= (0, 8, 0)`` (`f95b321 <https://github.com/autumnjolitz/instruct/commit/f95b3210efb880a47dfeb8a54cb5094d123a745b>`_ by Autumn).
- [README] try to make more friendly for github (`3d4d145 <https://github.com/autumnjolitz/instruct/commit/3d4d145af6b5c329ca9274eef74875a02b636431>`_ by Autumn Jolitz).


Version v0.8.0a0
-------------------

Release 2024-06-18

Other

- [CURRENT_VERSION] prerelease 0.8.0a0 (`acce414 <https://github.com/autumnjolitz/instruct/commit/acce4143a645329657187f6c3329f84a33bb4f61>`_ by Autumn).
- [*] up version, remove unused imports, add to README (`cd7191d <https://github.com/autumnjolitz/instruct/commit/cd7191dff5b657ec34e175e0dc5d6cd136fa706c>`_ by Autumn).
- [*] refactor ``IAtomic`` -> ``AbstractAtomic``, ``AtomicImpl`` -> ``BaseAtomic`` (`6c8bf41 <https://github.com/autumnjolitz/instruct/commit/6c8bf41a9f2ec0536c105b65668bd24984d858ee>`_ by Autumn).
- [generate_version] fix to pass black (the pre version had a single quote ``'``) (`838fb31 <https://github.com/autumnjolitz/instruct/commit/838fb31d7d342c0ec3f77adc18e73ccf7e36eecb>`_ by Autumn).
- [workflows.build] express the version (`5e5059f <https://github.com/autumnjolitz/instruct/commit/5e5059f7c9f031d0fbc09c14d537555fd7505756>`_ by Autumn).
- [CURRENT_VERSION] bump to 0.8.0 series (`066f08f <https://github.com/autumnjolitz/instruct/commit/066f08f3d727601f85c969ec5bc37444fc5ac047>`_ by Autumn).
- [typing] satisfy mypy for NoDefault (`28c236f <https://github.com/autumnjolitz/instruct/commit/28c236f951f4dfc30e91a79f73c97eace4dd7c14>`_ by Autumn).
- [*] use ``getattr_static`` more aggressively (`7b095d0 <https://github.com/autumnjolitz/instruct/commit/7b095d0d95f4fea3d0a81eabbf392a33bb7d63c2>`_ by Autumn).
- [constants] add ``Undefined`` (`7dccf96 <https://github.com/autumnjolitz/instruct/commit/7dccf9670e1e735650b4f379c536c802e7921fcf>`_ by Autumn).
- [*] pass 3.12 tests (`5962696 <https://github.com/autumnjolitz/instruct/commit/5962696d4fa0a845c2b432940cbb89d6642ee1ee>`_ by Autumn).
- [typing] check for NoDefault (`2146a2e <https://github.com/autumnjolitz/instruct/commit/2146a2e0c19d532b88cc2157773664d0464434b8>`_ by Autumn).
- [*] silence mypy with an ignore (`4d5b894 <https://github.com/autumnjolitz/instruct/commit/4d5b8941faf95eed45283bfcf9f7cec02c710acd>`_ by Autumn).
- [dev-requirements] fix version (`65fd3fe <https://github.com/autumnjolitz/instruct/commit/65fd3fe0d7a837346481b3eebb8b29a1b4cac179>`_ by Autumn).
- [*] default initialize untyped generics to ``Any`` (`c601ad5 <https://github.com/autumnjolitz/instruct/commit/c601ad5d0aa1ba30e8a231839d9eafb3d28a2c16>`_ by Autumn).
- [*] pass mypy (`426e1ee <https://github.com/autumnjolitz/instruct/commit/426e1eea2a2af67852bb6c97ada693741b5c5a76>`_ by Autumn).
- [*] all backport (`5b8385e <https://github.com/autumnjolitz/instruct/commit/5b8385e25030c69053e5838e9ffb1f2438930d24>`_ by Autumn).
- [*] backport some more (`c7deaa4 <https://github.com/autumnjolitz/instruct/commit/c7deaa40102ee0e84c15a5bdfdfb131de9eda26d>`_ by Autumn).
- [*] copy from bugfix/master/relax-restrictions (`12842fd <https://github.com/autumnjolitz/instruct/commit/12842fd0e94b597bc31a64d0361cbeaebd794be1>`_ by Autumn).
- [*] rename ``Atomic`` -> ``AtomicMeta`` (`c46caec <https://github.com/autumnjolitz/instruct/commit/c46caecf27904f16cd004618b2bb882e71cb0922>`_ by Autumn).
- [*] support generics (`4955f18 <https://github.com/autumnjolitz/instruct/commit/4955f18d04258bbd3c27562022708281cc98e645>`_ by Autumn).



Version v0.7.5post2
-------------------

Release 2024-02-29

Other

- [typedef] fix typo (`1c33b63 <https://github.com/autumnjolitz/instruct/commit/1c33b637bd58b4d5329013881babf6709b9d9f1c>`_ by Autumn).


Version v0.7.5.post1
-------------------

Release 2024-02-29

Other

- [typedef] fix for 3.7 (`46552e0 <https://github.com/autumnjolitz/instruct/commit/46552e0ed57beda354f856c8de174ddca8b1c36a>`_ by Autumn).


Version v0.7.5
-------------------

Release 2024-02-29

Other

- [CURRENT_VERSION] bump (`1f68ad0 <https://github.com/autumnjolitz/instruct/commit/1f68ad0d73e8acd7f57e1ee8a48ccb4c67462ae5>`_ by Autumn).
- [typedef] support ``type | type`` in 3.10+ and ``__init_subclass__`` (`78c1a85 <https://github.com/autumnjolitz/instruct/commit/78c1a85bb316bb1cffc87d83cc4d86533682e121>`_ by Autumn).
- [README] try to make more friendly for github (`f069f7e <https://github.com/autumnjolitz/instruct/commit/f069f7e77ebee4e392983b540ae362cd8b2ba119>`_ by Autumn Jolitz).
- [CHANGES, README] update (`383b7fe <https://github.com/autumnjolitz/instruct/commit/383b7feee9e70a2f05431bda4faca14ad4ab0b67>`_ by Autumn Jolitz).
- [CHANGES.rst] template it (`292680e <https://github.com/autumnjolitz/instruct/commit/292680e87d57d067ef9ba1516f9f6514eb237d47>`_ by Autumn Jolitz).
- [CHANGES] investigate use of git-changelog (`4d3470a <https://github.com/autumnjolitz/instruct/commit/4d3470a3ee7da6acc6942ba17f21fca9a5374a30>`_ by Autumn Jolitz).


Version v0.7.4
-------------------

Release 2023-12-10

- [.github] mess with development one (`725005e <https://github.com/autumnjolitz/instruct/commit/725005ec0363e83857d1e308937e95e29cbe4d18>`_ by Autumn Jolitz).
- [*] refactor build, add invoke interface as my makefile (`fd8e724 <https://github.com/autumnjolitz/instruct/commit/fd8e7245cddb2aa8c6f93f27a515a2c0ca5f0649>`_ by Autumn Jolitz).
- [README] add badges (`b30a7bc <https://github.com/autumnjolitz/instruct/commit/b30a7bcd7344393a7c7fd94a383f30d5a85b4a6e>`_ by Autumn).
- [release] test before upload (`4431408 <https://github.com/autumnjolitz/instruct/commit/44314086aeb1be094a2bdd2ef7fff7f645abaede>`_ by Autumn).
- [0.7.3.post1] bump version for pypi (`ade6cd8 <https://github.com/autumnjolitz/instruct/commit/ade6cd882d2771f4abe9927e78614886f7f01ad6>`_ by Autumn).
- [*] Port instruct to newer Python versions (#3) (`19c30b2 <https://github.com/autumnjolitz/instruct/commit/19c30b278c23cc63fadbbaeadc30409c15bce098>`_ by Autumn Jolitz).


Version v0.7.3
-------------------

Release 2023-07-18

- add notes on use of ``Range`` and friends
- Export ``RangeFlags`` from ``__init__``
- Unlock ``typing-extensions`` range


Version v0.7.2
-------------------

Release 2022-05-13

- Add dummy ``__iter__`` to ``SimpleBase`` which addresses principal of least astonishment for an empty class


Version v0.7.1
-------------------

Release 2022-05-13

- Add ``devel`` to setup extras
- export ``clear``, ``reset_to_defaults``
- make ``_set_defaults`` first call the zero-init version, then cascade through the inheritance tree for any overrides
- add default functions for empty classes, use ``__public_class__`` for ``public_class`` calls
- Remove ``fast_new`` in favor of using ``_set_defaults``
- Allow ``__public_class__`` to be overridden in rare cases


Version v0.7.0
-------------------

Release 2022-05-12

- Add change log
- Correct README example (it works!)
- Correct bug where ``_asdict``, ``_astuple``, ``_aslist`` were not added to an empty class
- Allow use of ``Annotation[type, ...others...]`` in type definitions
- Support use of ``Range`` in a type ``Annotation`` to restrict the range of values allowed for a type
- Support use of ``NoPickle``, ``NoJSON``, ``NoIterable`` to skip fields from pickling, JSON dumping and ``__iter__`` respectively
- ``_asdict``/``_astuple``/``_aslist`` will still return **ALL** values within an instruct-class.
- The field ``_annotated_metadata`` on a class contains a mapping of ``field_name -> (...others...)``
- Correct a bug where ``Literal[Enum.Value]`` would erroneously allow a matching non-Enum value if the ``__eq__`` on the Enum was overridden to allow it
- We now check via ``is`` and on ``__eq__`` checks we check the type as well to reject the wrong types
- Upgrade to Jinja2 for the 3.x series!
- Upgrade typing-extensions to 4.2.0
- Mark support as Python 3.7+
