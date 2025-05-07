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

- avoid raising an exception inside testing tuple structure for a custom type (`0a3108c <https://github.com/autumnjolitz/instruct/commit/0a3108c8969e87f5294608d081341bfc2ada0c50>`_ by Autumn).

Docs

- update (`8f9ea11 <https://github.com/autumnjolitz/instruct/commit/8f9ea113905356c6a11dc71b9c1a2770d96a7d3f>`_ by Autumn).
- remove contradictory statement (`e4ed0b4 <https://github.com/autumnjolitz/instruct/commit/e4ed0b40a82be3e24cc0362a5e76832057344204>`_ by Autumn).

Build

- correct changelog link (`bef4aeb <https://github.com/autumnjolitz/instruct/commit/bef4aebd37678963a511227fcb0c8cdb0a074406>`_ by Autumn).
- adjust tasks to allow for releasing on a version other than the ``CURRENT_VERSION.txt`` next default (`fc42c02 <https://github.com/autumnjolitz/instruct/commit/fc42c02de0dbba61bb1e89b61babcd2d1f0429e6>`_ by Autumn).
- bump version to 0.8.1 (`8a4c2ef <https://github.com/autumnjolitz/instruct/commit/8a4c2ef7b4122edab3a92123fd7846bca2571cb8>`_ by Autumn).

Version v0.8.0
-------------------

Release 2025-07-07

Features

- ``instruct/about.py`` will be structured for tuple comparisions like ``>= (0, 8, 0)`` (`b9714f8 <https://github.com/autumnjolitz/instruct/commit/b9714f859a4639f57cf13fd250567b9f8688ecf7>`_ by Autumn).
- add ``Undefined`` (`41980a0 <https://github.com/autumnjolitz/instruct/commit/41980a094fbd28245c7ac300ad26c0436e577338>`_ by Autumn).
- implement generics! (`0e716bf <https://github.com/autumnjolitz/instruct/commit/0e716bf8cd49d9b231e1f38fb7ec1278cce4724b>`_ by Autumn).

Performance Improvements

- use ``inspect.getattr_static`` more aggressively (`c16a0ea <https://github.com/autumnjolitz/instruct/commit/c16a0eab801857caf389d612c2e34153d53ca4e9>`_ by Autumn).

Bug Fixes

- do not list the stack in a json output (`2694716 <https://github.com/autumnjolitz/instruct/commit/2694716a525194d1ea888460502a27ac591b02cc>`_ by Autumn).
- Python 3.7 cannot specialize the ``WeakKeyDictionary``, so guard behind TYPE_CHECKING (`1bc76ff <https://github.com/autumnjolitz/instruct/commit/1bc76ff132e617ca4f5987ffcbe2852533452a33>`_ by Autumn).
- satisfy type checker for Python 3.11 and below (`c478dd1 <https://github.com/autumnjolitz/instruct/commit/c478dd1e167cfb19b7bbf51261cc97c13f6bbee4>`_ by Autumn).
- added type hint to ``__json__`` method (`a6da934 <https://github.com/autumnjolitz/instruct/commit/a6da9344f6aa7b5b04e7121c928d75566d436ba5>`_ by Autumn).
- ignore mypy error from an attribute test (`1230465 <https://github.com/autumnjolitz/instruct/commit/12304654b43b685bf9ca38b4004c6bcac950706b>`_ by Autumn).
- add git changelog helper (`b79c727 <https://github.com/autumnjolitz/instruct/commit/b79c727291e2535296dc4c1b8c5d9fa56dc3ac79>`_ by Autumn Jolitz).
- satisfy mypy for ``NoDefault`` type (`297f268 <https://github.com/autumnjolitz/instruct/commit/297f268d2f80212dcc9c3f593d95d8d40979e051>`_ by Autumn).
- correct Python 3.12 to pass tests (`f9e5296 <https://github.com/autumnjolitz/instruct/commit/f9e529611d4e32300b5932fcc5cc69e2640570c3>`_ by Autumn).
- check for ``NoDefault`` (`94c5f07 <https://github.com/autumnjolitz/instruct/commit/94c5f078e7dfc2fcb78652b9b17be81a2180fff0>`_ by Autumn).
- default initialize untyped generics to ``Any`` (`e0e781f <https://github.com/autumnjolitz/instruct/commit/e0e781ff1a3576e5df6804a78a47a6310bc06a08>`_ by Autumn).
- update backport for Python 3.7 (`fffa961 <https://github.com/autumnjolitz/instruct/commit/fffa961f83d6e03bd77fad3b36728852bf9463b0>`_ by Autumn).

