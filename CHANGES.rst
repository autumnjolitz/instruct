.. |Changes|
Version `v0.9.1 <https://github.com/autumnjolitz/instruct/releases/tag/v0.9.1>`_
----------------------------------------------------------------------------------

Released 2025-07-09

`Compare with v0.9.0 <https://github.com/autumnjolitz/instruct/compare/v0.9.0...v0.9.1>`_ (15 commits since)

Bug Fixes

- gather **all** defining scopes for type hint resolution (`ced1d08 <https://github.com/autumnjolitz/instruct/commit/ced1d083e52773529c239c7b6f5c03eaa5b29b37>`_ by Autumn Jolitz).
- satisfy verify-types (`2972b85 <https://github.com/autumnjolitz/instruct/commit/2972b85fc745c1c6ecb90b853e0da440cce9acb9>`_ by Autumn Jolitz).
- handle case where ``instruct.typing.resolve()`` is given ``(type, hint)`` and expects a UnionType out of it (`e796397 <https://github.com/autumnjolitz/instruct/commit/e7963973ddf81805d2aaa2a7970b11169b895bd9>`_ by Autumn Jolitz).

Style

- fix missing whitespace (`4352555 <https://github.com/autumnjolitz/instruct/commit/4352555e611904c0c94852db8db8f1cb72bbaa0c>`_ by Autumn Jolitz).

Continuous Integration

- delete anchor line from rst to avoid pypi errors (`44ee9d8 <https://github.com/autumnjolitz/instruct/commit/44ee9d85e236e86ea16d8754d94eea14456826e1>`_ by Autumn Jolitz).

Build

- set version to 0.9.1 (`0fabda7 <https://github.com/autumnjolitz/instruct/commit/0fabda7b9501da726bc622eb2da502a47d0e0a9a>`_ by Autumn Jolitz).
- remove invalid classifiers due to PyPI returning **only one error per run** (`c227194 <https://github.com/autumnjolitz/instruct/commit/c227194ed136a2251a1f56af4e46316ebd6ca0ea>`_ by Autumn Jolitz).
- fallback to just the README due to PyPi being too restrictive (`6576c9a <https://github.com/autumnjolitz/instruct/commit/6576c9ac12775b7682631fb70aa9471ae2cf780c>`_ by Autumn Jolitz).
- remove changelog due to rst errors on pypi (`fca19ff <https://github.com/autumnjolitz/instruct/commit/fca19ffb9fc1ba5c67867a57c529698fdb7da57f>`_ by Autumn Jolitz).
- include files unconditionally (`ae7c1ab <https://github.com/autumnjolitz/instruct/commit/ae7c1ab272fc49c7b55148aec6d376328d8650dd>`_ by Autumn Jolitz).
- ``invoke build`` may ``--include`` or ``--exclude`` files (`3865f99 <https://github.com/autumnjolitz/instruct/commit/3865f99095a3e9700405e47a89e945bdc5827695>`_ by Autumn Jolitz).
- replace mutable source control references with tagged references (`d17072f <https://github.com/autumnjolitz/instruct/commit/d17072fd10888b42c7e019ca633f63884fade1b1>`_ by Autumn Jolitz).
- prune classifiers, add min python marker (`d4849d5 <https://github.com/autumnjolitz/instruct/commit/d4849d5f28f55bcd4e2e07af5a2e1470e650b066>`_ by Autumn Jolitz).
- add changelog and benchmark to source dist (`8bc2ac3 <https://github.com/autumnjolitz/instruct/commit/8bc2ac3b18401aef1e439ef0a263919b0b40e7fe>`_ by Autumn Jolitz).
- set version to 0.9.1a0 (`eaa1cce <https://github.com/autumnjolitz/instruct/commit/eaa1cce5b34ab34ab61c4bbbb50d0bd1c95ab737>`_ by Autumn Jolitz).

Version `v0.9.0 <https://github.com/autumnjolitz/instruct/releases/tag/v0.9.0>`_
----------------------------------------------------------------------------------

Released 2025-07-08

`Compare with v0.8.6 <https://github.com/autumnjolitz/instruct/compare/v0.8.6...v0.9.0>`_ (26 commits since)

Features

- remove class keyword ``concrete_class`` fully in favor of ``contextvars.ContextVar`` approach (`378680d <https://github.com/autumnjolitz/instruct/commit/378680d0be63665b26b3fbd4fb4e16c9e3ae7b80>`_ by Autumn).
- upgrade all files to 3.8 (`25d2874 <https://github.com/autumnjolitz/instruct/commit/25d2874ec1b9bc52ea3dbf3cbad6f0b98162e832>`_ by Autumn).
- drop 3.7 official support (`8818c45 <https://github.com/autumnjolitz/instruct/commit/8818c457033ab85408fc35e8c57cc70caa2c21cd>`_ by Autumn).

Bug Fixes

- remove unused field (`78596a3 <https://github.com/autumnjolitz/instruct/commit/78596a3add164687559e2a87a3767eafdc45c5e4>`_ by Autumn).
- format (`a9e1c4b <https://github.com/autumnjolitz/instruct/commit/a9e1c4b784d6094e24da64e46f9c3c00e0615d67>`_ by Autumn).

Docs

- update (`a9d73c6 <https://github.com/autumnjolitz/instruct/commit/a9d73c601fa9419cede295891673fede89a196bb>`_ by Autumn Jolitz).
- remove broken change logs (`4d94f1e <https://github.com/autumnjolitz/instruct/commit/4d94f1e9bb6b574313e4238784f09adb18fa449b>`_ by Autumn).

Dependencies

- update pre-commit-hooks (`dc016c3 <https://github.com/autumnjolitz/instruct/commit/dc016c3d4cd2a0960b1fdd05cf94aab688f08016>`_ by Autumn Jolitz).

Style

- fix ignore comments (`30ed5e1 <https://github.com/autumnjolitz/instruct/commit/30ed5e17b7f0ff54a9355b908543420e5e92c7b1>`_ by Autumn Jolitz).

Chore

- pass linter on ``__main__.py`` (`ef815a6 <https://github.com/autumnjolitz/instruct/commit/ef815a668ee5b2bad15024811cfef01d400092e5>`_ by Autumn).
- update copyright year (`9795d2e <https://github.com/autumnjolitz/instruct/commit/9795d2e53916c465ad5e8f4fd95b0bee82b73af7>`_ by Autumn).

Build

- set version to 0.9.0 (`455acea <https://github.com/autumnjolitz/instruct/commit/455acea6b2467bc053c81783ee37f329c8270d05>`_ by Autumn Jolitz).
- remove changelog constraints, fix up changelog with release dates from `PyPI <https://pypi.org/project/instruct/#history>`_ (`f88d342 <https://github.com/autumnjolitz/instruct/commit/f88d34226d8a61b3f303d6d79c7343b2156bf618>`_ by Autumn Jolitz).
- fix setup to account for git's packed refs, add ``packaging`` to setup requirements (`7330dba <https://github.com/autumnjolitz/instruct/commit/7330dba96a072c8e3a94737194c5034035eb932b>`_ by Autumn Jolitz).
- use newer commit as ``git log`` can't see the older commit (`9828f81 <https://github.com/autumnjolitz/instruct/commit/9828f814746e4e5e60db9d09b77e2d86dac3092e>`_ by Autumn).
- fix case where venv was not passing ``--devel``/``--tests`` (`6cecebc <https://github.com/autumnjolitz/instruct/commit/6cecebc00f079e5e86be57f665ff8896b45f98c9>`_ by Autumn).
- ignore ``__main__.py`` for pyupgrade (`32bfcc7 <https://github.com/autumnjolitz/instruct/commit/32bfcc77bad1269e938a7a3c1e4d81ebbc094411>`_ by Autumn).
- enforce py38+ typing (`d32d3e0 <https://github.com/autumnjolitz/instruct/commit/d32d3e02da7699d6f4edacf8eff98967f8c45ab4>`_ by Autumn).
- use 3.8 as lowest python (`5b6a820 <https://github.com/autumnjolitz/instruct/commit/5b6a820311e3f99fbf0bd227be0edd40d4f2100c>`_ by Autumn).
- set version to 0.8.7 (`1d83ee5 <https://github.com/autumnjolitz/instruct/commit/1d83ee5cacd42442ea6208917c95d04cbe8c98a6>`_ by Autumn).
- fix changes since url, CI output (`b261284 <https://github.com/autumnjolitz/instruct/commit/b2612843e91d576f644c0aae2d11b52e15227568>`_ by Autumn).
- fix changelog generation (`5ab995d <https://github.com/autumnjolitz/instruct/commit/5ab995d8cd773c475c4091b8f7b40a288ead5c98>`_ by Autumn).

Other

- feature!: remove type ``_parent`` in favor of fixed thunks on data classes pointing to parent and metaclass handling type level queries (`7148644 <https://github.com/autumnjolitz/instruct/commit/7148644cbfd0816234ea851f82a47b8cd8d0caff>`_ by Autumn).
- feature: correct typehints and implement slice/int array operations by default (`76fb2f9 <https://github.com/autumnjolitz/instruct/commit/76fb2f9aa54dfc06fdcb26fda157f6bfe9c3f773>`_ by Autumn).
- feature: make use of ``deduplicate(...)`` (`f944d91 <https://github.com/autumnjolitz/instruct/commit/f944d9133efc359da466c5e4563b22452e353658>`_ by Autumn).
- feature!: clean up, deprecate class kwargs that can clash with other impls (`a53552f <https://github.com/autumnjolitz/instruct/commit/a53552f02ff2d9bf093c5851093eb72f76ba42b5>`_ by Autumn).

