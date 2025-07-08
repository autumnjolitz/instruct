.. |Changes|

Version `v0.8.6 <https://github.com/autumnjolitz/instruct/releases/tag/v0.8.6>`_
----------------------------------------------------------------------------------

Released 2025-07-08

`Compare with v0.8.5 <https://github.com/autumnjolitz/instruct/compare/v0.8.5...v0.8.6>`_ (9 commits since)

Features

- implement ``AutoRepr`` (aka ``autorepr=True``) (`d58c423 <https://github.com/autumnjolitz/instruct/commit/d58c423ddc06ef80cdb349f51b4005245efbc9f8>`_ by Autumn).

Bug Fixes

- only call ``.as_json()`` when encountering ``Exception`` (if the stack is expanded from item that has ``.errors``, it will already have JSONable items) (`3e75170 <https://github.com/autumnjolitz/instruct/commit/3e7517024c39fce016b30cea2ff3fd077a26452d>`_ by Autumn).
- avoid exposing ``NoIterable`` fields via ``keys()``, ``items()`` (`dc6a6d8 <https://github.com/autumnjolitz/instruct/commit/dc6a6d8f28b67e54904867d0cd4946d9eb41f798>`_ by Autumn).
- correct syntax error when no effective fields (may occur if all fields are ``Annotated[..., NoIterable]``) (`2b47a16 <https://github.com/autumnjolitz/instruct/commit/2b47a16985637ed34f62afdcd68d1da29dde404d>`_ by Autumn).

Docs

- update (`7f4e53c <https://github.com/autumnjolitz/instruct/commit/7f4e53c9f8662c0fa974057b95b48a89cf105bc2>`_ by Autumn).

Tests

- verify ``NoPickle`` (`886fedd <https://github.com/autumnjolitz/instruct/commit/886fedd0a0b33f0ab1233c79e91b7f13e0d5b4ce>`_ by Autumn).

Chore

- correct type hint errors (`e554179 <https://github.com/autumnjolitz/instruct/commit/e554179422e98772dbc99ee03665e0ec11c28b0a>`_ by Autumn).

Build

- use a tempfile instead of a ``StringIO`` for ``git tag -F`` (`57d2e0d <https://github.com/autumnjolitz/instruct/commit/57d2e0d795053368ce156a9b45d28c3736ed8262>`_ by Autumn).
- set version to 0.8.6 (`6590620 <https://github.com/autumnjolitz/instruct/commit/6590620204e82cb8594fb9e41531e603e4b3f05e>`_ by Autumn).

Version `v0.8.5 <https://github.com/autumnjolitz/instruct/releases/tag/v0.8.5>`_
----------------------------------------------------------------------------------

Released 2025-07-08

`Compare with v0.8.4 <https://github.com/autumnjolitz/instruct/compare/v0.8.4...v0.8.5>`_ (17 commits since)

Bug Fixes

- satisfy both mypy and ruff for ``TypingDefinition`` (`895f357 <https://github.com/autumnjolitz/instruct/commit/895f35764c7f549c0a471b1d7ae854f570b7edee>`_ by Autumn).
- apply ``pre-commit`` to all files (`f1164d1 <https://github.com/autumnjolitz/instruct/commit/f1164d1e2177eb557ad653f6898c3a8499e23276>`_ by Autumn).
- ``ValidationError`` should operate on ``.errors`` as it is ``list[Exception] | tuple[Exception, ...]`` (`c6d85bf <https://github.com/autumnjolitz/instruct/commit/c6d85bf163f13bcdef939cd0dfeb9196599825f1>`_ by Autumn).

Docs

- update (`1c69969 <https://github.com/autumnjolitz/instruct/commit/1c699692248952aac6ca18b03ea2038746996589>`_ by Autumn).

Dependencies

- add missing ``=`` for version (`9bfc231 <https://github.com/autumnjolitz/instruct/commit/9bfc231e6589c4c99624ebe08637f901d79c50e7>`_ by Autumn).
- remove ``black``, update packages (`74d22d6 <https://github.com/autumnjolitz/instruct/commit/74d22d64565c87ac24e6e0ddffd2d6b0f1fb1898>`_ by Autumn).

Chore

- satisfy mypy type checks (`8566e7f <https://github.com/autumnjolitz/instruct/commit/8566e7f015af87be76dd86c35bbf64474bd99425>`_ by Autumn).

Continuous Integration

- remove Python 3.7 support (`6b0e61d <https://github.com/autumnjolitz/instruct/commit/6b0e61d6bb519ea31f00585f5760b13edf8d0cbc>`_ by Autumn).

Build