Code Refactoring

- split into language, compat, add type hints, restructure to be more specific (`9845934 <https://github.com/autumnjolitz/instruct/commit/98459347c2bd025eab032e2b0eab9d8e04bdd4bc>`_ by Autumn).
- rename ``IAtomic`` to ``AbstractAtomic``, ``AtomicImpl`` to ``BaseAtomic`` (`7d2fb28 <https://github.com/autumnjolitz/instruct/commit/7d2fb284ee357c4d7a435f1f7706ab847733eed3>`_ by Autumn).
- rename ``Atomic`` to ``AtomicMeta`` (`644fecb <https://github.com/autumnjolitz/instruct/commit/644fecba437cee23dbe039693a80921108d1016c>`_ by Autumn).

Docs

- update (`1080c7c <https://github.com/autumnjolitz/instruct/commit/1080c7c550a63f9b7404f54f399029a55bfa5ae0>`_ by Autumn).
- clean up (`0184422 <https://github.com/autumnjolitz/instruct/commit/01844228dda2e623e0b70376410a1cf04dca48c5>`_ by Autumn).
- add newline for change list (`345cb2d <https://github.com/autumnjolitz/instruct/commit/345cb2d0646acaac9b2debd793e90d777a150e67>`_ by Autumn).
- ``git-changelog`` requires a "v" prefix to match v prefixed tags (`8b8b6cf <https://github.com/autumnjolitz/instruct/commit/8b8b6cfe8cc63372d035230bd97c5aea53a9e935>`_ by Autumn).
- try to make more friendly for github (`a530071 <https://github.com/autumnjolitz/instruct/commit/a530071c76ee269258c3b1597d9d14fc76cb3a14>`_ by Autumn Jolitz).

Dependencies

- pin ``black`` for python 3.8 (`6a500d6 <https://github.com/autumnjolitz/instruct/commit/6a500d691d645ae20f35a82aff646aec5869589a>`_ by Autumn).

Tests

- update (`eeb311f <https://github.com/autumnjolitz/instruct/commit/eeb311f44338ae99c2981a9c5d81430b1c76c6d1>`_ by Autumn). Caused By: `91f05963ea1c25f36d551834f7ae672d05955074 <https://github.com/autumnjolitz/instruct/commit/91f05963ea1c25f36d551834f7ae672d05955074>_`

Style

- run black (`88faff7 <https://github.com/autumnjolitz/instruct/commit/88faff735a5d60c87769780c9a87ebcdbfd3a03f>`_ by Autumn).

Chore

- ignore ``python**`` folders (used in cross version testing) (`de0a37c <https://github.com/autumnjolitz/instruct/commit/de0a37cc12db86da43fed8aad4f5cea833f1a9a7>`_ by Autumn).
- drop pytype overlay (`6b0a8f8 <https://github.com/autumnjolitz/instruct/commit/6b0a8f844e988420a5f04b69c70a110bb1e06b7f>`_ by Autumn).
- up version to 0.8.0, remove unused imports, add to README that Generics are supported (`4b0902a <https://github.com/autumnjolitz/instruct/commit/4b0902aa168f8e385232afe89d9fcfa266398e76>`_ by Autumn).
- silence mypy on ``Genericizable`` with an ignore (`5cfb45f <https://github.com/autumnjolitz/instruct/commit/5cfb45f5bf376475437589c2ebd2c529c6e74c1d>`_ by Autumn).
- pass mypy type checks (`506a810 <https://github.com/autumnjolitz/instruct/commit/506a8103ba1d8e33f2a1685a480ee00deca611af>`_ by Autumn).

Continuous Integration