Version `v0.8.6 <https://github.com/autumnjolitz/instruct/releases/tag/v0.8.6>`_
----------------------------------------------------------------------------------

Released 2025-06-11

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

Released 2025-05-07

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

Released 2024-06-30

`Compare with v0.8.3 <https://github.com/autumnjolitz/instruct/compare/v0.8.3...v0.8.4>`_ (3 commits since)

Bug Fixes

- adjust ``copy_with`` to attempt to use ``__class_getitem__`` as the fallback (`597e16f <https://github.com/autumnjolitz/instruct/commit/597e16f6b4ee500d05967418b3855fa10aed1e03>`_ by Autumn).

Docs

- update (`cd8b31d <https://github.com/autumnjolitz/instruct/commit/cd8b31d406b024c2ab344c34e1a5879c9716fb57>`_ by Autumn).

Build

- set version to 0.8.4 (`ad5d62c <https://github.com/autumnjolitz/instruct/commit/ad5d62c153aeeabe6a3d3acb0938dfdeb4c7ffa7>`_ by Autumn).

Version `v0.8.3 <https://github.com/autumnjolitz/instruct/releases/tag/v0.8.3>`_
----------------------------------------------------------------------------------

Released 2024-06-30

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

Released 2024-06-23

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

Released 2024-06-16

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

Released 2024-06-09

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

Released 2024-02-29

`Compare with v0.7.5 <https://github.com/autumnjolitz/instruct/compare/v0.7.5...v0.7.5.post2>`_ (1 commits since)

Bug Fixes

- correct for Python 3.7 (`e58c523 <https://github.com/autumnjolitz/instruct/commit/e58c523ce4edbca560267b6a6a0c1fd8919c485c>`_ by Autumn).

Version `v0.7.5 <https://github.com/autumnjolitz/instruct/releases/tag/v0.7.5>`_
----------------------------------------------------------------------------------

Released 2024-02-29

`Compare with v0.7.3.post1 <https://github.com/autumnjolitz/instruct/compare/v0.7.3.post1...v0.7.5>`_ (9 commits since)

Features

- support ``type | type`` in Python 3.10 and above, implement ``__init_subclass__(cls)`` (`88164e3 <https://github.com/autumnjolitz/instruct/commit/88164e390267b6ee690d88bed6e60e17bd4da98b>`_ by Autumn).

Docs

- try to make more friendly for github (`46df415 <https://github.com/autumnjolitz/instruct/commit/46df4150a4928659b4464ef9282da033c8cabea2>`_ by Autumn Jolitz).
- update ``CHANGES.rst``, ``README.rst`` (`42bd3d2 <https://github.com/autumnjolitz/instruct/commit/42bd3d23f11362d3584896fb8b31a4aa83103bf2>`_ by Autumn Jolitz).
- template-ize for release note generation (`5e508b7 <https://github.com/autumnjolitz/instruct/commit/5e508b714bb47cd2d904a75e4534d7ffab912867>`_ by Autumn Jolitz).
- test of `git-changelog <https://github.com/pawamoy/git-changelog>`_ (`a4aeb37 <https://github.com/autumnjolitz/instruct/commit/a4aeb375e0ee83fdbbb332d8d5573fadf91d8917>`_ by Autumn Jolitz).

Chore

- add badges to ``README.rst``, adjust github CI workflow names (`66b4067 <https://github.com/autumnjolitz/instruct/commit/66b4067edb731e1f76e324fa46e1127bdcc51f6c>`_ by Autumn).

Continuous Integration

- add PyPy in testing (`fd12152 <https://github.com/autumnjolitz/instruct/commit/fd12152ab66246e18e4cdcd2876065814f1f8da5>`_ by Autumn Jolitz).

Build

- bump version to v0.7.5 (`9924da8 <https://github.com/autumnjolitz/instruct/commit/9924da815d892a9c4b3127f337c7cd965148d033>`_ by Autumn).
- refactor, use `invoke <https://www.pyinvoke.org/>`_ (`5871827 <https://github.com/autumnjolitz/instruct/commit/5871827f418aa250b3c4bef48d7b2f448ae3d956>`_ by Autumn Jolitz).

Version `v0.7.3.post1 <https://github.com/autumnjolitz/instruct/releases/tag/v0.7.3.post1>`_
----------------------------------------------------------------------------------------------

Released 2023-12-04

`Compare with v0.7.3 <https://github.com/autumnjolitz/instruct/compare/v0.7.3...v0.7.3.post1>`_ (2 commits since)

Continuous Integration

- add test (`f3c25b0 <https://github.com/autumnjolitz/instruct/commit/f3c25b05b752ed6e329afe45a578b00441787f4a>`_ by Autumn).

Build

- bump version to v0.7.3.post1 (`f8afb3d <https://github.com/autumnjolitz/instruct/commit/f8afb3d562f177e23e9b679c7b6a85ed84ad8b62>`_ by Autumn).

Version `v0.7.3 <https://github.com/autumnjolitz/instruct/releases/tag/v0.7.3>`_
----------------------------------------------------------------------------------

Released 2023-07-18

`Compare with v0.7.2 <https://github.com/autumnjolitz/instruct/compare/v0.7.2...v0.7.3>`_ (2 commits since)

Features

- Port instruct to newer Python versions, implement CI/CD (`7dda1bd <https://github.com/autumnjolitz/instruct/commit/7dda1bde4af7e53808f278c07fca9adbc23c147e>`_ by Autumn Jolitz).

Build

- unlock versions to be more flexible, bump to v0.7.3 (`2e0a5cc <https://github.com/autumnjolitz/instruct/commit/2e0a5ccc731ba686f8738d045b4af9d9061f2411>`_ by Autumn).

Version `v0.7.2 <https://github.com/autumnjolitz/instruct/releases/tag/v0.7.2>`_
----------------------------------------------------------------------------------

Released 2022-05-13

`Compare with v0.7.1 <https://github.com/autumnjolitz/instruct/compare/v0.7.1...v0.7.2>`_ (8 commits since)

Features

- export ``RangeFlags`` (`7420aa5 <https://github.com/autumnjolitz/instruct/commit/7420aa53aa6e5cd7e9ba660daa97fcffb147107e>`_ by Autumn).
- remove fast new in favor of calling ``self._set_defaults()`` (`6edb925 <https://github.com/autumnjolitz/instruct/commit/6edb9255850aaadef7c1ad407e2f5341975c01a6>`_ by Autumn).

Bug Fixes

- add dummy ``__iter__`` to handle empty class case (`a51c252 <https://github.com/autumnjolitz/instruct/commit/a51c25208af689506235231c900dd91ffd1c43fb>`_ by Autumn).

Docs

- add notes on use of ``Range`` and friends (`04356d2 <https://github.com/autumnjolitz/instruct/commit/04356d234b83019f5c825cea42fa371ebe8d392b>`_ by Autumn).
- add comparison between instruct and pydantic (`9090595 <https://github.com/autumnjolitz/instruct/commit/90905952eb8ac3153c3ec66446103fb4e2bcdca9>`_ by Autumn).
- update (`f8c0209 <https://github.com/autumnjolitz/instruct/commit/f8c0209afac48ed377cce28f5d366978388f672d>`_ by Autumn).

Tests

- use ``_set_defaults``  instead (`7ccf4a4 <https://github.com/autumnjolitz/instruct/commit/7ccf4a4405ebd1c800e160deeac980556c540513>`_ by Autumn).
- add tests for ``_set_defaults(...)`` on a class (`12e2ee7 <https://github.com/autumnjolitz/instruct/commit/12e2ee7efb1a8dc65704452517ec64213616850a>`_ by Autumn).

Version `v0.7.1 <https://github.com/autumnjolitz/instruct/releases/tag/v0.7.1>`_
----------------------------------------------------------------------------------

Released 2022-05-13

`Compare with v0.7.0 <https://github.com/autumnjolitz/instruct/compare/v0.7.0...v0.7.1>`_ (5 commits since)

Features

- export ``instruct.clear()``, ``instruct.reset_to_defaults()``, make `instance._set_defaults()` first call the zero-init version, then cascade through the inheritance tree for any overrides, add default functions for empty classes, use ``__public_class__`` magic method for ``public_class`` calls (`1d1e528 <https://github.com/autumnjolitz/instruct/commit/1d1e528cd3ef8c1faa3218122f54e91f6f381d1d>`_ by Autumn).

Chore

- remove unused import in ``__main__.py`` (`fadf4c6 <https://github.com/autumnjolitz/instruct/commit/fadf4c6ae68dd5c7230270ae39fa672326870192>`_ by Autumn).

Continuous Integration

- check style (`252f2ba <https://github.com/autumnjolitz/instruct/commit/252f2ba27a0ae91563ad9a88da6eb4c56f8af715>`_ by Autumn).

Build

