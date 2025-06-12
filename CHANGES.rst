.. |Changes|
Version `v0.8.6 <https://github.com/autumnjolitz/instruct/releases/tag/v0.8.6>`_
----------------------------------------------------------------------------------

Released 2025-06-12

`Compare with first commit <https://github.com/autumnjolitz/instruct/compare/4fff08f31c4d556852deb0e2b309c2a95da0e62b...v0.8.6>`_ (300 commits since)

Features

- add ``AutoRepr`` (aka ``autorepr=True``) (`f6bfd79 <https://github.com/autumnjolitz/instruct/commit/f6bfd7975443ae93751ae3bbc9b480ba9840c7a1>`_ by Autumn).

Bug Fixes

- correct type hint errors (`5e3c4af <https://github.com/autumnjolitz/instruct/commit/5e3c4af1e4ff18edb32a5c3bf005d21eb9b0a410>`_ by Autumn).
- only call ``exception.as_json`` when encountering ``Exception`` (if the stack is expanded from item that has ``.errors``, it will already have JSONable items) (`eaae147 <https://github.com/autumnjolitz/instruct/commit/eaae147435cd3df529a9aabd6c96b701b7b03b37>`_ by Autumn).
- avoid exposing ``NoIterable`` fields via ``keys()``, ``items()`` (`8f58520 <https://github.com/autumnjolitz/instruct/commit/8f58520260fc9b1894a3a2a99ed126e4158ce9a1>`_ by Autumn).
- correct syntax error when no effective fields (may occur if all fields are ``Annotated[..., NoIterable]``) (`a2910ec <https://github.com/autumnjolitz/instruct/commit/a2910ec2b7710fb4e9b34a5b2dbe0f84a648e30c>`_ by Autumn).
- satisfy both mypy and ruff for ``TypingDefinition`` (`331e3b5 <https://github.com/autumnjolitz/instruct/commit/331e3b558573d19de6904b27c436f4ee89300302>`_ by Autumn).
- apply ``pre-commit`` to all files (`2491adf <https://github.com/autumnjolitz/instruct/commit/2491adfbf7b858fa64208df614238e530fcde004>`_ by Autumn).
- satisfy mypy (`a6e5f21 <https://github.com/autumnjolitz/instruct/commit/a6e5f219365dd451db7e4f1b8054fcc992efae17>`_ by Autumn).
- ValidationError should operate on ``.errors`` as it is ``list[Exception] | tuple[Exception, ...]`` (`5d1d8eb <https://github.com/autumnjolitz/instruct/commit/5d1d8eb535d6382bdec804f1880b902b1325f725>`_ by Autumn).
- adjust ``copy_with`` to attempt to use ``__class_getitem__`` as the fallback (`cf734c6 <https://github.com/autumnjolitz/instruct/commit/cf734c619c5c59f619fa0507cb3f41c16514b094>`_ by Autumn).
- correct subtype generation for 3.10+ ``types.UnionType``s (`786bde4 <https://github.com/autumnjolitz/instruct/commit/786bde40a1e6338082f928872500516532e8ece4>`_ by Autumn).
- add ``mode`` to benchmarking, refactor slightly (`e14fa21 <https://github.com/autumnjolitz/instruct/commit/e14fa213b955c28d2c5209ede1a81b6930b4866a>`_ by Autumn).
- ``fast=True`` now supports all event listener forms (`f5d61d8 <https://github.com/autumnjolitz/instruct/commit/f5d61d8cfe0e3e6e8fb8cb89494aba2ce79d070b>`_ by Autumn).
- ``__main__`` now can run benchmark again (`0874e69 <https://github.com/autumnjolitz/instruct/commit/0874e6982574325051b34c6eb2f2fc697686b81f>`_ by Autumn).
- handle fixed tuples correctly (`2858fe1 <https://github.com/autumnjolitz/instruct/commit/2858fe13ea3c1a774d4242f3bc6d4294bca3ae49>`_ by Autumn).
- use ``types.CodeType.replace(...)`` when available (`7d1f632 <https://github.com/autumnjolitz/instruct/commit/7d1f632612114b8b9e062c72684a18455994f1a6>`_ by Autumn).
- avoid raising an exception inside testing tuple structure for a custom type (`b0dab54 <https://github.com/autumnjolitz/instruct/commit/b0dab547b98e6271998de9753e70c95773155eb0>`_ by Autumn).
- exceptions will not list the stack in a json output (`3be4874 <https://github.com/autumnjolitz/instruct/commit/3be4874ef8783e1ad7737fb25b1d76c9a170f5ed>`_ by Autumn).
- utils for 3.7 cannot specialize the ``WeakKeyDictionary``, so guard behind TYPE_CHECKING (`ff72191 <https://github.com/autumnjolitz/instruct/commit/ff72191a4ae019308cd5d296f9480571f4060b39>`_ by Autumn).
- satisfy type checker for non-3.12 (`45509ef <https://github.com/autumnjolitz/instruct/commit/45509efd3c6b8f2f5443aca7a1a031526ad60a2e>`_ by Autumn).
- added type hint for exceptions ``__json__`` method (`202007f <https://github.com/autumnjolitz/instruct/commit/202007f9f79f073ce6302bb6ea118095bbc63eb8>`_ by Autumn).
- ignore mypy error from an attribute test (`2ff96cf <https://github.com/autumnjolitz/instruct/commit/2ff96cf07e716542c657a3817beb1267d74bbee3>`_ by Autumn).
- tests post refactor (`ca7e140 <https://github.com/autumnjolitz/instruct/commit/ca7e140faa7907b13ee2a01c282af00687fd3b33>`_ by Autumn).
- add git changelog helper (`0bfa2b3 <https://github.com/autumnjolitz/instruct/commit/0bfa2b38100ef294996411a7574453dabb52902c>`_ by Autumn Jolitz).

Code Refactoring

- add type hints, restructure to be more specific (`b2467a2 <https://github.com/autumnjolitz/instruct/commit/b2467a20c51c8e83140e59f5baa3f82a110583ae>`_ by Autumn).

Other