- remove Python 3.10+ specific type reference (`f41c750 <https://github.com/autumnjolitz/instruct/commit/f41c750cdb5893f99b08858fbc86914fed06321d>`_ by Autumn).
- add Python 3.10, 3.12 specific checks (`7a7694f <https://github.com/autumnjolitz/instruct/commit/7a7694ffef9922b9dfcca744c544a03285d4ef78>`_ by Autumn).
- refactor, move verify types/style into task file (`5597576 <https://github.com/autumnjolitz/instruct/commit/5597576a0c44e0c29cab4d33ec1f1268ca8565e5>`_ by Autumn).
- add ``instruct.compat`` as a typing compat module (`76cf633 <https://github.com/autumnjolitz/instruct/commit/76cf6334086d706d0329cac8d4d10592168acb7f>`_ by Autumn).
- drop unused mypy/pytype code (`5d7a32e <https://github.com/autumnjolitz/instruct/commit/5d7a32eb4ff2b85154c21c5968640362003cc3f4>`_ by Autumn).
- update pre-commit with ruff (`f648133 <https://github.com/autumnjolitz/instruct/commit/f648133a945ce5d05bed3c398f3a30fab3fde992>`_ by Autumn).
- update pre-commit-config (`edf9b20 <https://github.com/autumnjolitz/instruct/commit/edf9b20f87cd2ab444b7021cd833fde02814464c>`_ by Autumn).
- update precommit to use ruff (`82f0d9c <https://github.com/autumnjolitz/instruct/commit/82f0d9cd6e714701bca2ba87349141df2a03b75d>`_ by Autumn).
- set version to 0.8.5 (`57ac9d4 <https://github.com/autumnjolitz/instruct/commit/57ac9d4743a3311626dd6c95bc077326d27ad982>`_ by Autumn).

Version `v0.8.4 <https://github.com/autumnjolitz/instruct/releases/tag/v0.8.4>`_
----------------------------------------------------------------------------------

Released 2025-07-08

`Compare with v0.8.3 <https://github.com/autumnjolitz/instruct/compare/v0.8.3...v0.8.4>`_ (3 commits since)

Bug Fixes

- adjust ``copy_with`` to attempt to use ``__class_getitem__`` as the fallback (`597e16f <https://github.com/autumnjolitz/instruct/commit/597e16f6b4ee500d05967418b3855fa10aed1e03>`_ by Autumn).

Docs

- update (`cd8b31d <https://github.com/autumnjolitz/instruct/commit/cd8b31d406b024c2ab344c34e1a5879c9716fb57>`_ by Autumn).

Build

- set version to 0.8.4 (`ad5d62c <https://github.com/autumnjolitz/instruct/commit/ad5d62c153aeeabe6a3d3acb0938dfdeb4c7ffa7>`_ by Autumn).

Version `v0.8.3 <https://github.com/autumnjolitz/instruct/releases/tag/v0.8.3>`_
----------------------------------------------------------------------------------

Released 2025-07-08

`Compare with v0.8.2 <https://github.com/autumnjolitz/instruct/compare/v0.8.2...v0.8.3>`_ (14 commits since)

Features

- run benchmarks in CI, update ``README.rst``, add coverage reports (`c79546b <https://github.com/autumnjolitz/instruct/commit/c79546bdc145d030a7333b031fbfb43d26e1aa79>`_ by Autumn).

Bug Fixes

- correct subtype generation for Python 3.10+ ``types.UnionType``s (`2a970b0 <https://github.com/autumnjolitz/instruct/commit/2a970b062141aec0ae4e2f7fbadd79df1a14a5f1>`_ by Autumn).
- add ``mode`` to benchmarking in ``__main__.py``, refactor slightly (`af22b9b <https://github.com/autumnjolitz/instruct/commit/af22b9b779e41519ca83b546d5680c12c8ff0135>`_ by Autumn).
- ``instruct.Atomic``-derived type keywork argument ``fast=True`` now supports *all* event listener forms (`175f859 <https://github.com/autumnjolitz/instruct/commit/175f85997b92de3be3e173b7530d81b8c6f048a2>`_ by Autumn).
- ``__main__.py`` now can run ``benchmark`` again (`7726865 <https://github.com/autumnjolitz/instruct/commit/7726865f1d46067fce2a9229eba4332f81a039c0>`_ by Autumn).

Docs

- update (`cd2c748 <https://github.com/autumnjolitz/instruct/commit/cd2c74879c36c717c34337deeb13abd794c27de3>`_ by Autumn).
- remove ``|commits-since|`` as it is unused (`310ded3 <https://github.com/autumnjolitz/instruct/commit/310ded3715b1598ab3b1043b9495cfa23f24471e>`_ by Autumn).

Continuous Integration

- tweak output of benchmark post-processing (`2986c9c <https://github.com/autumnjolitz/instruct/commit/2986c9c1e4b2a0ab3722dafcec30716706b8db53>`_ by Autumn).
- rename the workflows (`c12c49e <https://github.com/autumnjolitz/instruct/commit/c12c49e4ea1c3dbb6d26b4f60ec535c0912479b7>`_ by Autumn).

Build