- v0.7.1 (`da6f64d <https://github.com/autumnjolitz/instruct/commit/da6f64d62a1f6a3bf2449b9b46e7ce5c8d3186cf>`_ by Autumn).
- add **devel** extra (`87c6e3b <https://github.com/autumnjolitz/instruct/commit/87c6e3ba5ae8da7b8c6cb34620c877ea6babc8e3>`_ by Autumn).

Version `v0.7.0 <https://github.com/autumnjolitz/instruct/releases/tag/v0.7.0>`_
----------------------------------------------------------------------------------

Released 2022-05-12

`Compare with v0.6.7 <https://github.com/autumnjolitz/instruct/compare/v0.6.7...v0.7.0>`_ (7 commits since)

Features

- spider annotations, use the ``NoPickle`` et al constants to influence class behavior (`2eea997 <https://github.com/autumnjolitz/instruct/commit/2eea997c6a742a293ecf33f1ab0fe795006be60a>`_ by Autumn).
- support ``Annotation[...]`` and within it, a set of ``Range``s, raise ``RangeError`` when a value is type allowed but does not fit the ranges specified! (`42599b0 <https://github.com/autumnjolitz/instruct/commit/42599b0fefe8a27dc645245e1aa34d97816954a2>`_ by Autumn).
- implement several constants for use in ``Annotation[...]`` including ``Range`` for interval capping (and ``RangeError``)! (`11f25b3 <https://github.com/autumnjolitz/instruct/commit/11f25b3ced2530fb8620da6beeca0053a50160a5>`_ by Autumn).

Docs

- update README, add a CHANGES file (`8840218 <https://github.com/autumnjolitz/instruct/commit/8840218f372211854bcdd732a6ec5d0d8e81b820>`_ by Autumn).

Dependencies

- bump jinja2 and typing_extensions versions (`9adca04 <https://github.com/autumnjolitz/instruct/commit/9adca04cc2c6c2132884f5a45ea94eb623127385>`_ by Autumn).

Tests

- add additional tests (`7aa8c31 <https://github.com/autumnjolitz/instruct/commit/7aa8c315d64291ca0347d7a542c2891d84f5b596>`_ by Autumn).

Build

- bump to v0.7.0 (`f97c699 <https://github.com/autumnjolitz/instruct/commit/f97c6990649390292fc308ee7c5aeb43630f34cf>`_ by Autumn).

Version `v0.6.7 <https://github.com/autumnjolitz/instruct/releases/tag/v0.6.7>`_
----------------------------------------------------------------------------------

Released 2021-03-31

`Compare with v0.6.6 <https://github.com/autumnjolitz/instruct/compare/v0.6.6...v0.6.7>`_ (1 commits since)

Performance Improvements

- cache by effective skipped fields across the board, do not confuse with second level skip/redefinitions, bump to v0.6.7 (`10aea05 <https://github.com/autumnjolitz/instruct/commit/10aea05582e1015834f179516c8b174c1d3a08c5>`_ by Autumn).

Version `v0.6.6 <https://github.com/autumnjolitz/instruct/releases/tag/v0.6.6>`_
----------------------------------------------------------------------------------

Released 2021-02-17

`Compare with v0.6.5 <https://github.com/autumnjolitz/instruct/compare/v0.6.5...v0.6.6>`_ (1 commits since)

Bug Fixes

- handle zero-length collections correctly, type hints should resolve using the locals, module globals, then typing ones, bump to v0.6.6 (`b7d0898 <https://github.com/autumnjolitz/instruct/commit/b7d0898980f74dbb4e8af9635300e1153133bdf8>`_ by Autumn).

Version `v0.6.5 <https://github.com/autumnjolitz/instruct/releases/tag/v0.6.5>`_
----------------------------------------------------------------------------------

Released 2021-02-16

`Compare with v0.6.4 <https://github.com/autumnjolitz/instruct/compare/v0.6.4...v0.6.5>`_ (1 commits since)

Features

- allow ``instruct.public_class()`` to access subclasses by index, document ambiguities, cascade subtraction preservation, bump to v0.6.5 (`8a0fdda <https://github.com/autumnjolitz/instruct/commit/8a0fddacc5033d2bfb845a1d83e55eae2bf745e5>`_ by Autumn).

Version `v0.6.4 <https://github.com/autumnjolitz/instruct/releases/tag/v0.6.4>`_
----------------------------------------------------------------------------------

Released 2021-01-13

`Compare with v0.6.3 <https://github.com/autumnjolitz/instruct/compare/v0.6.3...v0.6.4>`_ (1 commits since)

Bug Fixes

- adjust ``instruct.public_class`` to detect modified subtracted classes, allow proper overrides of ``__coerce__`` when class inheritance is greater than 1 deep, bump to v0.6.4 (`c4d2b91 <https://github.com/autumnjolitz/instruct/commit/c4d2b91e5fb3bf853d228edf8664480137dfe392>`_ by Autumn).

Version `v0.6.3 <https://github.com/autumnjolitz/instruct/releases/tag/v0.6.3>`_
----------------------------------------------------------------------------------

Released 2020-12-07

`Compare with v0.6.2 <https://github.com/autumnjolitz/instruct/compare/v0.6.2...v0.6.3>`_ (1 commits since)

Bug Fixes

- fix ``.keys(...)`` to operate on simple field that is ``Atomic`` descendant (no optional, etc wrapping), bump to v0.6.3 (`697a4ec <https://github.com/autumnjolitz/instruct/commit/697a4ecfe47ecc6de41df60171f14fc4aa28e2d3>`_ by Autumn).

Version `v0.6.2 <https://github.com/autumnjolitz/instruct/releases/tag/v0.6.2>`_
----------------------------------------------------------------------------------

Released 2020-12-07

`Compare with v0.6.1 <https://github.com/autumnjolitz/instruct/compare/v0.6.1...v0.6.2>`_ (3 commits since)

Features

- add ``instruct.show_all_fields`` to public API, ensure reachability for ``Optional`` type hinted fields (`5dde190 <https://github.com/autumnjolitz/instruct/commit/5dde190da1313dbec2ca3c6c723b2611cdedbc43>`_ by Autumn).
- allow ``instruct.keys()``, ``instruct.show_all_fields()`` to handle ``Union``, ``Optional`` with embedded ``Atomic`` types properly (`47f038d <https://github.com/autumnjolitz/instruct/commit/47f038dfb3936d255d8660d563cf94efad89f04d>`_ by Autumn).

Build

- v0.6.2 (`7e60b6a <https://github.com/autumnjolitz/instruct/commit/7e60b6ae264d08053235ecd50a35d8877a8efd7c>`_ by Autumn).

Version `v0.6.1 <https://github.com/autumnjolitz/instruct/releases/tag/v0.6.1>`_
----------------------------------------------------------------------------------

Released 2020-12-07

`Compare with v0.6.0 <https://github.com/autumnjolitz/instruct/compare/v0.6.0...v0.6.1>`_ (1 commits since)

Features

- allow class subtractions to be pickled/unpickled, make type name friendlier to ``inflection.titleize(...)``, ensure a test for class method replacements, pickling, bump to v0.6.1 (`e28f6c6 <https://github.com/autumnjolitz/instruct/commit/e28f6c66af8753060e783d829e2c89029d2a59b7>`_ by Autumn).

Version `v0.6.0 <https://github.com/autumnjolitz/instruct/releases/tag/v0.6.0>`_
----------------------------------------------------------------------------------

Released 2020-12-04

`Compare with v0.5.0 <https://github.com/autumnjolitz/instruct/compare/v0.5.0...v0.6.0>`_ (34 commits since)

Features

- allow keys() to operate and extract keys for an embedded field (`647ee5c <https://github.com/autumnjolitz/instruct/commit/647ee5c7c6dbd6979a574d56a0cc21f2fa991719>`_ by Autumn).
- allow for downcasting of a parent type to a subtracted type when generating the skip keys type (`9ca88d0 <https://github.com/autumnjolitz/instruct/commit/9ca88d0d4f3c45c6679fa84940e57cc9291b65be>`_ by Autumn).
- support collections by position, make unions branch on type checks, avoid pipe-nature in favor of graph branch approach (`fcbc5bc <https://github.com/autumnjolitz/instruct/commit/fcbc5bc1c3ac8ce985e8bf00075c6181a3e11c3c>`_ by Autumn).
- allow for generation of an effective coerce function based on type spidering (`b2f8195 <https://github.com/autumnjolitz/instruct/commit/b2f81953807eac4ac6d31ca04797fa2d5a8311eb>`_ by Autumn).
- introduce a union branch function that assumes unique traces in subtype (`7078730 <https://github.com/autumnjolitz/instruct/commit/7078730baae72305526c2bfe1320df2fc7f16c1d>`_ by Autumn).
- add in initial approach (````subtype.py````) for automated parent value type coercion to subtracted type (`5b50dc2 <https://github.com/autumnjolitz/instruct/commit/5b50dc2f264f33e02a5bfb3e8e3be50adc3cd2b7>`_ by Autumn).
- handle subtracted classes in a more generalized fashion, use the correct function globals for the ``LOAD_GLOBAL`` bytecode (`531918e <https://github.com/autumnjolitz/instruct/commit/531918eb0f43c5570acdad449d8b9c0e6d4cfff7>`_ by Autumn).
- support ``classmethod()`` rewriting for skip keys (`1505945 <https://github.com/autumnjolitz/instruct/commit/1505945e464a2789237164505741f053dafb7aeb>`_ by Autumn).
- implement ``cls & {...}`` (type inclusion masks) (`fbff83f <https://github.com/autumnjolitz/instruct/commit/fbff83f9c33cd31e4c923f0d4ac96a017d7e8311>`_ by Autumn).
- introduce more complex type subtractions that are commutative (`17ad8af <https://github.com/autumnjolitz/instruct/commit/17ad8af5d9290afe620fe8728773a26bf53c8a19>`_ by Autumn).
- implement a search-and-replace of instruct ``Atomics`` inside of type hint instances w/o overriding a singleton class instance (`39c8084 <https://github.com/autumnjolitz/instruct/commit/39c808471163a694b69d6aef43711aefb06cebcb>`_ by Autumn).
- implement single level, single ``Atomic``-descendant removal of attribute names on an ``Atomic``-derived object (termed **Skip Keys**) (`422e7b4 <https://github.com/autumnjolitz/instruct/commit/422e7b4e5e050170b61ead9f92d3fd99c3f5e707>`_ by Autumn).