- finalize, skip existing obj on pypi (`8df60b3 <https://github.com/autumnjolitz/instruct/commit/8df60b34c52eab79339ae2a1464fc0c380c69326>`_ by Autumn).
- disable word wrapping in pandoc (`c9479ee <https://github.com/autumnjolitz/instruct/commit/c9479ee5cced77be02aee4db6d39325ba58a6caa>`_ by Autumn).
- allow pypi publishing, add sha sums to the release notes (`5b49f13 <https://github.com/autumnjolitz/instruct/commit/5b49f1362e4c89c1e9463c56ef950384e08f9812>`_ by Autumn).
- add release functionality (handles versioning, etc) (`29d376b <https://github.com/autumnjolitz/instruct/commit/29d376b0d6944a648fd64a7f89b8443e75a164a6>`_ by Autumn).
- simplify, write version specific changes to the release, temporarily disable pypi (`e32a1a9 <https://github.com/autumnjolitz/instruct/commit/e32a1a9619d1fd820665cb7ffaf0309e3116cb3e>`_ by Autumn).
- use ``invoke build`` (`552203b <https://github.com/autumnjolitz/instruct/commit/552203b3019cf70f7acd7d1fdbd7c4eb1f14ebf9>`_ by Autumn).
- use the newer python setup step (`4d42fa4 <https://github.com/autumnjolitz/instruct/commit/4d42fa48630582ea364e58d5fbfb5328f5fd1559>`_ by Autumn).
- get all history for a change log generator (`15e9103 <https://github.com/autumnjolitz/instruct/commit/15e910335b692198f036cdafbbcd46b10a4fd8f6>`_ by Autumn).
- run the changes test before any tests run (`9b741ce <https://github.com/autumnjolitz/instruct/commit/9b741cedcd557f6b444390b7ae658a09e065d8ed>`_ by Autumn).
- ensure ``CHANGES.rst`` is always up-to-date (`d9bc2ce <https://github.com/autumnjolitz/instruct/commit/d9bc2ce513e116d05ee6fce237b47d0320e19d53>`_ by Autumn).
- print out black version (`42ba597 <https://github.com/autumnjolitz/instruct/commit/42ba5972c9e0faf8e0a681ff98a2e0fdf2d33c37>`_ by Autumn).
- relax restrictions on build (`6157a1c <https://github.com/autumnjolitz/instruct/commit/6157a1cc466a0279f93604e8895b97448236f3f5>`_ by Autumn).

Build

- bump version to 0.8.0 (`f5b0765 <https://github.com/autumnjolitz/instruct/commit/f5b0765770fe1d7c8913778e28b543595bb654c9>`_ by Autumn).
- assume `pawamoy/git-changelog@89 <https://github.com/pawamoy/git-changelog/pull/89>`_ will be merged in a few days (`7e23986 <https://github.com/autumnjolitz/instruct/commit/7e2398685a907c000c657d3bad0c81fe916bf07b>`_ by Autumn).
- remove invalid classifier (despite the fact this is used as a framework) (`3174afc <https://github.com/autumnjolitz/instruct/commit/3174afc934c41e0629489b27c5b67c088e53206f>`_ by Autumn).
- add ``checksum`` command (`83f3973 <https://github.com/autumnjolitz/instruct/commit/83f3973a63d07a2f48afe1d100a01f8e0f59c1fd>`_ by Autumn).
- overhaul setup.cfg classifiers et al, given that instruct has been production ready for years now (`0639313 <https://github.com/autumnjolitz/instruct/commit/0639313c3199c18a165c2fe73026918d5cda228e>`_ by Autumn).
- ignore python3.whatever directories, remove some default changelog options for use in tasks.py (`b47a942 <https://github.com/autumnjolitz/instruct/commit/b47a9426fadc5afe0ce2a1f10739735927c7b394>`_ by Autumn).
- run black (`cb40105 <https://github.com/autumnjolitz/instruct/commit/cb4010513b8b254f7ff4a9ccaec1ded4ba085a3e>`_ by Autumn).
- changelog can now omit in-flight/unreleased changes (`ac15505 <https://github.com/autumnjolitz/instruct/commit/ac15505ecbb460b7f1e06d06b87d526c5360cf02>`_ by Autumn).
- bump version to next alpha (`00dd465 <https://github.com/autumnjolitz/instruct/commit/00dd4659a1f65baa448b049b71bab3ef828208f5>`_ by Autumn).
- pre-commit should use repo's pyproject (`33e1369 <https://github.com/autumnjolitz/instruct/commit/33e13692233cb1b28417a80db76389254e0a73fe>`_ by Autumn).
- delete unused black config (`f6567ac <https://github.com/autumnjolitz/instruct/commit/f6567ac1b9c5fa11b74fba743141c8cf4a917a4a>`_ by Autumn).
- add files back for the naive ``python -m build`` case to work (`cf96480 <https://github.com/autumnjolitz/instruct/commit/cf96480b6d4334e3078b7f325898c6250ce682bc>`_ by Autumn).
- setup-metadata can now dump info from a ``wheel`` or ``sdist`` (`9c19cf4 <https://github.com/autumnjolitz/instruct/commit/9c19cf47d81467c3a5adcbcfaaaba4368da589e0>`_ by Autumn).
- ensure source distributions do not depend on source control, remove unused functions (`a7f6de0 <https://github.com/autumnjolitz/instruct/commit/a7f6de03e217d876b44f869a91d5b4ef58d9b095>`_ by Autumn). Referenced By: `Source Distributions <https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/#source-distributions>`_
- ensure task_support injects ``pprint`` (`a3abf25 <https://github.com/autumnjolitz/instruct/commit/a3abf2527cbbfc226212410bdb2e1145eaaf4558>`_ by Autumn).
- remove unused files (`cee5f21 <https://github.com/autumnjolitz/instruct/commit/cee5f214ae131209423538ac3bea1ebbff10ecde>`_ by Autumn).
- ensure ``about.VersionInfo`` has a compliant pep440 ``.public_...`` and ``__str__()`` functions (`f6bedea <https://github.com/autumnjolitz/instruct/commit/f6bedea81832ae9dc40745392ff00aca8f4ab6ad>`_ by Autumn).
- fix ``CHANGES.rst``, use fork of ``git-changelog`` until `pawamoy/git-changelog@89 <https://github.com/pawamoy/git-changelog/pull/89>`_ is merged and released, use pep440 versioning (`771790b <https://github.com/autumnjolitz/instruct/commit/771790b575ca43dbb9f5449b21706a87897e1c12>`_ by Autumn).
- fix type hint complaints, add helpers (`ad00166 <https://github.com/autumnjolitz/instruct/commit/ad00166f09c9151811ee58987c30eb531ea2e158>`_ by Autumn).
- add defaults for ``git-changelog``, require 2.4.0 as 2.4.1+ will ignore untyped commits (`39025c3 <https://github.com/autumnjolitz/instruct/commit/39025c31542ae459fa24c5f8dfa5c0e91138edda>`_ by Autumn).
- prerelease v0.8.0a0 (`ef84469 <https://github.com/autumnjolitz/instruct/commit/ef84469be82d7813492f701d9650ca1e414c11fd>`_ by Autumn).
- bump to v0.8.0 series (`f0ad5ae <https://github.com/autumnjolitz/instruct/commit/f0ad5aed353bfd62d9a40bec65fb306aa96ff618>`_ by Autumn).