- fix changes since url, CI output (`c50c856 <https://github.com/autumnjolitz/instruct/commit/c50c8562bf9ead06fda7bf769886c002dd8692ad>`_ by Autumn).
- add ``test`` and ``benchmark``commands (`e5a05cf <https://github.com/autumnjolitz/instruct/commit/e5a05cff98684dde9b60b6a8ba2b9a944b51cfca>`_ by Autumn).
- simplify the wrapper code to a common function, implement base64 wrapping (`1aed800 <https://github.com/autumnjolitz/instruct/commit/1aed800245a9f92f8b6e597e7311206c4cb55183>`_ by Autumn).
- set version to 0.8.3 (`e41da57 <https://github.com/autumnjolitz/instruct/commit/e41da57183802955c036010ab8b2d6411729c5f2>`_ by Autumn).

Other

- feature(typedef): implement simple ``type alias = hint`` (3.12+) (`a16b1cb <https://github.com/autumnjolitz/instruct/commit/a16b1cb47f45c6ebc9cd1b3c4f39dffb2839feb6>`_ by Autumn).

Version `v0.8.2 <https://github.com/autumnjolitz/instruct/releases/tag/v0.8.2>`_
----------------------------------------------------------------------------------

Released 2025-07-08

`Compare with v0.8.1 <https://github.com/autumnjolitz/instruct/compare/v0.8.1...v0.8.2>`_ (4 commits since)

Bug Fixes

- handle fixed tuples correctly (`c1bcd41 <https://github.com/autumnjolitz/instruct/commit/c1bcd41a6e58b3b38c106cc29a6d4766db771089>`_ by Autumn).
- use ``types.CodeType.replace(...)`` when available (`8bbc3cf <https://github.com/autumnjolitz/instruct/commit/8bbc3cfb4fe1aee28a80169fef2d21e85455dd7b>`_ by Autumn).

Docs

- update (`820f4ea <https://github.com/autumnjolitz/instruct/commit/820f4ea36c4b859203fa3a10b0aa127f5d90fd94>`_ by Autumn).

Build

- set version to 0.8.2 (`d29ffc5 <https://github.com/autumnjolitz/instruct/commit/d29ffc597b49cce6d2ee999c3f0515e651dee006>`_ by Autumn).

Version `v0.8.1 <https://github.com/autumnjolitz/instruct/releases/tag/v0.8.1>`_
----------------------------------------------------------------------------------

Released 2025-07-08

`Compare with v0.8.0 <https://github.com/autumnjolitz/instruct/compare/v0.8.0...v0.8.1>`_ (6 commits since)

Bug Fixes

- avoid raising an exception inside testing tuple structure for a custom type (`0a3108c <https://github.com/autumnjolitz/instruct/commit/0a3108c8969e87f5294608d081341bfc2ada0c50>`_ by Autumn).

Docs

- update (`900b323 <https://github.com/autumnjolitz/instruct/commit/900b323255092d8148428dc0a5b07d2965d27a3e>`_ by Autumn).
- remove contradictory statement (`e4ed0b4 <https://github.com/autumnjolitz/instruct/commit/e4ed0b40a82be3e24cc0362a5e76832057344204>`_ by Autumn).

Build

- correct changelog link (`bef4aeb <https://github.com/autumnjolitz/instruct/commit/bef4aebd37678963a511227fcb0c8cdb0a074406>`_ by Autumn).
- adjust tasks to allow for releasing on a version other than the ``CURRENT_VERSION.txt`` next default (`fc42c02 <https://github.com/autumnjolitz/instruct/commit/fc42c02de0dbba61bb1e89b61babcd2d1f0429e6>`_ by Autumn).
- bump version to 0.8.1 (`8a4c2ef <https://github.com/autumnjolitz/instruct/commit/8a4c2ef7b4122edab3a92123fd7846bca2571cb8>`_ by Autumn).

Version `v0.8.0 <https://github.com/autumnjolitz/instruct/releases/tag/v0.8.0>`_
----------------------------------------------------------------------------------

Released 2025-07-08

`Compare with v0.7.5.post2 <https://github.com/autumnjolitz/instruct/compare/v0.7.5.post2...v0.8.0>`_ (66 commits since)

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

Version `v0.7.5.post2 <https://github.com/autumnjolitz/instruct/releases/tag/v0.7.5.post2>`_
----------------------------------------------------------------------------------------------

Released 2025-07-08

`Compare with v0.7.5 <https://github.com/autumnjolitz/instruct/compare/v0.7.5...v0.7.5.post2>`_ (1 commits since)

Bug Fixes

- correct for Python 3.7 (`e58c523 <https://github.com/autumnjolitz/instruct/commit/e58c523ce4edbca560267b6a6a0c1fd8919c485c>`_ by Autumn).

Version `v0.7.5 <https://github.com/autumnjolitz/instruct/releases/tag/v0.7.5>`_
----------------------------------------------------------------------------------

Released 2025-07-08

`Compare with first commit <https://github.com/autumnjolitz/instruct/compare/fd12152ab66246e18e4cdcd2876065814f1f8da5...v0.7.5>`_ (7 commits since)

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