Performance Improvements

- refactor, allow caching of class subtractions via ``FrozenMapping`` (`d3e9ef7 <https://github.com/autumnjolitz/instruct/commit/d3e9ef71ff345f624223b3ad24af18f4ab472463>`_ by Autumn).

Bug Fixes

- in case of a tuple of existing types, add to it for the union (`bbd1ef6 <https://github.com/autumnjolitz/instruct/commit/bbd1ef6ed8f31a6f2f4507623d262faef76fbcfb>`_ by Autumn).
- on subtraction of fields that cannot be, just ignore it (`08163a5 <https://github.com/autumnjolitz/instruct/commit/08163a5533c7b44dfb3eda55a7847ce536106cad>`_ by Autumn).
- allow overriding of callouts to a class in a ``__coerce__`` function by using a closure intercept (`f2be81a <https://github.com/autumnjolitz/instruct/commit/f2be81a7a12f07ab5e154f6bc0877890073b45fd>`_ by Autumn).

Code Refactoring

- reduce wildcard exports, export ``instruct.public_class(...)`` (`890de96 <https://github.com/autumnjolitz/instruct/commit/890de968acec0543cfb832fa9555131e94377cae>`_ by Autumn).
- limit ``instruct.show_all_fields``, refactor ``CellType`` creation to a simpler form (`ea9d46f <https://github.com/autumnjolitz/instruct/commit/ea9d46f9815e331f24cf9a182e7b5470eadc3c06>`_ by Autumn).

Docs

- track progress (`4fdc793 <https://github.com/autumnjolitz/instruct/commit/4fdc793828a12f3b51bda2aae7fe959243def7bc>`_ by Autumn).
- update goals (`0a26794 <https://github.com/autumnjolitz/instruct/commit/0a2679417a292372b7a4b5d9656f5ffd9e307655>`_ by Autumn).

Tests

- move nameless person to test scope to pass flake8 false negative (`6fb8d11 <https://github.com/autumnjolitz/instruct/commit/6fb8d110801dc16260879909b72a6e3e2fd98c55>`_ by Autumn).
- document absurdities (`f231790 <https://github.com/autumnjolitz/instruct/commit/f231790e957213437b0ce4e551ea403ce50fc723>`_ by Autumn).
- note where the cached classes may be looked up (`e87d49a <https://github.com/autumnjolitz/instruct/commit/e87d49abd3b8e8af512f91e42d84a4f8ba7d629a>`_ by Autumn).

Chore

- add generic type hint param ``U`` (`6d12f28 <https://github.com/autumnjolitz/instruct/commit/6d12f289073cfa66a38113aa036f491c1c8de1bb>`_ by Autumn).
- annotate the ``ClassOrInstanceFuncsDescriptor`` (`513c103 <https://github.com/autumnjolitz/instruct/commit/513c10377593dc0535a1da73a484c083768d127a>`_ by Autumn).
- add ``CellType`` (`3054875 <https://github.com/autumnjolitz/instruct/commit/30548754ac1f867c094c403c46b906ed6b9a8b59>`_ by Autumn).
- add stub for annotated decoding (`75efce7 <https://github.com/autumnjolitz/instruct/commit/75efce75709cd64f3d74cfd7a1937938faa1c5e3>`_ by Autumn).
- add missing type (`5f46828 <https://github.com/autumnjolitz/instruct/commit/5f46828f6823aa08234bca2d1b088d01e12e9116>`_ by Autumn).

Continuous Integration

- update workflow (`a70bf50 <https://github.com/autumnjolitz/instruct/commit/a70bf50947c9a23e008e93ac5e82faf1170aa812>`_ by Autumn).
- Add github action to test project (`b938446 <https://github.com/autumnjolitz/instruct/commit/b9384469e6449e861df8de9aba35a8cf41b16d44>`_ by Autumn Jolitz).

Build

- v0.6.0 release (`2784646 <https://github.com/autumnjolitz/instruct/commit/27846462454ca26b17d544cc0aeab8a35e205190>`_ by Autumn).
- add trailing newline (`526c1de <https://github.com/autumnjolitz/instruct/commit/526c1deb62c427495f421d32c3dc2a136c0c9dfb>`_ by Autumn).
- ignore build, pytype files (`cc2051e <https://github.com/autumnjolitz/instruct/commit/cc2051e60ae9ed82d0cca3f3007d73bd12248903>`_ by Autumn).

Version `v0.5.0 <https://github.com/autumnjolitz/instruct/releases/tag/v0.5.0>`_
----------------------------------------------------------------------------------

Released 2020-11-10

`Compare with v0.4.13 <https://github.com/autumnjolitz/instruct/compare/v0.4.13...v0.5.0>`_ (2 commits since)

Features

- implement for ``Literal[...]``, bump minimum ``typing_extensions`` version, bump to v0.5.0 (`dbad02c <https://github.com/autumnjolitz/instruct/commit/dbad02c0ae55643452994dc5d14cd2938d55c4a0>`_ by Autumn).

Docs

- track new design goals (`fb1125f <https://github.com/autumnjolitz/instruct/commit/fb1125fce11d00d6992b86e67929a64703414e10>`_ by Autumn).

Version `v0.4.13 <https://github.com/autumnjolitz/instruct/releases/tag/v0.4.13>`_
------------------------------------------------------------------------------------

Released 2020-09-30

`Compare with v0.4.12 <https://github.com/autumnjolitz/instruct/compare/v0.4.12...v0.4.13>`_ (1 commits since)

Bug Fixes

- correct typo where disabling derived should apply at **all** times, not only in *debug mode*, bump to v0.4.13 (`4801c14 <https://github.com/autumnjolitz/instruct/commit/4801c14bf72d3ea1146edc400b20732feaacba5f>`_ by Autumn).

Version `v0.4.12 <https://github.com/autumnjolitz/instruct/releases/tag/v0.4.12>`_
------------------------------------------------------------------------------------

Released 2020-09-30

`Compare with v0.4.11 <https://github.com/autumnjolitz/instruct/compare/v0.4.11...v0.4.12>`_ (1 commits since)

Bug Fixes

- when ``dict`` is in the __coerce__ types for a key, disable ``derived`` matching for setters, bump to v0.4.12 (`40ebbb3 <https://github.com/autumnjolitz/instruct/commit/40ebbb3536dc7c011bee278201705fd2d1306464>`_ by Autumn).

Version `v0.4.11 <https://github.com/autumnjolitz/instruct/releases/tag/v0.4.11>`_
------------------------------------------------------------------------------------

Released 2020-07-15

`Compare with v0.4.9 <https://github.com/autumnjolitz/instruct/compare/v0.4.9...v0.4.11>`_ (3 commits since)

Features

- add top module level functions (``asdict()``, ``keys()``, etc), implement ``bytes`` support for ``json`` encoding, ``__coerce__`` may now have a tuple of field names in place of a field name to assign a single coercion to multiple attributes, bump to v0.4.11 (`9bb6344 <https://github.com/autumnjolitz/instruct/commit/9bb6344cc4d4f4b285f08e48bcad82181307e96d>`_ by Autumn).
- implement metaclass support of ``keys()``/``values()``/``items()``/``to_json()`` (allows class definitions to override those names but still recover it via the type or metaclass), add ``tuple``, ``list``, ``dict`` and ``NamedTuple``-like helper functions, bump to v0.4.10 (`1ee382a <https://github.com/autumnjolitz/instruct/commit/1ee382a3fae5141a2c763e31e722bc0eeea6c655>`_ by Autumn).

Chore

- preallocate names, values, ids before test (`373d6a2 <https://github.com/autumnjolitz/instruct/commit/373d6a29bc90f84086eeb6c9ab302d00560b47c0>`_ by Autumn).

Version `v0.4.9 <https://github.com/autumnjolitz/instruct/releases/tag/v0.4.9>`_
----------------------------------------------------------------------------------

Released 2020-07-07

`Compare with v0.4.8 <https://github.com/autumnjolitz/instruct/compare/v0.4.8...v0.4.9>`_ (1 commits since)