Version v0.7.5.post2
-------------------

Release 2025-07-08

Bug Fixes

- correct for Python 3.7 (`e58c523 <https://github.com/autumnjolitz/instruct/commit/e58c523ce4edbca560267b6a6a0c1fd8919c485c>`_ by Autumn).

Version v0.7.5
-------------------

Release 2025-07-08

Features

- support ``type | type`` in Python 3.10 and above, implement ``__init_subclass__(cls)`` (`88164e3 <https://github.com/autumnjolitz/instruct/commit/88164e390267b6ee690d88bed6e60e17bd4da98b>`_ by Autumn).

Docs

- try to make more friendly for github (`46df415 <https://github.com/autumnjolitz/instruct/commit/46df4150a4928659b4464ef9282da033c8cabea2>`_ by Autumn Jolitz).
- update ``CHANGES.rst``, ``README.rst`` (`42bd3d2 <https://github.com/autumnjolitz/instruct/commit/42bd3d23f11362d3584896fb8b31a4aa83103bf2>`_ by Autumn Jolitz).
- template-ize for release note generation (`5e508b7 <https://github.com/autumnjolitz/instruct/commit/5e508b714bb47cd2d904a75e4534d7ffab912867>`_ by Autumn Jolitz).
- test of `git-changelog <https://github.com/pawamoy/git-changelog>`_ (`a4aeb37 <https://github.com/autumnjolitz/instruct/commit/a4aeb375e0ee83fdbbb332d8d5573fadf91d8917>`_ by Autumn Jolitz).

Continuous Integration

- add PyPy in testing (`fd12152 <https://github.com/autumnjolitz/instruct/commit/fd12152ab66246e18e4cdcd2876065814f1f8da5>`_ by Autumn Jolitz).

Build

- bump version to v0.7.5 (`9924da8 <https://github.com/autumnjolitz/instruct/commit/9924da815d892a9c4b3127f337c7cd965148d033>`_ by Autumn).


Version v0.7.4
-------------------

Release 2023-12-10

Build

- refactor, use `invoke <https://www.pyinvoke.org/>`_

Chore

- add badges to ``README.rst``, adjust github CI workflow names

Continuous Integration

- add test

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