- feature: implement simple ``type alias = hint`` (3.12+) (`9e81459 <https://github.com/autumnjolitz/instruct/commit/9e814591f0b159c5a2e710d0e9edcacb983d1597>`_ by Autumn).
- remove: pytype overlay as it is not used (`06d06f7 <https://github.com/autumnjolitz/instruct/commit/06d06f7797612a52e90491fbc693e1488e2f9a5f>`_ by Autumn).
- change: ``instruct/about.py`` will be structured for tuple comparisions like ``>= (0, 8, 0)`` (`413ab7b <https://github.com/autumnjolitz/instruct/commit/413ab7b818aa90f531b97df3b9f4cc6e0cefd4ea>`_ by Autumn).
- [CURRENT_VERSION] prerelease 0.8.0a0 (`5276173 <https://github.com/autumnjolitz/instruct/commit/5276173c8b0f5cc5cf98f1ea02a5ce01911b5d55>`_ by Autumn).
- [*] up version, remove unused imports, add to README (`d8953f0 <https://github.com/autumnjolitz/instruct/commit/d8953f08630848b8b01a696f9b4456f2fcbcd89f>`_ by Autumn).
- [*] refactor ``IAtomic`` -> ``AbstractAtomic``, ``AtomicImpl`` -> ``BaseAtomic`` (`6934d2e <https://github.com/autumnjolitz/instruct/commit/6934d2e6f59ce9647da24ad0c15335e13dd8035d>`_ by Autumn).
- [generate_version] fix to pass black (the pre version had a single quote ``'``) (`0df4031 <https://github.com/autumnjolitz/instruct/commit/0df4031cac8f64261f752517b04eea19bfe53a63>`_ by Autumn).
- [workflows.build] express the version (`7ad2555 <https://github.com/autumnjolitz/instruct/commit/7ad2555c551040dd2216e98e889ac349b9c7be91>`_ by Autumn).
- [CURRENT_VERSION] bump to 0.8.0 series (`edd0714 <https://github.com/autumnjolitz/instruct/commit/edd071460d3fcde292ea6ced132a0cf23991b963>`_ by Autumn).
- [typing] satisfy mypy for NoDefault (`7e73b1b <https://github.com/autumnjolitz/instruct/commit/7e73b1b92b33a70bd46514e533e2c005f3057887>`_ by Autumn).
- [*] use ``getattr_static`` more aggressively (`b298f29 <https://github.com/autumnjolitz/instruct/commit/b298f299403375a5b7dea46267fa4de2889b81c5>`_ by Autumn).
- [constants] add ``Undefined`` (`c38a586 <https://github.com/autumnjolitz/instruct/commit/c38a586a6e87029fce20db07de82e72bc24f5b74>`_ by Autumn).
- [*] pass 3.12 tests (`063cb46 <https://github.com/autumnjolitz/instruct/commit/063cb468a5397cb60d930ef486d81583d9d63614>`_ by Autumn).
- [typing] check for NoDefault (`d639708 <https://github.com/autumnjolitz/instruct/commit/d63970879e5a6e71498b616326662f9e6ce1fd93>`_ by Autumn).
- [*] silence mypy with an ignore (`6a75246 <https://github.com/autumnjolitz/instruct/commit/6a752467724ecebcb943bfa7e04cca4993198a9d>`_ by Autumn).
- [dev-requirements] fix version (`52d3f3d <https://github.com/autumnjolitz/instruct/commit/52d3f3ddbda4e942c33da1e64cdfd7b9d3c4c371>`_ by Autumn).
- [*] default initialize untyped generics to ``Any`` (`8859af0 <https://github.com/autumnjolitz/instruct/commit/8859af0bcf24e14a57a4282d34515ed5f57de4e9>`_ by Autumn).
- [*] pass mypy (`63fb78c <https://github.com/autumnjolitz/instruct/commit/63fb78c91274fd0676bb9b55bf55a737b6f9bcbe>`_ by Autumn).
- [*] all backport (`a209547 <https://github.com/autumnjolitz/instruct/commit/a209547c8c9d99b6011c5a33217066987b877b22>`_ by Autumn).
- [*] backport some more (`23575b4 <https://github.com/autumnjolitz/instruct/commit/23575b4a031a55fcd4395f76787068b5bd3556a4>`_ by Autumn).
- [*] copy from bugfix/master/relax-restrictions (`a07b145 <https://github.com/autumnjolitz/instruct/commit/a07b1456708fd6c64b3b6d5cba03b4e9deb21fd2>`_ by Autumn).
- [*] rename ``Atomic`` -> ``AtomicMeta`` (`5c06eb0 <https://github.com/autumnjolitz/instruct/commit/5c06eb09f73bb96672f320dc5fe35c08653aa28f>`_ by Autumn).
- [*] support generics (`445b247 <https://github.com/autumnjolitz/instruct/commit/445b247cef68fcf6696e7f7fc96cd711a411b8e6>`_ by Autumn).
- [typedef] fix typo (`d630b66 <https://github.com/autumnjolitz/instruct/commit/d630b669f1ccc073527e81b7ceacb89919e921f1>`_ by Autumn).
- [typedef] fix for 3.7 (`c42bfba <https://github.com/autumnjolitz/instruct/commit/c42bfba44f2497becb9cb94a9010032a4ebbc90f>`_ by Autumn).
- [CURRENT_VERSION] bump (`3a2c0f5 <https://github.com/autumnjolitz/instruct/commit/3a2c0f55e2b3ba084f58258392cd9b02cea15c88>`_ by Autumn).
- [typedef] support ``type | type`` in 3.10+ and ``__init_subclass__`` (`953e38f <https://github.com/autumnjolitz/instruct/commit/953e38f75432011a5cf24b6509ae2ffcb5542bb3>`_ by Autumn).
- [README] try to make more friendly for github (`70827c9 <https://github.com/autumnjolitz/instruct/commit/70827c935be0612fa2925f93a0f56c618724429c>`_ by Autumn Jolitz).
- [CHANGES, README] update (`0ef72af <https://github.com/autumnjolitz/instruct/commit/0ef72afb765a00adfc3116d6c5e97229d1ddb124>`_ by Autumn Jolitz).
- [CHANGES.rst] template it (`bc98325 <https://github.com/autumnjolitz/instruct/commit/bc98325e79d04f983dab3427b94db2c86ec545cc>`_ by Autumn Jolitz).
- [CHANGES] investigate use of git-changelog (`fe037df <https://github.com/autumnjolitz/instruct/commit/fe037df3eb7a0b051adbafca317729f8394cafaa>`_ by Autumn Jolitz).
- [.github] mess with development one (`57bca7b <https://github.com/autumnjolitz/instruct/commit/57bca7b3bfdf7bcad784c60faae63909482e6278>`_ by Autumn Jolitz).
- [*] refactor build, add invoke interface as my makefile (`8b4aee7 <https://github.com/autumnjolitz/instruct/commit/8b4aee704636753794feadedebab7edc26171040>`_ by Autumn Jolitz).
- [README] add badges (`308fb88 <https://github.com/autumnjolitz/instruct/commit/308fb883c68984b6abaa14a731403e3c495395f7>`_ by Autumn).
- [release] test before upload (`534ebcc <https://github.com/autumnjolitz/instruct/commit/534ebcc50db71831e1a45e3103462699f753abb1>`_ by Autumn).
- [0.7.3.post1] bump version for pypi (`546ad9a <https://github.com/autumnjolitz/instruct/commit/546ad9a522c022952a3d6167ecaa0d86e94fd725>`_ by Autumn).
- [*] Port instruct to newer Python versions (#3) (`eefcab5 <https://github.com/autumnjolitz/instruct/commit/eefcab5f27c9889c86975d85d9253f14fb4576cf>`_ by Autumn Jolitz).
- [0.7.3] unlock versions to be more flexible (`5e7be6c <https://github.com/autumnjolitz/instruct/commit/5e7be6c406da35bc37daa5ecb8bb9643a4c53c08>`_ by Autumn).
- [README] add notes on use of ``Range`` and friends (`a50832c <https://github.com/autumnjolitz/instruct/commit/a50832c428d60b1758ab32f011e2a0fb4e6eb180>`_ by Autumn).
- [__init__] add ``RangeFlags`` to export (`b24a75a <https://github.com/autumnjolitz/instruct/commit/b24a75aa2dc0c4849b9cf44d04d561fbf4eb1aea>`_ by Autumn).
- [test_atomic] use ``_set_defaults``  instead (`8a1a48d <https://github.com/autumnjolitz/instruct/commit/8a1a48d4204d0199328bd41231fa412eca0c3a6c>`_ by Autumn).
- [README] add comparison between instruct and pydantic (`40adafd <https://github.com/autumnjolitz/instruct/commit/40adafd902614c012a9fc4cb8fc907a63732624c>`_ by Autumn).
- [*] add dummy ``__iter__`` to handle empty class case (`ef14e06 <https://github.com/autumnjolitz/instruct/commit/ef14e06274ecf9a051185c87a4c73a0dab295538>`_ by Autumn).
- [CHANGES] document (`b3758e2 <https://github.com/autumnjolitz/instruct/commit/b3758e2f995b7ffa7918105fb49c24b947ea7ea2>`_ by Autumn).
- [test_atomic] add more tests (`792f838 <https://github.com/autumnjolitz/instruct/commit/792f838eb1d437a78a5aab5d447c49bfea2f728b>`_ by Autumn).
- [__init__] remove fast new in favor of calling ``_set_defaults`` (`c968c22 <https://github.com/autumnjolitz/instruct/commit/c968c22b29a68a6eaac8d0ad04e717b1a4645d37>`_ by Autumn).
- [__init__] export ``clear``, ``reset_to_defaults``, make `_set_defaults` first call the zero-init version, then cascade through the inheritance tree for any overrides, add default functions for empty classes, use ``__public_class__`` for ``public_class`` calls (`557fa1f <https://github.com/autumnjolitz/instruct/commit/557fa1f155d73ae7846b0e7fbf40b1460e16886c>`_ by Autumn).
- [about] 0.7.1 (`0e66380 <https://github.com/autumnjolitz/instruct/commit/0e663807ddb1a00210c5b229118c73b13a5217c3>`_ by Autumn).
- [__main__] remove unused import (`723ce32 <https://github.com/autumnjolitz/instruct/commit/723ce32d3f7fe888fc410630cb2582108739814c>`_ by Autumn).
- [setup] add `devel` extras (`d5362c5 <https://github.com/autumnjolitz/instruct/commit/d5362c51b84aed4ef60d653bd300ca6565194e5c>`_ by Autumn).
- [workflows] check style (`0ae6a76 <https://github.com/autumnjolitz/instruct/commit/0ae6a769465b79a3b2206d5a2704543d8954b873>`_ by Autumn).
- [README, CHANGES] update README, add a CHANGES file (`3bbdb84 <https://github.com/autumnjolitz/instruct/commit/3bbdb84bd1230de100ca2e5d385d05ed362d6461>`_ by Autumn).
- [about] bump to 0.7.0 (`06accaa <https://github.com/autumnjolitz/instruct/commit/06accaaf37d93562ae0ce7f375ddd6d45d7270bb>`_ by Autumn).
- [setup] bump jinja2 and typing_extensions versions (`51496d4 <https://github.com/autumnjolitz/instruct/commit/51496d44b4683a970a28f031a513a4228af627fa>`_ by Autumn).
- [test_atomic] add additional tests (`ec7b087 <https://github.com/autumnjolitz/instruct/commit/ec7b087a3d03dde230c07c1bbeca1c3bf23014f8>`_ by Autumn).
- [__init__] spider annotations, use the ``NoPickle`` et al constants to influence class behavior (`dc135b3 <https://github.com/autumnjolitz/instruct/commit/dc135b3929ea6091f63eb7a1a10da58c7646c09c>`_ by Autumn).
- [typedef] support ``Annotation`` and within it, a set of ``Range``s, raise ``RangeError`` when a value is type allowed but does not fit the ranges specified! (`bad3554 <https://github.com/autumnjolitz/instruct/commit/bad3554094990acfe8f20a50444744d0f724d46c>`_ by Autumn).
- [constants, exceptions] several constants for use in ``Annotation[...]`` including ``Range`` for interval capping (and ``RangeError``)! (`94c1a64 <https://github.com/autumnjolitz/instruct/commit/94c1a64f30bd91092446a72ae71316c6fa88eace>`_ by Autumn).
- [0.6.7] cache by effective skipped fields across the board, do not confuse with second level skip/redefinitions (`e165b59 <https://github.com/autumnjolitz/instruct/commit/e165b597dcfa453508856ee2c9ed149fc50a4371>`_ by Autumn).
- [0.6.6] subtype handles zero-length collections correctly, type hints should resolve using the locals, module globals, then typing ones (`5d53ed0 <https://github.com/autumnjolitz/instruct/commit/5d53ed0f8f8587946728bc890e3edca9fc3efbe1>`_ by Autumn).
- [0.6.5] allow public class to access subclasses by index, document ambiguities, cascade subtraction preservation (`2c8cd91 <https://github.com/autumnjolitz/instruct/commit/2c8cd91fba582655418f61fdc4a81a8b9bbb95c2>`_ by Autumn).
- [0.6.4] fix public_class to detect modified subtracted classes, allow proper overrides of ``__coerce__`` when class inheritance is greater than 1 deep (`578c720 <https://github.com/autumnjolitz/instruct/commit/578c72060b9bd021003668fbd11b72bdf33822b9>`_ by Autumn).
- [0.6.3] bugfix - allow keys(...) to operate on field that is Atomic descendant (no optional, etc wrapping) (`0d132ec <https://github.com/autumnjolitz/instruct/commit/0d132ecc70cb4f0e000bfa0854fdc2f1e3602579>`_ by Autumn).
- [about] 0.6.2 (`31e6a0b <https://github.com/autumnjolitz/instruct/commit/31e6a0b418c74c21ff7c5b61b24e0b2648d0772d>`_ by Autumn).
- [__init__] add show_all_fields to public API, ensure reachability for Optional fields (`eefd409 <https://github.com/autumnjolitz/instruct/commit/eefd4097482629ce1217ffcc23d8231d0ef4d3ae>`_ by Autumn).
- [typedef] allow keys, show_all_fields to handle Union/Optional with embedded Atomics properly (`45f3f07 <https://github.com/autumnjolitz/instruct/commit/45f3f07ab5df3ef8fcb7b9a742d321f1b46dc9e5>`_ by Autumn).
- [0.6.1] allow class subtractions to be pickled/unpickled, make type name friendlier to inflection titleize, ensure a test for class method replacements, pickling (`d2d9259 <https://github.com/autumnjolitz/instruct/commit/d2d925916d114f6072797de47f1c5881ec858543>`_ by Autumn).
- [about] 0.6.0 release (`16e353d <https://github.com/autumnjolitz/instruct/commit/16e353d4d3495c55499b0c5458c978bab8c68836>`_ by Autumn).
- [.gitignore] add newline (`4030ecd <https://github.com/autumnjolitz/instruct/commit/4030ecdd96903dc7467c34bb9f232b1ffd31efaa>`_ by Autumn).
- [__init__] refactor, reduce wildcard exports, add a public_class(...) function that returns the public class from a data class or subtracted instance (`5ae5a80 <https://github.com/autumnjolitz/instruct/commit/5ae5a801ebb379dee6a609b9beadc56558f57f14>`_ by Autumn).
- [test_atomic] move nameless person to test scope to pass flake8 false negative (`ff13363 <https://github.com/autumnjolitz/instruct/commit/ff13363eea7fb31db5a670665ca715885d3a9798>`_ by Autumn).
- [__init__] allow keys() to operate and extract keys for an embedded field (`e0320d1 <https://github.com/autumnjolitz/instruct/commit/e0320d11a043c873c8fd4550ee66104180cefd79>`_ by Autumn).
- [__init__] in case of a tuple of existing types, add to it for the union (`65e6634 <https://github.com/autumnjolitz/instruct/commit/65e6634ad51bf5727c7c63ff77d0b26b0b68070b>`_ by Autumn).
- [__init__] allow for downcasting of a parent type to a subtracted type when generating the skip keys type (`798d981 <https://github.com/autumnjolitz/instruct/commit/798d981e31ace2405ab92f0e46d1620dceaa7bce>`_ by Autumn).
- [subtype] support collections by position, make unions branch on type checks, avoid pipe-nature in favor of graph branch approach (`14d1abe <https://github.com/autumnjolitz/instruct/commit/14d1abe5da8c566ca4f8fa544c9b8f75e2231193>`_ by Autumn).
- [typing] add U (`24b0009 <https://github.com/autumnjolitz/instruct/commit/24b000948a96101a45086dc15a757da0a6132583>`_ by Autumn).
- [subtype] allow for generation of an effective coerce function based on type spidering (`b4d5a36 <https://github.com/autumnjolitz/instruct/commit/b4d5a3614371e4ee8c0ec38d3f6ef166ada980a3>`_ by Autumn).
- [test_atomic] document absurdities (`149aafe <https://github.com/autumnjolitz/instruct/commit/149aafe99e108b6e52122cffafb604d4b57345d3>`_ by Autumn).
- [__init__] on subtraction of fields that cannot be, just ignore it (`a2147ca <https://github.com/autumnjolitz/instruct/commit/a2147ca0dd66d7b7462b2942e8d7d68a21f477ac>`_ by Autumn).
- [subtype] introduce a union branch function that assumes unique traces (`4917d0d <https://github.com/autumnjolitz/instruct/commit/4917d0d3208670cdb0edf54131ba0b789f514629>`_ by Autumn).
- [subtype] add in initial approach for automated parent value type coercion to subtracted type (`74cb651 <https://github.com/autumnjolitz/instruct/commit/74cb651d13a016be99b57831c967044904d9375e>`_ by Autumn).
- [__init__] handle subtracted classes in a more generalized fashion, use the correct function globals for LOAD_GLOBAL bytecode (`6ea1ea4 <https://github.com/autumnjolitz/instruct/commit/6ea1ea421356fee763e39f03d1ee8527407ab0d0>`_ by Autumn).
- [python-app] update workflow (`7905662 <https://github.com/autumnjolitz/instruct/commit/79056627ee1d3c39711e803dcd0f8549e9c9a961>`_ by Autumn).
- Add github action to test project (`70a2a30 <https://github.com/autumnjolitz/instruct/commit/70a2a301241baae91748ca032309bf6be971010f>`_ by Autumn Jolitz).
- [__init__] limit show_all_fields, refactor CellType creation to a simpler form (`4c8b02a <https://github.com/autumnjolitz/instruct/commit/4c8b02a55325a050a46d03e856ab9a230a5eccd0>`_ by Autumn).
- [types] annotate the ClassOrInstanceFuncsDescriptor (`6d8227a <https://github.com/autumnjolitz/instruct/commit/6d8227a1149c42dba0f372a6111601dbc4664613>`_ by Autumn).
- [typing] add CellType (`0a3f09a <https://github.com/autumnjolitz/instruct/commit/0a3f09ae3f8169d67d54fee526243eb7d51fb80f>`_ by Autumn).
- [__init__] support classmethod rewriting for skip keys (`70dcb3d <https://github.com/autumnjolitz/instruct/commit/70dcb3d1591265caaba6b6253d96a65ce082b69e>`_ by Autumn).
- [README] track progress (`e521d16 <https://github.com/autumnjolitz/instruct/commit/e521d16ef1f590e9ac35ca5683e738e3c612c5e0>`_ by Autumn).
- [__init__] allow overriding of callouts to a class in a `__coerce__` function by using a closure intercept (`a16546c <https://github.com/autumnjolitz/instruct/commit/a16546cde114ac54263473a43c47d7247c60e0e7>`_ by Autumn).
- [*] support `& ` on classes (`875eed5 <https://github.com/autumnjolitz/instruct/commit/875eed564c7b4faf63ee072ff27985da6b86f585>`_ by Autumn).
- [test_atomic] note where the cached classes may be looked up (`d490bf6 <https://github.com/autumnjolitz/instruct/commit/d490bf6fb6128c6046add6ed9281d55e35cb349d>`_ by Autumn).
- [*] refactor, allow caching of class subtractions via FrozenMapping (`014cf0f <https://github.com/autumnjolitz/instruct/commit/014cf0f6543a6600d02db86f204d35b0817dfb41>`_ by Autumn).
- [typedef] add stub for annotated decoding (`fa0ac80 <https://github.com/autumnjolitz/instruct/commit/fa0ac80e4d1d80d4ddd2bc5258dd2d94e7b29b65>`_ by Autumn).
- [test_atomic] add missing type (`764a96a <https://github.com/autumnjolitz/instruct/commit/764a96a68a577e8800dc30f97a687bad3b41a555>`_ by Autumn).
- [.gitignore] ignore build, pytype files (`fdda9e5 <https://github.com/autumnjolitz/instruct/commit/fdda9e5482413c66192d7e052b0ad1673a32672f>`_ by Autumn).
- [__init__] introduce more complex type subtractions that are communative (`84b035e <https://github.com/autumnjolitz/instruct/commit/84b035e520a8f9a2a9da6168c99a7b4bae5fe151>`_ by Autumn).
- [README] add new goals (`47aaa04 <https://github.com/autumnjolitz/instruct/commit/47aaa043c09b4b1c580b3cecf249c189b4b6080d>`_ by Autumn).
- [typedef] allow search/replace of instruct Atomics inside of typing.py instances w/o overriding a singleton (`1bf8de9 <https://github.com/autumnjolitz/instruct/commit/1bf8de99eb8a1fb73c8f87c579451975ef612c3a>`_ by Autumn).
- [__init__] skip keys support for single level, single Atomic-descendant removal of keys on an Atomic object (`b8aa725 <https://github.com/autumnjolitz/instruct/commit/b8aa725a84b4ff573534b8625e1689f9568235fb>`_ by Autumn).
- [0.5.0] add support for Literal's, bump minimum typing_extensions version (`b487a15 <https://github.com/autumnjolitz/instruct/commit/b487a15c06fdefc96c331195de747d6251260ab3>`_ by Autumn).
- [README] track new design goal additions (`c0b9feb <https://github.com/autumnjolitz/instruct/commit/c0b9feb0b0ff9687a248ba38a25797098596a106>`_ by Autumn).
- [0.4.13] fix typo where disabling derived should apply at all times, not only in debug mode (`32615bc <https://github.com/autumnjolitz/instruct/commit/32615bc2732d16f0ac4ebbdd23bba57cc1c8e3ec>`_ by Autumn).
- [0.4.12] if ``dict`` is in the __coerce__ types for a key, disable ``derived`` matching for setters (`2a38ee4 <https://github.com/autumnjolitz/instruct/commit/2a38ee4576b2a215cc6bcd4b0b36b94f7009987d>`_ by Autumn).
- [__main__] preallocate names, values, ids before test (`f25c1f3 <https://github.com/autumnjolitz/instruct/commit/f25c1f3c724cd9f658b1c37a9d59ca24f550f0d7>`_ by Autumn).
- [0.4.11] add top level ``asdict``, ``keys``, etc functions, bytes support for json encoding, ``__coerce__`` handles tuple of keys (`980ed5e <https://github.com/autumnjolitz/instruct/commit/980ed5ebbdeb26e50b05eb1b4589f21b9c94630e>`_ by Autumn).
- [0.4.10] metaclass support of key/values/items/to_json even on classes with clobbered fields, tuple/list/dict NamedTuple-like helper functions (`6fe85e9 <https://github.com/autumnjolitz/instruct/commit/6fe85e9f76d2d332834e3ad444fa13cab162f34a>`_ by Autumn).
- [0.4.9] correct issue where keyword only defaults were stripped (`33bf286 <https://github.com/autumnjolitz/instruct/commit/33bf286b50fc64ee286b759d1846e4e3988478ef>`_ by Autumn).
- [0.4.8] allow class definition in IDLE sessions (`4200aaa <https://github.com/autumnjolitz/instruct/commit/4200aaa9d232762e8cbe1c9c98b3f01d6118dbda>`_ by Autumn).
- [0.4.7] support dataclass/NamedTuple-like in lieu of ``__slots__``, allow for overriding of autogenerated magic methods while allowing ``super()`` in their overrides (`e8ac0b0 <https://github.com/autumnjolitz/instruct/commit/e8ac0b043faf0f069dee389d75e6cd93d02d7166>`_ by Autumn).
- [precommit] fix to older black because tuple unpacking for everything is noisy AF (`155c910 <https://github.com/autumnjolitz/instruct/commit/155c910d7fa54eec60e054fb4810ff269722b285>`_ by Autumn).
- [*] 0.4.6 - allow subtraction of fields on an adhoc basis (`b80dad7 <https://github.com/autumnjolitz/instruct/commit/b80dad77296a4e16242a6f9772db069baef16c17>`_ by Autumn).
- [__init__] refactor to make clearer, rename dataclass to "concrete_class" to signal "don't touch this" (`398cc83 <https://github.com/autumnjolitz/instruct/commit/398cc8363a2916764f453e557416d96558913b09>`_ by Autumn).
- [typedef] add helper function (`1fedefa <https://github.com/autumnjolitz/instruct/commit/1fedefa15b396a3c92de24bbe7bb9ebd89fba10b>`_ by Autumn).
- [typedef] document to be clearer, remove erroneous cast to type (`ae432c7 <https://github.com/autumnjolitz/instruct/commit/ae432c79380b7e3b0fac7b3418f7d363927c1f1e>`_ by Autumn).
- [__init__] avoid calling ``parse_typedef`` on ``__coerce__ = None`` (`b745164 <https://github.com/autumnjolitz/instruct/commit/b74516434d3425a8b6026bd108d6dde55f391de9>`_ by Autumn).
- [0.4.5] keep a weakreference to the owning classes to avoid constant rebinding for one-time class definitions (`1890144 <https://github.com/autumnjolitz/instruct/commit/18901449847866e9b8b994853282051d0b3f0ac9>`_ by Autumn Jolitz).
- [0.4.4] use order preserving keys(), provide class-level keys(), allow for positional arguments (`49c3769 <https://github.com/autumnjolitz/instruct/commit/49c376912e9a017da47fe24b17f8eb505ef9bf0f>`_ by Autumn Jolitz).
- [__init__, test_atomic] at class definition time, track if the property type list may have a collection of Atomic descendants (`e975f07 <https://github.com/autumnjolitz/instruct/commit/e975f0775ed2676bcb327d1ca9a2e727f607a901>`_ by Autumn Jolitz).
- [typedef, test_typedef] function for determining if it contains a collection/mapping of Atomic-descendents in type definition (`305db0c <https://github.com/autumnjolitz/instruct/commit/305db0cea5d666e3facc1f7b37bf8a082a047578>`_ by Autumn Jolitz).
- [about] 0.4.3 (`2950c31 <https://github.com/autumnjolitz/instruct/commit/2950c318ba402eafe03a62277e76fafb0c422017>`_ by Autumn Jolitz).
- Update author information (`fe4d0e2 <https://github.com/autumnjolitz/instruct/commit/fe4d0e2027040ef20f1a07e152d7cb22a2dd41cb>`_ by Autumn Jolitz).
- [0.4.2] preserve original slots at ``_slots``, improve FrozenMapping interface (`768ee26 <https://github.com/autumnjolitz/instruct/commit/768ee26c179adf0e68edde766ec49d18f3c362ce>`_ by Autumn Jolitz).
- [0.4.1] restrict flatten to only merge list, tuple, generators (`6169863 <https://github.com/autumnjolitz/instruct/commit/61698638b79b30033466424eeec6ece7d2ebfc9f>`_ by Autumn Jolitz).
- [0.4.0] finer grained exceptions, support `[]` on properties, rename `skip`->`dataclass`, ability to handle property type violations with a handler function (`598b35e <https://github.com/autumnjolitz/instruct/commit/598b35e5bcf56fc0e523db9de40fcb8702b4d108>`_ by Autumn Jolitz).
- [0.3.8] Mapping immutability on to_json, enforce `__coerce__` constraints (`6be62d4 <https://github.com/autumnjolitz/instruct/commit/6be62d444cf3758e7d71bc2983a7acf6a5d35b9c>`_ by Autumn Jolitz).
- [0.3.7] fix bug for singular exception (`63d1eac <https://github.com/autumnjolitz/instruct/commit/63d1eac116987202e919c730e9ae9e1be5c5d9d7>`_ by Autumn Jolitz).
- [0.3.6] bugfix - support embedded Tuple[int, int, int, int] (`8065e73 <https://github.com/autumnjolitz/instruct/commit/8065e733a8c7dfbbb7a2aaf76f2341ee89867d63>`_ by Autumn Jolitz).
- [0.3.5] explicitly support Tuple[type, ...], Dict[key_type, value_type] (`12696b4 <https://github.com/autumnjolitz/instruct/commit/12696b4961dcf40ba3fa4335c4dcf9f7e54d3d0b>`_ by Autumn Jolitz).
- [*]7 add black (`003f98d <https://github.com/autumnjolitz/instruct/commit/003f98d8d002cdbd4dae75492045dd1f980a1c7d>`_ by Autumn Jolitz).
- [0.3.4] support redefining properties on inherited members if explicitly called out (`fd39ad9 <https://github.com/autumnjolitz/instruct/commit/fd39ad95e11477c341e9565bf82dc1bc798e14b4>`_ by Autumn Jolitz).
- [support] add in potential hooks for mypy and pytype (`271c493 <https://github.com/autumnjolitz/instruct/commit/271c4938abb5d287486ec365658e59a08684d4fb>`_ by Autumn Jolitz).
- [setup] add in defintions for type checkers (`49446a6 <https://github.com/autumnjolitz/instruct/commit/49446a6ec657520f6e97c0cee02125a165de5cb1>`_ by Autumn Jolitz).
- [typedef] pass type check (`1e91350 <https://github.com/autumnjolitz/instruct/commit/1e91350284d04eb85c96d2fe2fd8148c125e4101>`_ by Autumn Jolitz).
- [about] 0.3.3 (`90533b4 <https://github.com/autumnjolitz/instruct/commit/90533b4c8f851fe602ee3da1546a76f2e9bac0da>`_ by Autumn Jolitz).
- [__main__] silence conditional import (`9606cf2 <https://github.com/autumnjolitz/instruct/commit/9606cf2efb19c976b7d63a068ab53bcdc4586dba>`_ by Autumn Jolitz).
- [__init__] add types (`470cce0 <https://github.com/autumnjolitz/instruct/commit/470cce060965ebc992b0068a1bd0e50817a10153>`_ by Autumn Jolitz).
- [typing] add project type definitions (`6e62cef <https://github.com/autumnjolitz/instruct/commit/6e62cef48428077aaae39df6f5ba78d0e7614123>`_ by Autumn Jolitz).
- [0.3.2] support nested ClassCreationFaileds (`b2fa790 <https://github.com/autumnjolitz/instruct/commit/b2fa7905d939b57204957f1e15ed3984e5a69a89>`_ by Autumn Jolitz).
- [0.3.1] pass _column_types for mixins (`31f6e46 <https://github.com/autumnjolitz/instruct/commit/31f6e46379f9bfc0a3fa91b2e9cbc48f2c6999fe>`_ by Autumn Jolitz).
- [0.3.0] renormalize the changes list (`a45a337 <https://github.com/autumnjolitz/instruct/commit/a45a33756215cad25bf08cb0fd048a0487719aab>`_ by Autumn Jolitz).
- [0.2.7] identify as Mapping (`69d21cd <https://github.com/autumnjolitz/instruct/commit/69d21cdc350fc26f7d86729c9ff26205e3692177>`_ by Autumn Jolitz).
- [0.2.6] add in a from_json top level helper (`23d42be <https://github.com/autumnjolitz/instruct/commit/23d42be4b7850a577cad543f6f44b15575e33038>`_ by Autumn Jolitz).
- [0.2.5] fix qualname for internal dataclasses (`d4aaa0c <https://github.com/autumnjolitz/instruct/commit/d4aaa0c822b4a7158a25f9aee5e6d087d32e1766>`_ by Autumn Jolitz).
- [0.2.4] fix up qualname, module on dataclass instances (`5cd4e25 <https://github.com/autumnjolitz/instruct/commit/5cd4e255a719f340710a6f5dcd062fe2a16eac49>`_ by Autumn Jolitz).
- [__init__] remove leading `_` (`14a1a10 <https://github.com/autumnjolitz/instruct/commit/14a1a104c6ef5e9467cc4be0e5b1be34a63eb4e6>`_ by Autumn Jolitz).
- [test_atomic] test for the mutable leakage (`97a1204 <https://github.com/autumnjolitz/instruct/commit/97a12049adcce79dcaedb75a3a07ebf6ce0b58bb>`_ by Autumn Jolitz).
- [0.2.3] assume immutable copies (`224a6c7 <https://github.com/autumnjolitz/instruct/commit/224a6c723ba62fb3f0b877456aa8feb85ebb2cd8>`_ by Autumn Jolitz).
- [*] 0.2.2 - add in typename of Class exception (`8d918ba <https://github.com/autumnjolitz/instruct/commit/8d918bace7d6375f184cd2479e995a74fff1646c>`_ by Autumn Jolitz).
- [__init__] use the `globals()` for overridden props from `__module__` (`7988271 <https://github.com/autumnjolitz/instruct/commit/7988271e9ece901b93a6d797a1d7f2137a4e67a2>`_ by Autumn Jolitz).
- [about] 0.2.1 (`8b8b026 <https://github.com/autumnjolitz/instruct/commit/8b8b0266ebb03ae1b7e5e823cc3cbcb92fb8acf8>`_ by Autumn Jolitz).
- [test_atomic] add test for clear (`77ea90b <https://github.com/autumnjolitz/instruct/commit/77ea90b7e056ad77342836d95c06a610dd7307ae>`_ by Autumn Jolitz).
- [*] use `_{key}_` for internal access (`9883660 <https://github.com/autumnjolitz/instruct/commit/988366078292f424402c4eeb4c0127a5307bd52e>`_ by Autumn Jolitz).
- [__init__] `_raw_{key}` -> `_{key}_`, fix up __class__ for super() (`a6b1808 <https://github.com/autumnjolitz/instruct/commit/a6b18081baefe0129dbebee5d7661dce9bacca5b>`_ by Autumn Jolitz).
- [about] 0.2.0 (`84f47b3 <https://github.com/autumnjolitz/instruct/commit/84f47b350dc3b660f796b6e32b3ec3e55742d644>`_ by Autumn Jolitz).
- [0.1.1] remove errant debug print (`c36c5c3 <https://github.com/autumnjolitz/instruct/commit/c36c5c39263e0f52573b6c81382a5f66a322cdd3>`_ by Autumn Jolitz).
- [0.1.0] support 1-level Iterable[Base]->JSON, hooks, better pickling, setitem on class (`4ef5b64 <https://github.com/autumnjolitz/instruct/commit/4ef5b6444dc7fb6d18d364a69e0b99c59c0e085f>`_ by Autumn Jolitz).
- [*] 0.0.22 - avoid expanding Enums for type defs (`e3d56d1 <https://github.com/autumnjolitz/instruct/commit/e3d56d1104ec5373ab719afa9e4d0b1d65cbb995>`_ by Autumn Jolitz).
- [*] 0.0.21 - more tests (`60d7e53 <https://github.com/autumnjolitz/instruct/commit/60d7e53a124c8a05f481fc2a970620a8658f42a4>`_ by Autumn Jolitz).
- [*] 0.0.20 - track coerce types (`6dd6866 <https://github.com/autumnjolitz/instruct/commit/6dd6866dbdd3304ae2c3f723fedae02e79277ce2>`_ by Autumn Jolitz).
- [*] 0.0.19 - support nested List better (`427e7bf <https://github.com/autumnjolitz/instruct/commit/427e7bfa10c6ac95e94f69dc87c7cc5e4c33179d>`_ by Autumn Jolitz).
- [test_atomic] fix tests (`f2c0ed5 <https://github.com/autumnjolitz/instruct/commit/f2c0ed58a1cdaef07224322224608a556026aa17>`_ by Autumn Jolitz).
- [*] 0.0.18 - error on generics, support nested lists (`ebecd5a <https://github.com/autumnjolitz/instruct/commit/ebecd5a949265e52f80ca64a694414e611ea15a0>`_ by Autumn Jolitz).
- [.gitignore] ignore python/ venv and .pytest_cache (`acfffa5 <https://github.com/autumnjolitz/instruct/commit/acfffa5fc5c7d87035e72fc327fdd7519aaedd2b>`_ by Autumn Jolitz).
- [*] 0.0.17, fix type message (`c60b798 <https://github.com/autumnjolitz/instruct/commit/c60b798bb836bccad3e41e725f601d29f938bdac>`_ by Autumn Jolitz).
- [*] 0.0.16 - fix history truncation (`cdf4ca9 <https://github.com/autumnjolitz/instruct/commit/cdf4ca94be690df0f9c43671191c7b4aa50e9482>`_ by Autumn Jolitz).
- [*] support correct property accounting (`0e30102 <https://github.com/autumnjolitz/instruct/commit/0e301024d248cc23981fdc212401a4523e3839f3>`_ by Autumn Jolitz).
- [*] 0.0.14 - now with better type names (`c2e88cd <https://github.com/autumnjolitz/instruct/commit/c2e88cd7b76806331db9329229769d151efa2a0b>`_ by Autumn Jolitz).
- [*] 0.0.13 - index properties onto the class (`bb2f2fc <https://github.com/autumnjolitz/instruct/commit/bb2f2fc922462648124213869a176b99c92165ca>`_ by Autumn Jolitz).
- [*] 0.0.12, supports overrideable type errors (`7c64cbb <https://github.com/autumnjolitz/instruct/commit/7c64cbbc6ea2239c86164228b29f1042ffe7d44a>`_ by Autumn Jolitz).
- [*] Correct bug in fast=True, 0.0.11 (`8643b3c <https://github.com/autumnjolitz/instruct/commit/8643b3cd5bd82dcb11a203e4e41bba2cbfa00e8d>`_ by Autumn Jolitz).
- [*] add in **mapping support (`cc66a24 <https://github.com/autumnjolitz/instruct/commit/cc66a2498422c56a69ce0932218a6fb2e34365fe>`_ by Autumn Jolitz).
- [*] refactor and introduce better naming (`948712e <https://github.com/autumnjolitz/instruct/commit/948712ee4d54238fa5b7151fbbca733dfd0a5248>`_ by Autumn Jolitz).
- [*] Support generation of custom types to match requirements (`08823a5 <https://github.com/autumnjolitz/instruct/commit/08823a5470e63d7381f358ec9ea74e1ba207505e>`_ by Autumn Jolitz).
- [*] restore '__hash__' to data classes (`476807d <https://github.com/autumnjolitz/instruct/commit/476807d6b16e2fb00d2cbbf59dae5d9d88a3c94a>`_ by Autumn Jolitz).
- [__init__] make it possible to get the parent support class (`b186660 <https://github.com/autumnjolitz/instruct/commit/b1866607e6e80675744af201d917095f3c395590>`_ by Autumn Jolitz).
- [*] python 3.7 focus (`9cd710b <https://github.com/autumnjolitz/instruct/commit/9cd710b8880b618dbf0decb0ba1727788746b873>`_ by Autumn Jolitz).
- [about] bump (`3522e16 <https://github.com/autumnjolitz/instruct/commit/3522e160585f0a113637198c67b86a72e3257444>`_ by Autumn Jolitz).
- [macros] allow use of `type` as a var name (`a20c541 <https://github.com/autumnjolitz/instruct/commit/a20c5413ee5669f7f61db96a7ec1c53bf4a04d95>`_ by Autumn Jolitz).
- [*] this is not a universal build (`7fb73d4 <https://github.com/autumnjolitz/instruct/commit/7fb73d4a5a4ccf21e5c87e08cae2239eb4999d5f>`_ by Autumn Jolitz).
- [*] updates for 3.7 (`58feb63 <https://github.com/autumnjolitz/instruct/commit/58feb634e36746796f16fc18d6ae9281ae350830>`_ by Autumn Jolitz).
- [setup.cfg] remove inaccurate (`3b7b11f <https://github.com/autumnjolitz/instruct/commit/3b7b11fe0d4b7363777a41aecef261cb0726dd9e>`_ by Autumn Jolitz).
- [setup] initial release of just the object structure (`3c45220 <https://github.com/autumnjolitz/instruct/commit/3c452209448b585ff3a972684cfb2725c9867195>`_ by Autumn Jolitz).
- [README] update (`feaf89d <https://github.com/autumnjolitz/instruct/commit/feaf89dc59214802ac7375185d21f2dc9442750b>`_ by Autumn Jolitz).
- [setup] add pytest dependency (`2cc81cb <https://github.com/autumnjolitz/instruct/commit/2cc81cb4ac13c5918d0fbc710faef70a78279b6f>`_ by Autumn Jolitz).
- [__init__] update for python3.6 (`d781bcd <https://github.com/autumnjolitz/instruct/commit/d781bcdbe8945a16e95bf2dbe91739b84b8e3c80>`_ by Autumn Jolitz).
- [init] bugfixes (`7c4fc5e <https://github.com/autumnjolitz/instruct/commit/7c4fc5e2aae3ed3a6488d38ccdbcb66e285fc34b>`_ by Autumn Jolitz).
- [readme] update intent (`1c42816 <https://github.com/autumnjolitz/instruct/commit/1c428164bec6b2e63f0d4c8d82bdf4ca611cf443>`_ by Autumn Jolitz).
- [tests] add test for the readme (`23123ab <https://github.com/autumnjolitz/instruct/commit/23123ab3be7af1212450d500ab57f283d46ddcfc>`_ by Autumn Jolitz).
- fix (`0c35681 <https://github.com/autumnjolitz/instruct/commit/0c356819059af90b5bd00cfb3ededdf3bf3de5f9>`_ by Autumn Jolitz).
- Add docs (`f2bfcca <https://github.com/autumnjolitz/instruct/commit/f2bfccaf4d621c05e68660d5fcb7419fd8936407>`_ by Autumn Jolitz).
- add space (`55a829f <https://github.com/autumnjolitz/instruct/commit/55a829f9fbacc802ca962fc55e75c1fd3f9b6291>`_ by Autumn Jolitz).
- Log performance (`475e41d <https://github.com/autumnjolitz/instruct/commit/475e41d1463aa0f70d9026cf3d3fbb1f209b3cb5>`_ by Autumn Jolitz).
- Log my approach (`ebe9cc7 <https://github.com/autumnjolitz/instruct/commit/ebe9cc7b75b15502c9be853506c45c303b4c6f45>`_ by Autumn Jolitz).
- Add JSON/Pickle/Coercion support (`b98b9a5 <https://github.com/autumnjolitz/instruct/commit/b98b9a56356b4c9c5e8e810ab5226dd18a55fc5e>`_ by Autumn Jolitz).
- Add field linkages (`3b0b201 <https://github.com/autumnjolitz/instruct/commit/3b0b2012af5b338be369ab612cc600b122556006>`_ by Autumn Jolitz).
- Support multiple inheritance, optimize edge classes (`9df72c8 <https://github.com/autumnjolitz/instruct/commit/9df72c8bada2b846bd57fe3a903021a322d20fc5>`_ by Autumn Jolitz).
- Increase performance through codegen of constant structural cases (`9d9499b <https://github.com/autumnjolitz/instruct/commit/9d9499b4dbc62e6c59153797415fcc7644617fff>`_ by Autumn Jolitz).
- Delete unused code (`dc520b6 <https://github.com/autumnjolitz/instruct/commit/dc520b6cb4029593f42b8d14f0a7342629b24fdd>`_ by Autumn Jolitz).
- Use Jinja to handle the macro-work (`b00d1c1 <https://github.com/autumnjolitz/instruct/commit/b00d1c1da3f3c50d0a93c8ec0ad79a9e83b096a3>`_ by Autumn Jolitz).
- Optimize through use of `__new__` to seed vital fields ahead of time (`c159161 <https://github.com/autumnjolitz/instruct/commit/c159161636c0a3fec0b68ee37af6941f2cfd4681>`_ by Autumn Jolitz).
- Handle the "How do I describe default variables but support clearing/set of None for defaults" (`e963674 <https://github.com/autumnjolitz/instruct/commit/e96367473e7f80e9eb589106fa16495f28b1ccfc>`_ by Autumn Jolitz).
- Support derived embedded classes and duck-eqing them (`5ded37b <https://github.com/autumnjolitz/instruct/commit/5ded37b7e7e9e3c02cc563341b6eb74c8f9987e7>`_ by Autumn Jolitz).
- Flush out an idea (`4fff08f <https://github.com/autumnjolitz/instruct/commit/4fff08f31c4d556852deb0e2b309c2a95da0e62b>`_ by Autumn Jolitz).

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