Bug Fixes

- correct issue where keyword only defaults were stripped, bump to v0.4.9 (`97ed502 <https://github.com/autumnjolitz/instruct/commit/97ed5022d3b735700d2e54bbcc37893b4ceb1af5>`_ by Autumn).

Version `v0.4.8 <https://github.com/autumnjolitz/instruct/releases/tag/v0.4.8>`_
----------------------------------------------------------------------------------

Released 2020-07-02

`Compare with v0.4.7 <https://github.com/autumnjolitz/instruct/compare/v0.4.7...v0.4.8>`_ (1 commits since)

Bug Fixes

- update ``README.rst``, allow class definition in IDLE sessions, bump to v0.4.8 (`2e70769 <https://github.com/autumnjolitz/instruct/commit/2e70769b79bf39c16ae5e68adb9c5beee7b469f9>`_ by Autumn).

Version `v0.4.7 <https://github.com/autumnjolitz/instruct/releases/tag/v0.4.7>`_
----------------------------------------------------------------------------------

Released 2020-07-02

`Compare with v0.4.6 <https://github.com/autumnjolitz/instruct/compare/v0.4.6...v0.4.7>`_ (2 commits since)

Features

- implement ``dataclass``/``NamedTuple``-like type hinting, allow for overriding of autogenerated magic methods while allowing argless ``super()`` in their overrides, bump to v0.4.7 (`b71398b <https://github.com/autumnjolitz/instruct/commit/b71398bd2be8e14e7a25d812c209d434ac4d119b>`_ by Autumn).

Build

- fix ``precommit`` to older ``black`` because I feel the new tuple unpacking style for everything is rather noisy (`00e9450 <https://github.com/autumnjolitz/instruct/commit/00e9450a2d40b756cc92f503ad42a3ee53093fd4>`_ by Autumn).

Version `v0.4.6 <https://github.com/autumnjolitz/instruct/releases/tag/v0.4.6>`_
----------------------------------------------------------------------------------

Released 2020-05-11

`Compare with v0.4.5 <https://github.com/autumnjolitz/instruct/compare/v0.4.5...v0.4.6>`_ (5 commits since)

Features

- allow subtraction of fields on an adhoc basis, bump to v0.4.6 (`59cf2b1 <https://github.com/autumnjolitz/instruct/commit/59cf2b1da59b0689b34f96057dba59a2c402a14b>`_ by Autumn).
- add helper function to typedef to check if atomic type class or meta (`a280f4b <https://github.com/autumnjolitz/instruct/commit/a280f4becd61ec69eca97e5ad613497b8a5a3f18>`_ by Autumn).

Bug Fixes

- avoid calling ``parse_typedef`` on ``__coerce__ = None`` (`4018332 <https://github.com/autumnjolitz/instruct/commit/40183325773228d3a479e2dbc84b41aa0d94d0cc>`_ by Autumn).

Code Refactoring

- refactor to make clearer, rename ``dataclass`` to ``concrete_class`` to signal "don't touch this" (`2342e46 <https://github.com/autumnjolitz/instruct/commit/2342e46bb705bd9fef0bb4480d2ae04bf491c33e>`_ by Autumn).

Docs

- document ````typedef.py```` to be clearer, remove erroneous cast to type (`802cc67 <https://github.com/autumnjolitz/instruct/commit/802cc67eb5c3b21005762bd59aaa73e760544e42>`_ by Autumn).

Version `v0.4.5 <https://github.com/autumnjolitz/instruct/releases/tag/v0.4.5>`_
----------------------------------------------------------------------------------

Released 2020-02-14

`Compare with v0.4.4 <https://github.com/autumnjolitz/instruct/compare/v0.4.4...v0.4.5>`_ (1 commits since)

Performance Improvements

- keep a weak reference to the owning classes to avoid constant rebinding for one-time class definitions, bump to v0.4.5 (`fa6b459 <https://github.com/autumnjolitz/instruct/commit/fa6b459dd5b6afc9c4d68c07acc27aabb262a028>`_ by Autumn Jolitz).

Version `v0.4.4 <https://github.com/autumnjolitz/instruct/releases/tag/v0.4.4>`_
----------------------------------------------------------------------------------

Released 2020-02-10

`Compare with v0.4.3 <https://github.com/autumnjolitz/instruct/compare/v0.4.3...v0.4.4>`_ (1 commits since)

Features

- order preserving ``keys()`` on an instance, provide class-level ``keys()``, implement positional arguments, bump to v0.4.4 (`87c1b6f <https://github.com/autumnjolitz/instruct/commit/87c1b6f69e8eae34cbba97552227931b1558ab77>`_ by Autumn Jolitz).

Version `v0.4.3 <https://github.com/autumnjolitz/instruct/releases/tag/v0.4.3>`_
----------------------------------------------------------------------------------

Released 2020-01-06

`Compare with v0.4.2 <https://github.com/autumnjolitz/instruct/compare/v0.4.2...v0.4.3>`_ (3 commits since)

Performance Improvements

- at ``class ....`` definition time, track if the property type list **may** have a collection of ``Atomic`` descendants (allows one to check a mapping instead of type hints) (`ff812db <https://github.com/autumnjolitz/instruct/commit/ff812db57b5bc294fdfabd1495abd6d29457d111>`_ by Autumn Jolitz).

Tests

- functions for determining if it contains a collection/mapping of ``Atomic``-descendents in ``class ...`` definition (`95f79a5 <https://github.com/autumnjolitz/instruct/commit/95f79a5aeda698a135e1014b9c591f9549344e1d>`_ by Autumn Jolitz).

Other

- [about] 0.4.3 (`eb70a1c <https://github.com/autumnjolitz/instruct/commit/eb70a1cbb372ea072636ec349cc72d64e033c4d9>`_ by Autumn Jolitz).

Version `v0.4.2 <https://github.com/autumnjolitz/instruct/releases/tag/v0.4.2>`_
----------------------------------------------------------------------------------

Released 2019-10-13

`Compare with v0.4.1 <https://github.com/autumnjolitz/instruct/compare/v0.4.1...v0.4.2>`_ (2 commits since)

Features

- preserve original slots at ``_slots``, improve FrozenMapping interface, bump to v0.4.2 (`44ab8dc <https://github.com/autumnjolitz/instruct/commit/44ab8dcbaa239957ee63daee653d44956ed4c4a7>`_ by Autumn Jolitz).

Version `v0.4.1 <https://github.com/autumnjolitz/instruct/releases/tag/v0.4.1>`_
----------------------------------------------------------------------------------

Released 2019-10-13

`Compare with v0.4.0 <https://github.com/autumnjolitz/instruct/compare/v0.4.0...v0.4.1>`_ (1 commits since)

Bug Fixes

- restrict flatten to only merge list, tuple, generators, bump to v0.4.1 (`1d922a4 <https://github.com/autumnjolitz/instruct/commit/1d922a4c0492ea5c82d60f77c96ecd1d50d689c8>`_ by Autumn Jolitz).

Version `v0.4.0 <https://github.com/autumnjolitz/instruct/releases/tag/v0.4.0>`_
----------------------------------------------------------------------------------

Released 2019-09-18

`Compare with v0.3.8 <https://github.com/autumnjolitz/instruct/compare/v0.3.8...v0.4.0>`_ (1 commits since)

Features

- finer grained exceptions, support ``[]`` on properties, rename ``skip`` to ``dataclass``, impllement ability to handle property type violations with a handler function, bump to v0.4.0 (`15d26a5 <https://github.com/autumnjolitz/instruct/commit/15d26a5c23946b984c58e41fdcf0074bfb8b0594>`_ by Autumn Jolitz).

Version `v0.3.8 <https://github.com/autumnjolitz/instruct/releases/tag/v0.3.8>`_
----------------------------------------------------------------------------------

Released 2019-08-22

`Compare with v0.3.7 <https://github.com/autumnjolitz/instruct/compare/v0.3.7...v0.3.8>`_ (1 commits since)

Bug Fixes

- ``Mapping`` immutability on ``to_json``, enforce ``__coerce__`` constraints, bump to v0.3.8 (`a45e1b1 <https://github.com/autumnjolitz/instruct/commit/a45e1b152b687109e371fd40ab9c2fd83ab72321>`_ by Autumn Jolitz).

Version `v0.3.7 <https://github.com/autumnjolitz/instruct/releases/tag/v0.3.7>`_
----------------------------------------------------------------------------------

Released 2019-08-07

`Compare with v0.3.5 <https://github.com/autumnjolitz/instruct/compare/v0.3.5...v0.3.7>`_ (1 commits since)

Bug Fixes

- correct singular exception, bump to v0.3.7 (`103739b <https://github.com/autumnjolitz/instruct/commit/103739b25cc7118510b8603e0bceab7ad3a3e3f6>`_ by Autumn Jolitz).

Version `v0.3.5 <https://github.com/autumnjolitz/instruct/releases/tag/v0.3.5>`_
----------------------------------------------------------------------------------

Released 2019-08-07

`Compare with v0.3.4 <https://github.com/autumnjolitz/instruct/compare/v0.3.4...v0.3.5>`_ (2 commits since)

Features

- explicitly support ``Tuple[Type, ...]``, ``Dict[KeyType, ValueType]``, bump to v0.3.5 (`8903c5b <https://github.com/autumnjolitz/instruct/commit/8903c5b41f95d126d4cf07b7afdebaa7151fcb93>`_ by Autumn Jolitz).

Build

- add black (`3ed3a00 <https://github.com/autumnjolitz/instruct/commit/3ed3a004644196cfc23bd0739265474ed80e697e>`_ by Autumn Jolitz).

Version `v0.3.4 <https://github.com/autumnjolitz/instruct/releases/tag/v0.3.4>`_
----------------------------------------------------------------------------------

Released 2019-04-30

`Compare with v0.3.3 <https://github.com/autumnjolitz/instruct/compare/v0.3.3...v0.3.4>`_ (4 commits since)

Features

- support redefining properties on inherited members if explicitly called out, bump to v0.3.4 (`f60943f <https://github.com/autumnjolitz/instruct/commit/f60943f5bae8a508e2e3c53f6060f520ee17165d>`_ by Autumn Jolitz).

Chore

- pass type check in ````typedef.py```` (`d9ef56c <https://github.com/autumnjolitz/instruct/commit/d9ef56c622464aaf02a7fb63edbef711b6f5e25c>`_ by Autumn Jolitz).

Build

- add in hooks for `mypy <https://mypy.readthedocs.io/>`_ and `pytype <https://github.com/google/pytype>`_ (`0c0b526 <https://github.com/autumnjolitz/instruct/commit/0c0b5261d9413b41372f8b2331df1d7c2af098d3>`_ by Autumn Jolitz).
- add in defintions for type checkers (`8834579 <https://github.com/autumnjolitz/instruct/commit/88345798b081e82ab81d432dac58c11a4b4ef532>`_ by Autumn Jolitz).

Version `v0.3.3 <https://github.com/autumnjolitz/instruct/releases/tag/v0.3.3>`_
----------------------------------------------------------------------------------

Released 2019-04-22

`Compare with v0.3.2 <https://github.com/autumnjolitz/instruct/compare/v0.3.2...v0.3.3>`_ (3 commits since)

Chore

- add type hints (`0c7f6bb <https://github.com/autumnjolitz/instruct/commit/0c7f6bbb0df090ce501489103be792a191c85dc9>`_ by Autumn Jolitz).
- add project type hint definitions (`da3c079 <https://github.com/autumnjolitz/instruct/commit/da3c079ac3c036e0e6837761845cd3861e80bbe3>`_ by Autumn Jolitz).

Build

- bump to v0.3.3 (`0eb1781 <https://github.com/autumnjolitz/instruct/commit/0eb17817963ff028986ffadbd4d944a434b2891e>`_ by Autumn Jolitz).

Version `v0.3.2 <https://github.com/autumnjolitz/instruct/releases/tag/v0.3.2>`_
----------------------------------------------------------------------------------

Released 2019-03-19

`Compare with v0.3.1 <https://github.com/autumnjolitz/instruct/compare/v0.3.1...v0.3.2>`_ (1 commits since)

Bug Fixes

- support nested ``ClassCreationFailed``s, bump to v0.3.2 (`bbf15c7 <https://github.com/autumnjolitz/instruct/commit/bbf15c78060af699ba71f49cfd4e2356f86b0223>`_ by Autumn Jolitz).

Version `v0.3.1 <https://github.com/autumnjolitz/instruct/releases/tag/v0.3.1>`_
----------------------------------------------------------------------------------

Released 2019-03-09

`Compare with v0.3.0 <https://github.com/autumnjolitz/instruct/compare/v0.3.0...v0.3.1>`_ (1 commits since)

Features

- expose  ``_column_types`` for mixins, bump to v0.3.1 (`11636dc <https://github.com/autumnjolitz/instruct/commit/11636dc961171e539ed3edeeae1b933a1b1658e6>`_ by Autumn Jolitz).

Version `v0.3.0 <https://github.com/autumnjolitz/instruct/releases/tag/v0.3.0>`_
----------------------------------------------------------------------------------

Released 2019-02-11

`Compare with v0.2.7 <https://github.com/autumnjolitz/instruct/compare/v0.2.7...v0.3.0>`_ (1 commits since)

Bug Fixes

- renormalize the changes list, bump to v0.3.0 (`01c37b1 <https://github.com/autumnjolitz/instruct/commit/01c37b1a583617dd61536617b14ea96d3c83d1da>`_ by Autumn Jolitz).

Version `v0.2.7 <https://github.com/autumnjolitz/instruct/releases/tag/v0.2.7>`_
----------------------------------------------------------------------------------

Released 2019-02-06

`Compare with v0.2.6 <https://github.com/autumnjolitz/instruct/compare/v0.2.6...v0.2.7>`_ (1 commits since)

Features

- identify as a ``Mapping``, bump to v0.2.7 (`fe23126 <https://github.com/autumnjolitz/instruct/commit/fe2312652fc15c0503d166b8e6b857459710695d>`_ by Autumn Jolitz).

Version `v0.2.6 <https://github.com/autumnjolitz/instruct/releases/tag/v0.2.6>`_
----------------------------------------------------------------------------------

Released 2019-02-06

`Compare with v0.2.5 <https://github.com/autumnjolitz/instruct/compare/v0.2.5...v0.2.6>`_ (1 commits since)

Features

- add in a ``from_json`` top level helper, bump to v0.2.6 (`c57eb16 <https://github.com/autumnjolitz/instruct/commit/c57eb1676dd0ac22be35a525c4124dcf73e74281>`_ by Autumn Jolitz).

Version `v0.2.5 <https://github.com/autumnjolitz/instruct/releases/tag/v0.2.5>`_
----------------------------------------------------------------------------------

Released 2019-02-06

`Compare with v0.2.4 <https://github.com/autumnjolitz/instruct/compare/v0.2.4...v0.2.5>`_ (1 commits since)

Bug Fixes

- correct ``__qualname__`` for internal dataclasses, bump to v0.2.5 (`e611963 <https://github.com/autumnjolitz/instruct/commit/e61196348286909aada4cd14a9b2a7d5cfbecf2b>`_ by Autumn Jolitz).

Version `v0.2.4 <https://github.com/autumnjolitz/instruct/releases/tag/v0.2.4>`_
----------------------------------------------------------------------------------

Released 2019-02-06

`Compare with v0.2.3 <https://github.com/autumnjolitz/instruct/compare/v0.2.3...v0.2.4>`_ (3 commits since)

Bug Fixes

- correct ``__qualname__``, ``__module__`` on dataclass instances, bump to v0.2.4 (`f9c1362 <https://github.com/autumnjolitz/instruct/commit/f9c136207bd7858c21d4dda8f679e4571c6c8604>`_ by Autumn Jolitz).
- remove leading ``_`` (`6b2bfbb <https://github.com/autumnjolitz/instruct/commit/6b2bfbbbd4175fab0cf2471309f91679fc572293>`_ by Autumn Jolitz).

Tests

- verify JSON and mutable values (`a54d2a8 <https://github.com/autumnjolitz/instruct/commit/a54d2a89bdc22785bd3a01f8a83de35eb33a8268>`_ by Autumn Jolitz).

Version `v0.2.3 <https://github.com/autumnjolitz/instruct/releases/tag/v0.2.3>`_
----------------------------------------------------------------------------------

Released 2019-02-05

`Compare with v0.2.2 <https://github.com/autumnjolitz/instruct/compare/v0.2.2...v0.2.3>`_ (1 commits since)

Features

- assume immutable copies if possible, bump to v0.2.3 (`0767baf <https://github.com/autumnjolitz/instruct/commit/0767baf3aa63bcd4fb778ab9d5209bc68446c573>`_ by Autumn Jolitz).

Version `v0.2.2 <https://github.com/autumnjolitz/instruct/releases/tag/v0.2.2>`_
----------------------------------------------------------------------------------

Released 2019-02-04

`Compare with v0.2.1 <https://github.com/autumnjolitz/instruct/compare/v0.2.1...v0.2.2>`_ (1 commits since)

Features

- add class name into class creation failure message, bump to v0.2.2 (`789b948 <https://github.com/autumnjolitz/instruct/commit/789b948ca2104f3b9a5faafe6234e08ed9a91be1>`_ by Autumn Jolitz).

Version `v0.2.1 <https://github.com/autumnjolitz/instruct/releases/tag/v0.2.1>`_
----------------------------------------------------------------------------------

Released 2019-02-04

`Compare with v0.2.0 <https://github.com/autumnjolitz/instruct/compare/v0.2.0...v0.2.1>`_ (2 commits since)

Features

- use the ``globals()`` for overridden props from ``__module__`` (`f61e851 <https://github.com/autumnjolitz/instruct/commit/f61e851c62d0b8094788d8203c75996b1332c155>`_ by Autumn Jolitz).

Build

- bump to v0.2.1 (`bc4d30c <https://github.com/autumnjolitz/instruct/commit/bc4d30cd85bb6ecfe264fdfd82f30a43fc7e884d>`_ by Autumn Jolitz).

Version `v0.2.0 <https://github.com/autumnjolitz/instruct/releases/tag/v0.2.0>`_
----------------------------------------------------------------------------------

Released 2019-02-04

`Compare with v0.1.1 <https://github.com/autumnjolitz/instruct/compare/v0.1.1...v0.2.0>`_ (4 commits since)

Features

- use `_{key}_` for internal access (`d647e21 <https://github.com/autumnjolitz/instruct/commit/d647e21df66fdd62e66c0f0988458140d516c3f1>`_ by Autumn Jolitz).
- rename the internal of ``_raw_{key}`` to ``_{key}_``, fix up ``__class__`` reference for argless ``super()`` calls (`2690415 <https://github.com/autumnjolitz/instruct/commit/26904151e860bff27d128bbce32b23e6f4fb6ff8>`_ by Autumn Jolitz).

Tests

- add test for ``clear()`` (`573c535 <https://github.com/autumnjolitz/instruct/commit/573c535db80dad143ca40da9a6f61f4844be6c36>`_ by Autumn Jolitz).

Build

- bump to v0.2.0 (`4d376a4 <https://github.com/autumnjolitz/instruct/commit/4d376a4e1fd8bfb15663489e4b51df196641ebcf>`_ by Autumn Jolitz).

Version `v0.1.1 <https://github.com/autumnjolitz/instruct/releases/tag/v0.1.1>`_
----------------------------------------------------------------------------------

Released 2019-02-01

`Compare with v0.1.0 <https://github.com/autumnjolitz/instruct/compare/v0.1.0...v0.1.1>`_ (1 commits since)

Bug Fixes

- remove errant debug print, bump to v0.1.1 (`8ef5e5e <https://github.com/autumnjolitz/instruct/commit/8ef5e5e0e2372e723ba0a16f88f050e6ab9fe395>`_ by Autumn Jolitz).

Version `v0.1.0 <https://github.com/autumnjolitz/instruct/releases/tag/v0.1.0>`_
----------------------------------------------------------------------------------

Released 2019-02-01

`Compare with v0.0.21 <https://github.com/autumnjolitz/instruct/compare/v0.0.21...v0.1.0>`_ (1 commits since)

Features

- support 1-level ``Iterable[Base]`` -> ``JSON``, hooks, better pickling, ``__setitem__`` on class, bump to v0.1.0 (`2f0feea <https://github.com/autumnjolitz/instruct/commit/2f0feeacadee6760f77a154f79ba6b63f4dd51ac>`_ by Autumn Jolitz).

Version `v0.0.21 <https://github.com/autumnjolitz/instruct/releases/tag/v0.0.21>`_
------------------------------------------------------------------------------------

Released 2018-12-19

`Compare with v0.0.20 <https://github.com/autumnjolitz/instruct/compare/v0.0.20...v0.0.21>`_ (1 commits since)

Tests

- more tests, bump to v0.0.21 (`52a75e6 <https://github.com/autumnjolitz/instruct/commit/52a75e67fd19c6f2ce64ccf2a84695f66f8dad91>`_ by Autumn Jolitz).

Version `v0.0.20 <https://github.com/autumnjolitz/instruct/releases/tag/v0.0.20>`_
------------------------------------------------------------------------------------

Released 2018-12-19

`Compare with v0.0.19 <https://github.com/autumnjolitz/instruct/compare/v0.0.19...v0.0.20>`_ (1 commits since)

Features

- track coerce types, bump to v0.0.20 (`a5c96ca <https://github.com/autumnjolitz/instruct/commit/a5c96cae29ae08982a0d86b2ba7c4755c4195f2a>`_ by Autumn Jolitz).

Version `v0.0.19 <https://github.com/autumnjolitz/instruct/releases/tag/v0.0.19>`_
------------------------------------------------------------------------------------

Released 2018-12-19

`Compare with v0.0.18 <https://github.com/autumnjolitz/instruct/compare/v0.0.18...v0.0.19>`_ (2 commits since)

Features

- support nested List better, bump to v0.0.19 (`9f48c95 <https://github.com/autumnjolitz/instruct/commit/9f48c959b2f095352699441df136ffbdf25c0caf>`_ by Autumn Jolitz).

Tests

- fix test atomic (`10a7e56 <https://github.com/autumnjolitz/instruct/commit/10a7e56a802ec14ac75554e3fcd0de1f99668c30>`_ by Autumn Jolitz).

Version `v0.0.18 <https://github.com/autumnjolitz/instruct/releases/tag/v0.0.18>`_
------------------------------------------------------------------------------------

Released 2018-12-19

`Compare with v0.0.17 <https://github.com/autumnjolitz/instruct/compare/v0.0.17...v0.0.18>`_ (3 commits since)

Bug Fixes

- error on generics, support nested lists, bump to v0.0.18 (`96582de <https://github.com/autumnjolitz/instruct/commit/96582de0696f95151d05d6bb8ee657db86bee914>`_ by Autumn Jolitz).

Chore

- ignore python/ venv and .pytest_cache (`4ab0a70 <https://github.com/autumnjolitz/instruct/commit/4ab0a70f03d0c05a9b6c44d19a2c6f6368574360>`_ by Autumn Jolitz).
- remove inaccurate ``setup.cfg`` (`6709054 <https://github.com/autumnjolitz/instruct/commit/67090547b4b8d5e3e1cf7d3ab5da698f1398a90b>`_ by Autumn Jolitz).

Version `v0.0.17 <https://github.com/autumnjolitz/instruct/releases/tag/v0.0.17>`_
------------------------------------------------------------------------------------

Released 2018-12-14

`Compare with v0.0.16 <https://github.com/autumnjolitz/instruct/compare/v0.0.16...v0.0.17>`_ (1 commits since)

Bug Fixes

- fix type message, bump to v0.0.17 (`ded8a9c <https://github.com/autumnjolitz/instruct/commit/ded8a9cb98794868361a4415f3452ccba57e7bc7>`_ by Autumn Jolitz).

Version `v0.0.16 <https://github.com/autumnjolitz/instruct/releases/tag/v0.0.16>`_
------------------------------------------------------------------------------------

Released 2018-12-13

`Compare with v0.0.15 <https://github.com/autumnjolitz/instruct/compare/v0.0.15...v0.0.16>`_ (1 commits since)

Features

- fix history truncation, bump to v0.0.16 (`e18a73c <https://github.com/autumnjolitz/instruct/commit/e18a73c62b460bfb169932ba47806c23e4153579>`_ by Autumn Jolitz).

Version `v0.0.15 <https://github.com/autumnjolitz/instruct/releases/tag/v0.0.15>`_
------------------------------------------------------------------------------------

Released 2018-12-13

`Compare with v0.0.14 <https://github.com/autumnjolitz/instruct/compare/v0.0.14...v0.0.15>`_ (1 commits since)

Bug Fixes

- support correct property accounting (`431742d <https://github.com/autumnjolitz/instruct/commit/431742dc7f6761231f7ccf3f0c5ffbb32ed04ea3>`_ by Autumn Jolitz).

Version `v0.0.14 <https://github.com/autumnjolitz/instruct/releases/tag/v0.0.14>`_
------------------------------------------------------------------------------------

Released 2018-12-13

`Compare with v0.0.13 <https://github.com/autumnjolitz/instruct/compare/v0.0.13...v0.0.14>`_ (1 commits since)

Features

- now with better type names, bump to v0.0.14 (`9a1994f <https://github.com/autumnjolitz/instruct/commit/9a1994f6a2056b90e59495d34af3ae3f79f877e5>`_ by Autumn Jolitz).

Version `v0.0.13 <https://github.com/autumnjolitz/instruct/releases/tag/v0.0.13>`_
------------------------------------------------------------------------------------

Released 2018-12-12

`Compare with v0.0.12 <https://github.com/autumnjolitz/instruct/compare/v0.0.12...v0.0.13>`_ (1 commits since)

Features

- index properties onto the class, bump to v0.0.13 (`aabef91 <https://github.com/autumnjolitz/instruct/commit/aabef91bb95ac3885d45f3ce341ee0961ff1a0c5>`_ by Autumn Jolitz).

Version `v0.0.12 <https://github.com/autumnjolitz/instruct/releases/tag/v0.0.12>`_
------------------------------------------------------------------------------------

Released 2018-12-12

`Compare with v0.0.11 <https://github.com/autumnjolitz/instruct/compare/v0.0.11...v0.0.12>`_ (1 commits since)

Features

- supports overrideable type errors, bump version to v0.0.12 (`2b7746a <https://github.com/autumnjolitz/instruct/commit/2b7746ab0b6556de97ac0cdea0e8f3498044b9f6>`_ by Autumn Jolitz).

Version `v0.0.11 <https://github.com/autumnjolitz/instruct/releases/tag/v0.0.11>`_
------------------------------------------------------------------------------------

Released 2018-12-11

`Compare with v0.0.10 <https://github.com/autumnjolitz/instruct/compare/v0.0.10...v0.0.11>`_ (1 commits since)

Bug Fixes

- Correct bug in class keyword argument ``fast=True``, bump version to v0.0.11 (`eb7e57f <https://github.com/autumnjolitz/instruct/commit/eb7e57fccc817430072e2b384f690c27ec3116b7>`_ by Autumn Jolitz).

Version `v0.0.10 <https://github.com/autumnjolitz/instruct/releases/tag/v0.0.10>`_
------------------------------------------------------------------------------------

Released 2018-12-11

`Compare with v0.0.9 <https://github.com/autumnjolitz/instruct/compare/v0.0.9...v0.0.10>`_ (1 commits since)

Features

- add in ``**mapping`` support (`e07105e <https://github.com/autumnjolitz/instruct/commit/e07105e98c71ca9b3e4cd84a988cecbc33edecf9>`_ by Autumn Jolitz).

Version `v0.0.9 <https://github.com/autumnjolitz/instruct/releases/tag/v0.0.9>`_
----------------------------------------------------------------------------------

Released 2018-12-11

`Compare with v0.0.8 <https://github.com/autumnjolitz/instruct/compare/v0.0.8...v0.0.9>`_ (1 commits since)

Code Refactoring

- restructure and introduce better naming (`99e1ae8 <https://github.com/autumnjolitz/instruct/commit/99e1ae812e441e7edd124947280e7018bcd3882b>`_ by Autumn Jolitz).

Version `v0.0.8 <https://github.com/autumnjolitz/instruct/releases/tag/v0.0.8>`_
----------------------------------------------------------------------------------

Released 2018-12-11

`Compare with v0.0.7 <https://github.com/autumnjolitz/instruct/compare/v0.0.7...v0.0.8>`_ (1 commits since)

Features

- Support generation of custom types to match requirements (`a1a5643 <https://github.com/autumnjolitz/instruct/commit/a1a5643f5dd64bec2ec1b5da6649920b592d7975>`_ by Autumn Jolitz).

Version `v0.0.7 <https://github.com/autumnjolitz/instruct/releases/tag/v0.0.7>`_
----------------------------------------------------------------------------------

Released 2018-12-10

`Compare with v0.0.6 <https://github.com/autumnjolitz/instruct/compare/v0.0.6...v0.0.7>`_ (1 commits since)

Bug Fixes

- restore ``__hash__`` to data classes (`0e9ef2b <https://github.com/autumnjolitz/instruct/commit/0e9ef2b7dc7261b16a764774aead2ccce747317a>`_ by Autumn Jolitz).

Version `v0.0.6 <https://github.com/autumnjolitz/instruct/releases/tag/v0.0.6>`_
----------------------------------------------------------------------------------

Released 2018-12-10

`Compare with v0.0.5 <https://github.com/autumnjolitz/instruct/compare/v0.0.5...v0.0.6>`_ (1 commits since)

Features

- make it possible to get the parent support class (`9088c1f <https://github.com/autumnjolitz/instruct/commit/9088c1fde075e485dc4e68b3ea0031e62954a39f>`_ by Autumn Jolitz).

Version `v0.0.5 <https://github.com/autumnjolitz/instruct/releases/tag/v0.0.5>`_
----------------------------------------------------------------------------------

Released 2018-12-10

`Compare with v0.0.4 <https://github.com/autumnjolitz/instruct/compare/v0.0.4...v0.0.5>`_ (1 commits since)

Features

- Python 3.7 focus (`d32a4e9 <https://github.com/autumnjolitz/instruct/commit/d32a4e94eb19dcff94cc2055a9e3a124fdb2ca1a>`_ by Autumn Jolitz).

Version `v0.0.4 <https://github.com/autumnjolitz/instruct/releases/tag/v0.0.4>`_
----------------------------------------------------------------------------------

Released 2018-12-10

`Compare with v0.0.3 <https://github.com/autumnjolitz/instruct/compare/v0.0.3...v0.0.4>`_ (2 commits since)

Features

- allow use of ``type`` as a attribute name (`8d91b48 <https://github.com/autumnjolitz/instruct/commit/8d91b4852a02289649bf3ee7f8cdf5147820ab3b>`_ by Autumn Jolitz).

Chore

- bump version (`3848f59 <https://github.com/autumnjolitz/instruct/commit/3848f590a88919cc494dba9dce7973e2eed62335>`_ by Autumn Jolitz).

Version `v0.0.3 <https://github.com/autumnjolitz/instruct/releases/tag/v0.0.3>`_
----------------------------------------------------------------------------------

Released 2018-12-10

`Compare with v0.0.2 <https://github.com/autumnjolitz/instruct/compare/v0.0.2...v0.0.3>`_ (1 commits since)

Build

- this is not a universal build (`1e3bab8 <https://github.com/autumnjolitz/instruct/commit/1e3bab8031b710c8bc33507cab3a23858056ace7>`_ by Autumn Jolitz).

Version `v0.0.2 <https://github.com/autumnjolitz/instruct/releases/tag/v0.0.2>`_
----------------------------------------------------------------------------------

Released 2018-12-10

`Compare with v0.0.1 <https://github.com/autumnjolitz/instruct/compare/v0.0.1...v0.0.2>`_ (1 commits since)

Features

- updates for Python 3.7 (`0ed83ef <https://github.com/autumnjolitz/instruct/commit/0ed83efcbae0bbed31f3b17f5bedd8c32576e94c>`_ by Autumn Jolitz).

Version `v0.0.1 <https://github.com/autumnjolitz/instruct/releases/tag/v0.0.1>`_
----------------------------------------------------------------------------------

Released 2018-12-09

`Compare with first commit <https://github.com/autumnjolitz/instruct/compare/3d80b09739f780ebaa60a85583b615805277cab3...v0.0.1>`_ (20 commits since)

Features

- update for Python 3.6 (`004caba <https://github.com/autumnjolitz/instruct/commit/004caba2f07c3cdc411ce2d910e6155f0a69121f>`_ by Autumn Jolitz).
- Add JSON, pickle, and coercion (allows casting from ``N`` types to an appropriate type) (`8fe8aa2 <https://github.com/autumnjolitz/instruct/commit/8fe8aa2c581031d93791938c073d02c7979baac0>`_ by Autumn Jolitz).
- Add field linkages (`9531dad <https://github.com/autumnjolitz/instruct/commit/9531dad9fc9e9287148a09f91061453ee8b4a827>`_ by Autumn Jolitz).
- Support multiple inheritance, optimize edge classes (`2d7a4fa <https://github.com/autumnjolitz/instruct/commit/2d7a4fa34747407af008c168e895aca1b607be34>`_ by Autumn Jolitz).
- Use Jinja to handle the macro-work (`487fa3d <https://github.com/autumnjolitz/instruct/commit/487fa3de98896a203a9d58904bf75e9fbf29c784>`_ by Autumn Jolitz).
- Optimize through use of ``__new__`` to seed vital fields ahead of time (`48f29d3 <https://github.com/autumnjolitz/instruct/commit/48f29d331da00cda1cfed8d50a4ca1ccdb035d86>`_ by Autumn Jolitz).
- Support derived embedded classes and duck-eqing them (`b514f07 <https://github.com/autumnjolitz/instruct/commit/b514f0721de47be00153c54f535006727f1f1805>`_ by Autumn Jolitz).
- Flush out an idea (`3d80b09 <https://github.com/autumnjolitz/instruct/commit/3d80b09739f780ebaa60a85583b615805277cab3>`_ by Autumn Jolitz).

Performance Improvements

- Increase performance through codegen of constant structural cases (`f51acac <https://github.com/autumnjolitz/instruct/commit/f51acac3d8c68a5d0a3dd6021de0ef55aa8a3d81>`_ by Autumn Jolitz).

Bug Fixes

- bugfixes (`7803843 <https://github.com/autumnjolitz/instruct/commit/7803843896c0867753e0b33626f67d3ccddf0017>`_ by Autumn Jolitz).

Docs

- update (`24ad8fd <https://github.com/autumnjolitz/instruct/commit/24ad8fd9f61b2d644e25dcdbdb8a7c5104b6dcc4>`_ by Autumn Jolitz).
- update intent (`9ecfb23 <https://github.com/autumnjolitz/instruct/commit/9ecfb23f9cf0893edd6e183c7ad91123c5819d26>`_ by Autumn Jolitz).
- Add docs (`d0fb82c <https://github.com/autumnjolitz/instruct/commit/d0fb82cebe5b2dfc2ac790347878b6175f6f60f7>`_ by Autumn Jolitz).
- Log performance (`efe710a <https://github.com/autumnjolitz/instruct/commit/efe710ae29452604278c3af79e90d1fdc157c790>`_ by Autumn Jolitz).
- Log my approach (`d6972e8 <https://github.com/autumnjolitz/instruct/commit/d6972e8da542d7841b2e0d5ff4af92e110c31bea>`_ by Autumn Jolitz).

Dependencies

- add pytest dependency (`7b1022a <https://github.com/autumnjolitz/instruct/commit/7b1022abb2cfc70b3725625b2109abe6b36a590d>`_ by Autumn Jolitz).

Tests

- add test for the readme (`ce75dfd <https://github.com/autumnjolitz/instruct/commit/ce75dfd7f2fdac9615e5751b4286aa631dc84a7d>`_ by Autumn Jolitz).

Chore

- Delete unused code (`93e8791 <https://github.com/autumnjolitz/instruct/commit/93e87911b7065f7438d187d942e5994a196f73d0>`_ by Autumn Jolitz).

Build

- initial release of just the object structure (`9c43431 <https://github.com/autumnjolitz/instruct/commit/9c4343143b53efeefbeb8d8b28b01b524a6e1cdf>`_ by Autumn Jolitz).
