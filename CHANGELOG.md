# [2.2.0-dev.17](https://github.com/getappmap/appmap-python/compare/v2.2.0-dev.16...v2.2.0-dev.17) (2025-11-24)


### Bug Fixes

* **ci/release/publish:** verbose upload to testPyPi (trobleshooting upload failures with 400 Bad Request) ([500a3c8](https://github.com/getappmap/appmap-python/commit/500a3c89fb7aad02bd3be751e92254bfe2a2126c))

# [2.2.0-dev.16](https://github.com/getappmap/appmap-python/compare/v2.2.0-dev.15...v2.2.0-dev.16) (2025-11-24)


### Bug Fixes

* **ci/release/publish:** update testpypi endpoint ([9bc7729](https://github.com/getappmap/appmap-python/commit/9bc77296d0e9d2ab52b379d1188790f25b00c6b7))

# [2.2.0-dev.15](https://github.com/getappmap/appmap-python/compare/v2.2.0-dev.14...v2.2.0-dev.15) (2025-11-24)


### Bug Fixes

* **ci:** remove inappropriate step parameter which was not there before and should not be there ([2cd2f1c](https://github.com/getappmap/appmap-python/commit/2cd2f1cc2b60942550bfedfc36fc491d9a1abc11))

# [2.2.0-dev.14](https://github.com/getappmap/appmap-python/compare/v2.2.0-dev.13...v2.2.0-dev.14) (2025-11-24)


### Bug Fixes

* **ci/release:** typo in reference ([9bddf13](https://github.com/getappmap/appmap-python/commit/9bddf1382226f8618ef08a0fb5170a5778af9961))

# [2.2.0-dev.13](https://github.com/getappmap/appmap-python/compare/v2.2.0-dev.12...v2.2.0-dev.13) (2025-11-24)


### Bug Fixes

* **ci/release:** clean up bash snippet in setup ([37dcedd](https://github.com/getappmap/appmap-python/commit/37dcedd7f8d2521dfb2e348bd8afc8b43ba7053c))
* **ci/release:** more explicit dependencies between jobs ([268614e](https://github.com/getappmap/appmap-python/commit/268614eea4896d738e4c8f12819cc5e5e5f6ce0d))

# [2.2.0-dev.12](https://github.com/getappmap/appmap-python/compare/v2.2.0-dev.11...v2.2.0-dev.12) (2025-11-24)


### Bug Fixes

* **ci/release/setup:** correct propagation of outputs from step to job ([ef3e35c](https://github.com/getappmap/appmap-python/commit/ef3e35c1253661ccb8b4b854193f16b38c03c720))
* **ci/release/setup:** typo in conditional ([15542b3](https://github.com/getappmap/appmap-python/commit/15542b3191616adbcfb89123cfeaf5dd470147c1))
* **ci:** configure publishing parameters in a separate job, skip smoketest on altered packages, use altered distnames for publishing test only, restore original distribution name in pyproject.toml ([1b6143b](https://github.com/getappmap/appmap-python/commit/1b6143b72df930eee95c91616ba9ba73a225d861))
* **ci:** indentation issue ([c6e7149](https://github.com/getappmap/appmap-python/commit/c6e71493d30e7fce05ed6116b8ee4dd431ce212f))
* **ci:** one more syntax mistake ([01e4b90](https://github.com/getappmap/appmap-python/commit/01e4b901b35c50a89521a11d80cf8462678519ae))
* **ci:** proper syntax for evaluations ([7adeec9](https://github.com/getappmap/appmap-python/commit/7adeec9f0884865e22e0b64a96e2584b4ed2e1d8))

# [2.2.0-dev.11](https://github.com/getappmap/appmap-python/compare/v2.2.0-dev.10...v2.2.0-dev.11) (2025-11-23)


### Bug Fixes

* **ci:** correctly patch sdist for altered names ([0661304](https://github.com/getappmap/appmap-python/commit/0661304bc89ef293cce220271d435995d11d3596))
* **ci:** errors in Provides-Dist injector ([41dbb08](https://github.com/getappmap/appmap-python/commit/41dbb08ae731fca5604f098da56c241b9beec193))
* **ci:** manual fix -- rollback version in pyproject.toml to the last fully released dev version ([9b1161b](https://github.com/getappmap/appmap-python/commit/9b1161b7f4bb3b4b167ca06d9424af2db0315a80))

# [2.2.0-dev.11](https://github.com/getappmap/appmap-python/compare/v2.2.0-dev.10...v2.2.0-dev.11) (2025-11-23)


### Bug Fixes

* **ci:** errors in Provides-Dist injector ([41dbb08](https://github.com/getappmap/appmap-python/commit/41dbb08ae731fca5604f098da56c241b9beec193))

# [2.2.0-dev.10](https://github.com/getappmap/appmap-python/compare/v2.2.0-dev.9...v2.2.0-dev.10) (2025-11-23)


### Bug Fixes

* **ci:** enforce distribution name via pyproject.toml patching ([b43835f](https://github.com/getappmap/appmap-python/commit/b43835f75f4950023aab6e9ea3ca18455484f0a3))

# [2.2.0-dev.9](https://github.com/getappmap/appmap-python/compare/v2.2.0-dev.8...v2.2.0-dev.9) (2025-11-23)


### Bug Fixes

* **ci:** update invocation of smoketest script to conform with new ci scripts layout ([b1fc2bf](https://github.com/getappmap/appmap-python/commit/b1fc2bf682e462a1e7ce5a6192267bfa712d986d))

# [2.2.0-dev.8](https://github.com/getappmap/appmap-python/compare/v2.2.0-dev.7...v2.2.0-dev.8) (2025-11-23)


### Bug Fixes

* **ci/releaserc:** perform SemVer->PEP440 coercion in a separate step ([b64fd4a](https://github.com/getappmap/appmap-python/commit/b64fd4a54ae8717c352bb9755ce277c03d0d098d))
* **ci:** dedicated script for artifacts patching in case distribution name is altered; +reorganizing scripts in ci/ ([5a42170](https://github.com/getappmap/appmap-python/commit/5a4217015ec5d1f81e7e025ab29c814dfa812b6f))
* **ci:** eliminate overlooked uses of renamed variables in release script ([386a57f](https://github.com/getappmap/appmap-python/commit/386a57f6fbdcf4675a7738960b52a10d4b26b573))
* **ci:** manually revert pyproject.toml to the last dev version properly tagged (v2.2.0-dev.7) ([f43aff7](https://github.com/getappmap/appmap-python/commit/f43aff7436403a45a5773379bf5e7d2683498417))
* **ci:** no semantic-release expectations on optional replacements (release suffix coercions) ([220c7c2](https://github.com/getappmap/appmap-python/commit/220c7c225e8a5e8698e142a0eff1c83b804dd6f3))
* **ci:** patch artifacts with Provides-Dist if distribution name is altered ([206971b](https://github.com/getappmap/appmap-python/commit/206971ba444bdb3b77eb8a6ec46a7bbeb14328ee))


### Features

* **ci/releaserc:** rollback previous change and trigger minor release instead of patch ([cdc2d58](https://github.com/getappmap/appmap-python/commit/cdc2d585849eff7f8902063b956f13d206800bfa))

# [2.2.0-dev.8](https://github.com/getappmap/appmap-python/compare/v2.2.0-dev.7...v2.2.0-dev.8) (2025-11-21)


### Bug Fixes

* **ci:** patch artifacts with Provides-Dist if distribution name is altered ([206971b](https://github.com/getappmap/appmap-python/commit/206971ba444bdb3b77eb8a6ec46a7bbeb14328ee))

# [2.2.0-dev.7](https://github.com/getappmap/appmap-python/compare/v2.2.0-dev.6...v2.2.0-dev.7) (2025-11-21)


### Bug Fixes

* **ci:** use underscores in alt package names ([d58c848](https://github.com/getappmap/appmap-python/commit/d58c8485cf280d377541dd1ed1acfa53f849e4b7))

# [2.2.0-dev.6](https://github.com/getappmap/appmap-python/compare/v2.2.0-dev.5...v2.2.0-dev.6) (2025-11-21)


### Bug Fixes

* **ci:** correctly expose APPMAP_PACKAGE_NAME into the smoketest container ([9cc399f](https://github.com/getappmap/appmap-python/commit/9cc399f1aba54b1a12adfcaf2ced7b2704409467))

# [2.2.0-dev.5](https://github.com/getappmap/appmap-python/compare/v2.2.0-dev.4...v2.2.0-dev.5) (2025-11-21)


### Bug Fixes

* **ci:** troubleshooting artifacts fetcher ([798310c](https://github.com/getappmap/appmap-python/commit/798310c2f413bad6f529b6ddb46693b3bf97f1f0))

# [2.2.0-dev.4](https://github.com/getappmap/appmap-python/compare/v2.2.0-dev.3...v2.2.0-dev.4) (2025-11-21)


### Bug Fixes

* **ci:** missing shell directive on an action ([d10dee2](https://github.com/getappmap/appmap-python/commit/d10dee2cf9ae62e35e7cfb039c26e85af58af643))

# [2.2.0-dev.3](https://github.com/getappmap/appmap-python/compare/v2.2.0-dev.2...v2.2.0-dev.3) (2025-11-21)


### Bug Fixes

* **ci/smoketest:** account for possible altering of package name ([890629f](https://github.com/getappmap/appmap-python/commit/890629fbac99eaa858b7e69737eb0282a0b5a98d))
* **ci:** typo (double-quotes in interpolation) ([4730fc0](https://github.com/getappmap/appmap-python/commit/4730fc052b5d5454a2f821488cc6cd2508cbc783))

# [2.2.0-dev.2](https://github.com/getappmap/appmap-python/compare/v2.2.0-dev.1...v2.2.0-dev.2) (2025-11-21)


### Bug Fixes

* **ci/github/actions:** unzip artifacts after fetching ([4ce4f4d](https://github.com/getappmap/appmap-python/commit/4ce4f4d61f0a81196aa9735ce7192f2aae618be0))

# [2.2.0-dev.1](https://github.com/getappmap/appmap-python/compare/v2.1.9-dev.3...v2.2.0-dev.1) (2025-11-21)


### Bug Fixes

* **ci:** mistake in declaration -- environment belongs to workflow level not job level ([cf04dbe](https://github.com/getappmap/appmap-python/commit/cf04dbe43c88f23b6f1b85772866fcde00b69746))


### Features

* **ci:** support altering package names before publication (useful in rare occasions) ([d8f45d4](https://github.com/getappmap/appmap-python/commit/d8f45d4d3df462df7df145c366b8d954138b4fc2))

## [2.1.9-dev.3](https://github.com/getappmap/appmap-python/compare/v2.1.9-dev.2...v2.1.9-dev.3) (2025-11-11)


### Bug Fixes

* **ci/smoketest:** prevent failure by exposing git into image (as required by recent appmap) ([c68d759](https://github.com/getappmap/appmap-python/commit/c68d759535302d23cf9ff78f514088fd112070a2))

## [2.1.9-dev.2](https://github.com/getappmap/appmap-python/compare/v2.1.9-dev.1...v2.1.9-dev.2) (2025-11-11)


### Bug Fixes

* **workflows/release:** use python3.12-slim for smoketest (alpine has no bash) ([7939b19](https://github.com/getappmap/appmap-python/commit/7939b19b13eceadb0ea96c0c3131e08827a1be3b))

## [2.1.9-dev.1](https://github.com/getappmap/appmap-python/compare/v2.1.8...v2.1.9-dev.1) (2025-11-11)


### Bug Fixes

* **ci:** correctly name release branch in releaserc, +eliminate some trailing spaces ([40352b0](https://github.com/getappmap/appmap-python/commit/40352b0bfd0b01017b9859680fb82ce87b4d4144))
* **ci:** one more syntax fix, do not use .env in job conditionals ([1075528](https://github.com/getappmap/appmap-python/commit/10755284d92aae9d451ba0cdc1059583d17f0f39))
* **ci:** one more syntax fix, stray double-quotes ([3eafbbf](https://github.com/getappmap/appmap-python/commit/3eafbbf4448612ce1fa3b40c2498d76bf14c9e08))
* **ci:** pin specific testing branch to trigger a prerelease ([ed79ac4](https://github.com/getappmap/appmap-python/commit/ed79ac4ab928cb10f4a701fbde0d5188f33511f9))
* **ci:** syntax issue (also this commit triggers semantic-release version bump) ([3a0327a](https://github.com/getappmap/appmap-python/commit/3a0327a83f34f0703bde6c34182873e0fda88e17))
* **ci:** temporary enable release workflow run on pushes to ci/** ([87c8938](https://github.com/getappmap/appmap-python/commit/87c8938a722b6261298a7a507078b778e48dcf3f))
* **ci:** unblock first step of release (relax guard condition to allow execution on push to ci/*) ([5539f33](https://github.com/getappmap/appmap-python/commit/5539f334e93b8a6eca125f5eb86c5dc12817a884))
* **releaserc:** add missing closing quote, removed redundant branch qualifier ([3d140b2](https://github.com/getappmap/appmap-python/commit/3d140b26c5888a881034ba444bd2895f696b1c9b))
* **releaserc:** indentation + comments ([0688f75](https://github.com/getappmap/appmap-python/commit/0688f7528825d608d4cb0e4e67d490bfebb98890))
* **releaserc:** remove non-existing branch references ([b7ccb2e](https://github.com/getappmap/appmap-python/commit/b7ccb2e3d4b80db6366a8da04fab5d665e962770))
* **semantic-release:** PEP440 compatibility for prereleases ([f8bedfc](https://github.com/getappmap/appmap-python/commit/f8bedfcdfb9e67e603033fb6e862c33a13aa1336))

## [2.1.9-ci.1](https://github.com/getappmap/appmap-python/compare/v2.1.8...v2.1.9-ci.1) (2025-11-11)


### Bug Fixes

* **ci:** correctly name release branch in releaserc, +eliminate some trailing spaces ([40352b0](https://github.com/getappmap/appmap-python/commit/40352b0bfd0b01017b9859680fb82ce87b4d4144))
* **ci:** one more syntax fix, do not use .env in job conditionals ([1075528](https://github.com/getappmap/appmap-python/commit/10755284d92aae9d451ba0cdc1059583d17f0f39))
* **ci:** one more syntax fix, stray double-quotes ([3eafbbf](https://github.com/getappmap/appmap-python/commit/3eafbbf4448612ce1fa3b40c2498d76bf14c9e08))
* **ci:** pin specific testing branch to trigger a prerelease ([ed79ac4](https://github.com/getappmap/appmap-python/commit/ed79ac4ab928cb10f4a701fbde0d5188f33511f9))
* **ci:** syntax issue (also this commit triggers semantic-release version bump) ([3a0327a](https://github.com/getappmap/appmap-python/commit/3a0327a83f34f0703bde6c34182873e0fda88e17))
* **ci:** temporary enable release workflow run on pushes to ci/** ([87c8938](https://github.com/getappmap/appmap-python/commit/87c8938a722b6261298a7a507078b778e48dcf3f))
* **ci:** unblock first step of release (relax guard condition to allow execution on push to ci/*) ([5539f33](https://github.com/getappmap/appmap-python/commit/5539f334e93b8a6eca125f5eb86c5dc12817a884))
* **releaserc:** remove non-existing branch references ([b7ccb2e](https://github.com/getappmap/appmap-python/commit/b7ccb2e3d4b80db6366a8da04fab5d665e962770))

## [2.1.8](https://github.com/getappmap/appmap-python/compare/v2.1.7...v2.1.8) (2024-11-13)


### Bug Fixes

* Prevent process recordings from clobbering one another ([0347af1](https://github.com/getappmap/appmap-python/commit/0347af18d69f5f3be6a8c0789400bacd3fff42b9))

## [2.1.7](https://github.com/getappmap/appmap-python/compare/v2.1.6...v2.1.7) (2024-08-15)


### Bug Fixes

* cache Env.root_dir, is_appmap_repo ([5122d76](https://github.com/getappmap/appmap-python/commit/5122d7659722663cecf4d203883a48d136e19618))
* disable parameter rendering by  default ([91f1364](https://github.com/getappmap/appmap-python/commit/91f136445c16bcb55912549d8512bea7732d8218))

## [2.1.6](https://github.com/getappmap/appmap-python/compare/v2.1.5...v2.1.6) (2024-08-13)


### Bug Fixes

* generate AppMap data from django tests ([ea0918c](https://github.com/getappmap/appmap-python/commit/ea0918cf4e952a9e1ab4a48253ec16e4484b78a0))
* make wrapt function objects pickleable ([3561e3b](https://github.com/getappmap/appmap-python/commit/3561e3b13a1f004b793073a9f9f7e1345b192fa1))

## [2.1.5](https://github.com/getappmap/appmap-python/compare/v2.1.4...v2.1.5) (2024-08-05)


### Bug Fixes

* reenable instrumentation of properties ([7b3119a](https://github.com/getappmap/appmap-python/commit/7b3119a4fdf60e19a28a279d4ba6afe379925e14))

## [2.1.4](https://github.com/getappmap/appmap-python/compare/v2.1.3...v2.1.4) (2024-07-26)


### Bug Fixes

* disable property instrumentation by default ([a280300](https://github.com/getappmap/appmap-python/commit/a2803003a57b1aabc87cadc755786613e2709ff2))

## [2.1.3](https://github.com/getappmap/appmap-python/compare/v2.1.2...v2.1.3) (2024-07-26)


### Bug Fixes

* add APPMAP_INSTRUMENT_PROPERTIES ([11b6307](https://github.com/getappmap/appmap-python/commit/11b6307cf2bdbfae50f30d4f329e6ba3ac6f4035))
* add ruff ([ac94204](https://github.com/getappmap/appmap-python/commit/ac94204d9bd35bf238865a7bf44cea039f8282fb))
* improve property handling ([5cce0f0](https://github.com/getappmap/appmap-python/commit/5cce0f0644eebf7d19bad5cda61726393cd7ba68))
* show config packages on startup ([feec761](https://github.com/getappmap/appmap-python/commit/feec761fefd5596c4fd7bde0cd9c3901e02791b3))
* try to avoid recording tests ([1847b0e](https://github.com/getappmap/appmap-python/commit/1847b0e7177327adc080854fbbec17b89166d516))

## [2.1.2](https://github.com/getappmap/appmap-python/compare/v2.1.1...v2.1.2) (2024-07-16)


### Bug Fixes

* catch BaseException from instrumented code ([c927f9c](https://github.com/getappmap/appmap-python/commit/c927f9cbbd809f683e8028505ef38bc3311fcf36))

## [2.1.1](https://github.com/getappmap/appmap-python/compare/v2.1.0...v2.1.1) (2024-07-15)


### Bug Fixes

* Flask events are ordered correctly ([f970fb7](https://github.com/getappmap/appmap-python/commit/f970fb7828edc3e5d19aa03e48e9302077d58614))
* only instrument property functions once ([23b52b5](https://github.com/getappmap/appmap-python/commit/23b52b507eedfb42a15e93a5e7ce1a5fc1d3edad))

# [2.1.0](https://github.com/getappmap/appmap-python/compare/v2.0.10...v2.1.0) (2024-07-03)


### Features

* instrument properties ([d69b6e1](https://github.com/getappmap/appmap-python/commit/d69b6e1648bd647b91ca4f9ef75300af7e015bfb))

## [2.0.10](https://github.com/getappmap/appmap-python/compare/v2.0.9...v2.0.10) (2024-06-21)


### Bug Fixes

* request recording in unittest setUp method ([1ee69cb](https://github.com/getappmap/appmap-python/commit/1ee69cb39b8be8e97b1498218b4ff3a4b9b1c3ee))

## [2.0.9](https://github.com/getappmap/appmap-python/compare/v2.0.8...v2.0.9) (2024-06-20)


### Bug Fixes

* appmap breaks vscode python extension starting a REPL ([c179b86](https://github.com/getappmap/appmap-python/commit/c179b86a5769de90775f0d8848e8ad0422961dfe))

## [2.0.8](https://github.com/getappmap/appmap-python/compare/v2.0.7...v2.0.8) (2024-06-05)


### Bug Fixes

* move __reduce_ex__ up to ObjectProxy ([f4618b6](https://github.com/getappmap/appmap-python/commit/f4618b68bc9bc40ff54120385c1820896094bd2e))
* optionally disable schema render ([4e29c13](https://github.com/getappmap/appmap-python/commit/4e29c1321d0e52554a797efd4e5bdda240e2fe82))
* support APPMAP_MAX_TIME ([d60c528](https://github.com/getappmap/appmap-python/commit/d60c52813aec424de1db2b45bb5f13eb23965d61))

## [2.0.7](https://github.com/getappmap/appmap-python/compare/v2.0.6...v2.0.7) (2024-06-05)


### Bug Fixes

* max recursion depth exceeded ([4223079](https://github.com/getappmap/appmap-python/commit/42230798cda296e31d437b93593e87760a498fad))

## [2.0.6](https://github.com/getappmap/appmap-python/compare/v2.0.5...v2.0.6) (2024-05-31)


### Bug Fixes

* use an RLock in SharedRecorder._add_event ([ec1f95d](https://github.com/getappmap/appmap-python/commit/ec1f95debdd3524b688793459be490432895d57c))

## [2.0.5](https://github.com/getappmap/appmap-python/compare/v2.0.4...v2.0.5) (2024-05-30)


### Bug Fixes

* appmap.Recording is available even when APPMAP=[secure] ([6bb7687](https://github.com/getappmap/appmap-python/commit/6bb7687412808c1d10a5d705ab0b1983868bb576))

## [2.0.4](https://github.com/getappmap/appmap-python/compare/v2.0.3...v2.0.4) (2024-05-29)


### Bug Fixes

* optionally limit number of events collected ([7c17a38](https://github.com/getappmap/appmap-python/commit/7c17a383fc849474ac44239abc6fb9f173f97edd))

## [2.0.3](https://github.com/getappmap/appmap-python/compare/v2.0.2...v2.0.3) (2024-05-28)


### Bug Fixes

* ask pytest not to rewrite our modules ([aae5dea](https://github.com/getappmap/appmap-python/commit/aae5dea50217568c67ccd312558c5e818f49b4ca))

## [2.0.2](https://github.com/getappmap/appmap-python/compare/v2.0.1...v2.0.2) (2024-05-27)


### Bug Fixes

* expect a missing config file ([9cb20a4](https://github.com/getappmap/appmap-python/commit/9cb20a4e09f4084bb11fa117016d6b418bc03651))

## [2.0.1](https://github.com/getappmap/appmap-python/compare/v2.0.0...v2.0.1) (2024-05-23)


### Bug Fixes

* completely disable record-by-default ([27e1bb4](https://github.com/getappmap/appmap-python/commit/27e1bb40734213ad100f27e024337e3d2e484c3e))
* handle non json serializable types ([b4fedc6](https://github.com/getappmap/appmap-python/commit/b4fedc6c8d22082c9640d03caa8fbf12121fe8f9))

# [2.0.0](https://github.com/getappmap/appmap-python/compare/v1.24.1...v2.0.0) (2024-05-23)


### Bug Fixes

* combine testing-related env vars ([500fe55](https://github.com/getappmap/appmap-python/commit/500fe55f06c536611e3e292b22a8fade62101afe))
* enabling process recording disables others ([74b2ee1](https://github.com/getappmap/appmap-python/commit/74b2ee15bfc380ee44ef74905e880541028f4c3b))
* honor APPMAP_RECORD_REQUESTS when testing ([2df0f37](https://github.com/getappmap/appmap-python/commit/2df0f37474d1cd26bdfdbb45baf4fd2c9c9c982f))


### Features

* disable record by default ([57b3910](https://github.com/getappmap/appmap-python/commit/57b3910a48cea8582612772d79abacc53b5b73d5))


### BREAKING CHANGES

* disable record by default

## [1.24.1](https://github.com/getappmap/appmap-python/compare/v1.24.0...v1.24.1) (2024-05-20)


### Bug Fixes

* find a config in the repo root ([b9ecced](https://github.com/getappmap/appmap-python/commit/b9ecced9407e59a302750615be66b08ad679ddb4))

# [1.24.0](https://github.com/getappmap/appmap-python/compare/v1.23.0...v1.24.0) (2024-05-17)


### Bug Fixes

* improve handling of unset APPMAP ([bbeee65](https://github.com/getappmap/appmap-python/commit/bbeee653a04df9dafb7e4b8c04db023b3f9be210))


### Features

* append to a single log file ([cacc62f](https://github.com/getappmap/appmap-python/commit/cacc62f9ba6811c45e3bebe8849ad48800be60f9))

# [1.23.0](https://github.com/getappmap/appmap-python/compare/v1.22.0...v1.23.0) (2024-05-16)


### Features

* check malformed path entries ([f7937ee](https://github.com/getappmap/appmap-python/commit/f7937eeffa4e690c57b3154847cc4b93c6187068))

# [1.22.0](https://github.com/getappmap/appmap-python/compare/v1.21.0...v1.22.0) (2024-05-15)


### Features

* search for config file ([4555c82](https://github.com/getappmap/appmap-python/commit/4555c82c156d24475a5974566f5d531f5cc2fd69))

# [1.21.0](https://github.com/getappmap/appmap-python/compare/v1.20.1...v1.21.0) (2024-04-29)


### Features

* add runner, get ready for v2 ([670660f](https://github.com/getappmap/appmap-python/commit/670660f4f1202f0a255d8f3ebcd11a4970090cca))

## [1.20.1](https://github.com/getappmap/appmap-python/compare/v1.20.0...v1.20.1) (2024-04-10)


### Bug Fixes

* don't create a log file by default ([1fac839](https://github.com/getappmap/appmap-python/commit/1fac839d0e5d053e26597c09c4451aac7f227ca2))

# [1.20.0](https://github.com/getappmap/appmap-python/compare/v1.19.1...v1.20.0) (2024-03-15)


### Bug Fixes

* log to a file by default ([3da004f](https://github.com/getappmap/appmap-python/commit/3da004f4ba67b7e3a923fc76ef733eec51a496c7))


### Features

* FastAPI support ([3dba2a2](https://github.com/getappmap/appmap-python/commit/3dba2a2561e51a6fe63c68dc870f817391c2bb0f))

## [1.19.1](https://github.com/getappmap/appmap-python/compare/v1.19.0...v1.19.1) (2024-02-29)


### Bug Fixes

* add TRACE log level ([778c6e3](https://github.com/getappmap/appmap-python/commit/778c6e3ecea63f45a17e4c52bca8a31f4d9bb073))
* drop Flask 1 ([5a28dc7](https://github.com/getappmap/appmap-python/commit/5a28dc733d684a9caa15fac7d16a9a82477dd8ca))
* drop python 3.7 support ([99d33c9](https://github.com/getappmap/appmap-python/commit/99d33c9de1e5aea980c6a8561e7822f9359bb76d))
* Flask integration should record exceptions ([2e89cfa](https://github.com/getappmap/appmap-python/commit/2e89cfaf3afc55901dfb9cbbe6fabde5d86c35ac))

# [1.19.0](https://github.com/getappmap/appmap-python/compare/v1.18.4...v1.19.0) (2024-02-13)


### Bug Fixes

* get rid of unused metadata fields ([87efc91](https://github.com/getappmap/appmap-python/commit/87efc91b262c607b38f5f38eeb5c3c9942074147))


### Features

* add process recording ([81e5226](https://github.com/getappmap/appmap-python/commit/81e52268ba87905b2f973a120020aec74d09bece))

## [1.18.4](https://github.com/getappmap/appmap-python/compare/v1.18.3...v1.18.4) (2024-02-10)


### Bug Fixes

* replace logging.info with logger in env.py ([68b6bca](https://github.com/getappmap/appmap-python/commit/68b6bca98d64bc55c7b5d0e67900791469fb5d2d))

## [1.18.3](https://github.com/getappmap/appmap-python/compare/v1.18.2...v1.18.3) (2024-02-05)


### Bug Fixes

* support python 3.12 ([136b47b](https://github.com/getappmap/appmap-python/commit/136b47b14d390768fe8448f4649cdab838b70a92))

## [1.18.2](https://github.com/getappmap/appmap-python/compare/v1.18.1...v1.18.2) (2024-01-22)


### Bug Fixes

* Exclude the appmap test files ([#271](https://github.com/getappmap/appmap-python/issues/271)) ([9ff91b8](https://github.com/getappmap/appmap-python/commit/9ff91b8ed73e8e7b7e01c1e28a829eecdf1e8581))

## [1.18.1](https://github.com/getappmap/appmap-python/compare/v1.18.0...v1.18.1) (2023-11-05)


### Bug Fixes

* move source_location property to metadata ([7ac2aa0](https://github.com/getappmap/appmap-python/commit/7ac2aa042ce89bff30dd0bd71ca3d6220d1c8ba4))

# [1.18.0](https://github.com/getappmap/appmap-python/compare/v1.17.1...v1.18.0) (2023-11-04)


### Features

* add noappmap decorator ([d8aa5d9](https://github.com/getappmap/appmap-python/commit/d8aa5d92535363b800fb26ac38686c4c51afa0ee))

## [1.17.1](https://github.com/getappmap/appmap-python/compare/v1.17.0...v1.17.1) (2023-10-27)


### Bug Fixes

* make sure functions can be excluded ([d7518ee](https://github.com/getappmap/appmap-python/commit/d7518ee361dc4912b94ef4a1b87eb2d1b3a8be2b))

# [1.17.0](https://github.com/getappmap/appmap-python/compare/v1.16.0...v1.17.0) (2023-07-11)


### Features

* Report test_failure when a test fails ([d5757f4](https://github.com/getappmap/appmap-python/commit/d5757f44500f954e84a1ff8965e4da888bcb33ae)), closes [#248](https://github.com/getappmap/appmap-python/issues/248)

# [1.16.0](https://github.com/getappmap/appmap-python/compare/v1.15.2...v1.16.0) (2023-05-25)


### Bug Fixes

* handle 3.11 find_spec implementation ([c62e64e](https://github.com/getappmap/appmap-python/commit/c62e64e04d3911e37e17a7254ed44f4975b4dd11))
* relax restriction on packaging to >=19.0 ([affdbda](https://github.com/getappmap/appmap-python/commit/affdbda3e3e492eeaadc9abe4803e0728a663f2b))
* update unittest integration for python 3.11 ([bd9598b](https://github.com/getappmap/appmap-python/commit/bd9598bea8576641b923d157690937bc2e07d3df))


### Features

* support python 3.11 ([15b0ddc](https://github.com/getappmap/appmap-python/commit/15b0ddc94397b78912bca2ad5a1bc68d4f3f2942))

## [1.15.2](https://github.com/getappmap/appmap-python/compare/v1.15.1...v1.15.2) (2023-05-23)


### Bug Fixes

* Don't record requests in test cases ([114038c](https://github.com/getappmap/appmap-python/commit/114038c704fed31a72d58edfa959bf2f0c10eef3)), closes [#234](https://github.com/getappmap/appmap-python/issues/234)

## [1.15.1](https://github.com/getappmap/appmap-python/compare/v1.15.0...v1.15.1) (2023-05-10)


### Bug Fixes

* pin urllib3 to v1 ([d1ed73c](https://github.com/getappmap/appmap-python/commit/d1ed73c23fb7d923c5c3a52586fc7474418337e2))
* support Werkzeug v2.3 ([28b5461](https://github.com/getappmap/appmap-python/commit/28b54615fd62f3c1430f013f9fa79645823bc2cf))

# [1.15.0](https://github.com/getappmap/appmap-python/compare/v1.14.2...v1.15.0) (2023-03-13)


### Features

* add schema to event parameters ([838f2de](https://github.com/getappmap/appmap-python/commit/838f2de8addd98f734e15ccc0ad90fc0d73553fc))

## [1.14.2](https://github.com/getappmap/appmap-python/compare/v1.14.1...v1.14.2) (2023-03-08)


### Bug Fixes

* bump version of "packaging" ([3224bf6](https://github.com/getappmap/appmap-python/commit/3224bf6bfee49ea95a04663d21442137535e1346))

## [1.14.1](https://github.com/getappmap/appmap-python/compare/v1.14.0...v1.14.1) (2023-02-23)


### Bug Fixes

* improve Django path normalization ([f536bd3](https://github.com/getappmap/appmap-python/commit/f536bd383a91b3882a10b0b691d186ce7537785d))

# [1.14.0](https://github.com/getappmap/appmap-python/compare/v1.13.3...v1.14.0) (2023-02-09)


### Bug Fixes

* Recorder._start_recording uses logger.debug ([6c9b5cc](https://github.com/getappmap/appmap-python/commit/6c9b5ccdcd4265876b2a69677b00c6f256103ee1))


### Features

* Add label definitions ([d53f3f4](https://github.com/getappmap/appmap-python/commit/d53f3f4ba2d69d5068a50539a6fdbbb9a4ee53d5))

## [1.13.3](https://github.com/getappmap/appmap-python/compare/v1.13.2...v1.13.3) (2023-02-09)


### Bug Fixes

* don't instrument extra class members ([68ff82e](https://github.com/getappmap/appmap-python/commit/68ff82eee4600386766ea45af4ab691666abcbad))

## [1.13.2](https://github.com/getappmap/appmap-python/compare/v1.13.1...v1.13.2) (2023-01-19)


### Bug Fixes

* enable logging from _appmap module ([f00fd2d](https://github.com/getappmap/appmap-python/commit/f00fd2d111ddc7b38953c9585f2f751feaf80157))
* instrument functions based on label config ([4f491cc](https://github.com/getappmap/appmap-python/commit/4f491cc4bb57f161c9470e9683dfc89f8ae6b7ad))

## [1.13.1](https://github.com/getappmap/appmap-python/compare/v1.13.0...v1.13.1) (2023-01-11)


### Bug Fixes

* improve handling of application/json requests ([7f4dc2d](https://github.com/getappmap/appmap-python/commit/7f4dc2d42efa26f4e32e6685c7afc9aec71e1766))

# [1.13.0](https://github.com/getappmap/appmap-python/compare/v1.12.8...v1.13.0) (2023-01-04)


### Features

* record unittest testcases by default ([f40434d](https://github.com/getappmap/appmap-python/commit/f40434d74731cc76ac1ed2cfea41a8655c6f6c1e))

## [1.12.8](https://github.com/getappmap/appmap-python/compare/v1.12.7...v1.12.8) (2022-12-12)


### Bug Fixes

* don't fail on unittest subtests ([4832377](https://github.com/getappmap/appmap-python/commit/4832377884780acf8be41f6fd7099737170ea6e2))

## [1.12.7](https://github.com/getappmap/appmap-python/compare/v1.12.6...v1.12.7) (2022-12-09)


### Bug Fixes

* set appmap_dir, language in default config ([7383c18](https://github.com/getappmap/appmap-python/commit/7383c18344f1567f7e91651144f1754b066754a5))

## [1.12.6](https://github.com/getappmap/appmap-python/compare/v1.12.5...v1.12.6) (2022-12-07)


### Bug Fixes

* allow instrumented functions to be pickled ([1c04dc0](https://github.com/getappmap/appmap-python/commit/1c04dc005cb49aa36cc6fa40952c743672882940))

## [1.12.5](https://github.com/getappmap/appmap-python/compare/v1.12.4...v1.12.5) (2022-12-04)


### Bug Fixes

* log at warning by default ([450c3b9](https://github.com/getappmap/appmap-python/commit/450c3b9043068f2ac0b88195fa9bcc0be9542efa))

## [1.12.4](https://github.com/getappmap/appmap-python/compare/v1.12.3...v1.12.4) (2022-11-21)


### Bug Fixes

* allow scripts to be run with -m ([dc75658](https://github.com/getappmap/appmap-python/commit/dc75658090c6baab7fd214c4f1221098917c1939))

## [1.12.3](https://github.com/getappmap/appmap-python/compare/v1.12.2...v1.12.3) (2022-11-08)


### Bug Fixes

* handle a tuple value for settings.MIDDLEWARE ([672e078](https://github.com/getappmap/appmap-python/commit/672e0786b75eb120f211e5eaf3d30fa839d8a8d3))

## [1.12.2](https://github.com/getappmap/appmap-python/compare/v1.12.1...v1.12.2) (2022-11-08)


### Bug Fixes

* allow concurrent remote and request recording ([65f106b](https://github.com/getappmap/appmap-python/commit/65f106bc107f80110b39f5647716c91f9f6a0929))
* use log level INFO by default ([6604dd4](https://github.com/getappmap/appmap-python/commit/6604dd4755dcc44eb4e0011568d81900a3afd17e))

## [1.12.1](https://github.com/getappmap/appmap-python/compare/v1.12.0...v1.12.1) (2022-11-04)


### Bug Fixes

* Avoid calling __class__ when describing values ([91be26e](https://github.com/getappmap/appmap-python/commit/91be26eecd04c2291c86e43043f1aee8a29f510f))

# [1.12.0](https://github.com/getappmap/appmap-python/compare/v1.11.0...v1.12.0) (2022-10-25)


### Bug Fixes

* improve Flask normalized-path parsing ([712dbd5](https://github.com/getappmap/appmap-python/commit/712dbd55dd7d00486ef6e7db7f74ce2e2aee73a8))
* inject Django middleware automatically ([f15e591](https://github.com/getappmap/appmap-python/commit/f15e5917cbed5e10fb973edff67e5e731edc0de4))


### Features

* support Flask 2 ([26cde29](https://github.com/getappmap/appmap-python/commit/26cde29b5bf857482c717cf8fd8b3da1740e3e74))

# [1.11.0](https://github.com/getappmap/appmap-python/compare/v1.10.4...v1.11.0) (2022-10-25)


### Features

* Don't show noise in the console. ([f763eb6](https://github.com/getappmap/appmap-python/commit/f763eb63a4d76d6f54ec0985d758803475850553))

## [1.10.4](https://github.com/getappmap/appmap-python/compare/v1.10.3...v1.10.4) (2022-10-23)


### Bug Fixes

* remove try ... except from appmap.pth ([4710280](https://github.com/getappmap/appmap-python/commit/4710280685adbe7d7c955ce960313a77bd1a26b8))

## [1.10.3](https://github.com/getappmap/appmap-python/compare/v1.10.2...v1.10.3) (2022-10-20)


### Bug Fixes

* use default values when config is incomplete ([8a307a2](https://github.com/getappmap/appmap-python/commit/8a307a246c2e3ef7c3ed2dc5b490c06def674eb3))

## [1.10.2](https://github.com/getappmap/appmap-python/compare/v1.10.1...v1.10.2) (2022-10-19)


### Bug Fixes

* capture events for app code once again ([5fd3797](https://github.com/getappmap/appmap-python/commit/5fd37974868509dfa24dd8eccd4bf7d61a8693fc))

## [1.10.1](https://github.com/getappmap/appmap-python/compare/v1.10.0...v1.10.1) (2022-10-13)


### Bug Fixes

* Require PyYAML >=5.3.0 rather than ^5.3.0 because some packages that use appmap-python ask for PyYAML==6.0 ([abfa874](https://github.com/getappmap/appmap-python/commit/abfa87480eaac53832cee68ec38cade1235d2efc))

# [1.10.0](https://github.com/getappmap/appmap-python/compare/v1.9.1...v1.10.0) (2022-10-12)


### Bug Fixes

* For Flask always set a before_request and an after_request handler ([fb73d80](https://github.com/getappmap/appmap-python/commit/fb73d804ce127ac7223a45c3fb55834eee437a50))
* Remove a testcase for Flask and a testcase for Django because it's not possible to test for appmap_not_enabled_requests_enabled_and_remote: when APPMAP=false the routes for remote recording are disabled ([5817b6e](https://github.com/getappmap/appmap-python/commit/5817b6e656371bdcec973cd239c98985784d11a6))
* The remote recording routes for Flask are enabled only if APPMAP=true ([45a297b](https://github.com/getappmap/appmap-python/commit/45a297bf375a20987ab083295b1678b5ef853fcc))


### Features

* record by default ([209f118](https://github.com/getappmap/appmap-python/commit/209f118109ba89eac96133526ac5c258d03a03a7))

## [1.9.1](https://github.com/getappmap/appmap-python/compare/v1.9.0...v1.9.1) (2022-10-11)


### Bug Fixes

* make sure event ids aren't duplicated ([4404fb0](https://github.com/getappmap/appmap-python/commit/4404fb004639b33c5be579387137d566c99af631))

# [1.9.0](https://github.com/getappmap/appmap-python/compare/v1.8.4...v1.9.0) (2022-10-03)


### Bug Fixes

* Create requests appmap filename in the same format as appmap-ruby. ([22df520](https://github.com/getappmap/appmap-python/commit/22df5201c21a74e983e239ca863fa167c9b823e3))
* skip the test_record_request testcases until _EventIds stops producing duplicate ids. ([5a8b461](https://github.com/getappmap/appmap-python/commit/5a8b46168ea7a27f287323c4923ca8e5b78e4baa))


### Features

* when APPMAP_RECORD_REQUESTS is set record each request in a separate file ([cd2ef5c](https://github.com/getappmap/appmap-python/commit/cd2ef5ccd9a7704fed4f167333dda546ab56c2f6))

## [1.8.4](https://github.com/getappmap/appmap-python/compare/v1.8.3...v1.8.4) (2022-10-03)


### Bug Fixes

* set global python version for builds ([be59666](https://github.com/getappmap/appmap-python/commit/be59666114133186f281dc5619ea2478a8c34eea))

## [1.8.3](https://github.com/getappmap/appmap-python/compare/v1.8.2...v1.8.3) (2022-10-03)


### Bug Fixes

* update Travis config to use 3.9 ([505f9fa](https://github.com/getappmap/appmap-python/commit/505f9fa949be6e6810137acc69fb7737655be79c))

## [1.8.2](https://github.com/getappmap/appmap-python/compare/v1.8.1...v1.8.2) (2022-10-03)


### Bug Fixes

* remove some debugging ([6e03c7e](https://github.com/getappmap/appmap-python/commit/6e03c7ef056b187dd0304c832a37d3602e359029))

## [1.8.1](https://github.com/getappmap/appmap-python/compare/v1.8.0...v1.8.1) (2022-10-03)


### Bug Fixes

* 3.10 support, wrap exec_module properly ([f50007b](https://github.com/getappmap/appmap-python/commit/f50007b0b6beeaddc52ae43e4ed1146f5609d19d))

# [1.8.0](https://github.com/getappmap/appmap-python/compare/v1.7.0...v1.8.0) (2022-09-27)


### Features

* automatically create appmap.yml ([1b935f5](https://github.com/getappmap/appmap-python/commit/1b935f5770a7f7c88c047eee1038f5d57c8b4f21))

# [1.7.0](https://github.com/getappmap/appmap-python/compare/v1.6.0...v1.7.0) (2022-09-27)


### Features

* update to v1.9.0 of appmap spec ([b95c260](https://github.com/getappmap/appmap-python/commit/b95c260ddcb9efdbe2e9266db814043917b714c4))

# [1.6.0](https://github.com/getappmap/appmap-python/compare/v1.5.3...v1.6.0) (2022-09-26)


### Features

* Allow per-thread recording ([e1bfd94](https://github.com/getappmap/appmap-python/commit/e1bfd94b93c94909819e5a963c2ddfe17c063c53))

## [1.5.3](https://github.com/getappmap/appmap-python/compare/v1.5.2...v1.5.3) (2022-09-22)


### Bug Fixes

* Instrumented functions can now be deepcopy'ed ([3bc9da6](https://github.com/getappmap/appmap-python/commit/3bc9da686bccbb97c1ca5991ff3884fab6dcd47c))

## [1.5.2](https://github.com/applandinc/appmap-python/compare/v1.5.1...v1.5.2) (2022-09-16)


### Bug Fixes

* Avoid querying database version when executing client queries ([51ffd44](https://github.com/applandinc/appmap-python/commit/51ffd44368efa5ddbb0bfa174f1681e60e60eb59)), closes [#158](https://github.com/applandinc/appmap-python/issues/158)
* drop python 3.6 ([d9c70a3](https://github.com/applandinc/appmap-python/commit/d9c70a36cb41f22f448bd70e7969336549b0227b))

## [1.5.1](https://github.com/applandinc/appmap-python/compare/v1.5.0...v1.5.1) (2022-02-02)


### Bug Fixes

* Don't hook unittest tests when disabled ([b6feab6](https://github.com/applandinc/appmap-python/commit/b6feab6a7d12ef9df86fffcf0c1155a3e89b6a5a))
* Handle finder that's a functools.partial ([913c7a9](https://github.com/applandinc/appmap-python/commit/913c7a9d16100060ae7f8e054690ca47ae99c042))

# [1.5.0](https://github.com/applandinc/appmap-python/compare/v1.4.0...v1.5.0) (2021-12-16)


### Bug Fixes

* Swap label declarations in the config file ([2214599](https://github.com/applandinc/appmap-python/commit/2214599f7f48d1749a610029a6fe41b0ccaecd0d))


### Features

* Preset labels for known library functions ([3b49925](https://github.com/applandinc/appmap-python/commit/3b49925c072d0c5f40e2a7e33a5d2f956100e002))

# [1.4.0](https://github.com/applandinc/appmap-python/compare/v1.3.2...v1.4.0) (2021-12-07)


### Bug Fixes

* Don't duplicate class name in fully qualified name ([d7f4bd3](https://github.com/applandinc/appmap-python/commit/d7f4bd38d66b4472fe177711ded225070c9341df))
* Don't include function labels in call events ([6f00a24](https://github.com/applandinc/appmap-python/commit/6f00a247547b2354199cf4618207395f034ecf3f))


### Features

* Allow specifying function labels in the config file ([3ae44f4](https://github.com/applandinc/appmap-python/commit/3ae44f43fe368af0b398671bc9623e0bc55e509f))

## [1.3.2](https://github.com/applandinc/appmap-python/compare/v1.3.1...v1.3.2) (2021-11-09)


### Bug Fixes

* Honor APPMAP env var when config is present ([45cac9d](https://github.com/applandinc/appmap-python/commit/45cac9d4d96775deb3ade357e7c265228356f862))

## [1.3.1](https://github.com/applandinc/appmap-python/compare/v1.3.0...v1.3.1) (2021-10-25)


### Bug Fixes

* Loosen version for some dependencies ([1159985](https://github.com/applandinc/appmap-python/commit/1159985aeb9c97972c2c40164c30c7177618ab2f))

# [1.3.0](https://github.com/applandinc/appmap-python/compare/v1.2.1...v1.3.0) (2021-09-26)


### Bug Fixes

* appmap-agent-init excludes more directories ([3691fb1](https://github.com/applandinc/appmap-python/commit/3691fb1fb0c7e2809b8be3047f4b1df46c62e444))


### Features

* Add appmap-agent-validate ([9f8da52](https://github.com/applandinc/appmap-python/commit/9f8da520b45ff511c8a55ac621d36321fb317d31))

## [1.2.1] - 2021-09-24
### Added
- The `appmap-agent-init` and `appmap-agent-status` internal commands are now available
  for the code-editor extensions.

### Fixed
- [#141] Ensure `appmap.django.Middleware` is always in the middleware stack.
- [#138] Path normalization for django requests is now more robust.
- [#128] The error message for a missing config file now shows the full path where the
  file was expected to be found.

## 1.2.0 - 2021-09-24
- Pulled

## [1.1.0] - 2021-06-08
### Added
- [#55] Informative message is displayed when appmap.yml is missing.
- [#119] Record template rendering in Django and flask.

### Fixed
- [#70] Django integration now records an ExceptionEvent when an unhandled
  exception is raised within Django itself while processing a request.
- When an argument to a method is missing, don't raise an exception in the
  appmap code. Instead omit the missing parameter and allow the original
  function call to raise ArgumentError if appropriate.
- Handle the case when a method is called with self=None.
- Function signature reflection now follows wrappers. This allows eg. functions
  decorated with functools.lru_cache to have their parameters captured.

### Changed
- Update tox config to test Django 2.2

### Fixed
- [#122] Path normalization for Django requests works in the presence of included
  URLconfs.

## [1.0.0] - 2021-05-27
### Added
- [#105] django integration now captures `normalized_path_info` for `http_server_request`
  events.
- [#102] Function comments now appear in the `classMap`.
- [#3] Allow remote recording django apps.
- [#99] A recording is now created atomically. It is first written to a temp file, which is then
  renamed to the final file.
- Capture HTTP client request and response.
- [#101] Record test status (failed or succeeded) in test appmap metadata.
- [#108] Capture message parameters in Flask.
- Flask, Django and SQLAlchemy versions are now recorded in the metadata.

### Fixed
- When using `pytest` as the test driver, failed unittest cases appmaps are now recorded.
- [#91] Limit appmap file name length to 255 characters.
- [#104] The flask integration now formats parameters in `normalized_path_info` to match
  the appmap spec.
- Git metadata is now cached, preventing running git several times per test case.
- Fix a problem with Django JSON parameter capture preventing the application
  from accessing the request body.

## [0.10.0] - 2021-05-07
### Added
- [#90] Capture HTTP response headers in django and flask.

### Changed
- Headers such as Host, User-Agent, Authorization and Content-Type are no longer
  filtered out in HTTP event `headers` field.

### Fixed
- When using `pytest` as the test driver, make sure the test case decorator returns the
  correct value.

## [0.9.0] - 2021-05-03
### Added
- Attempting to start recording while recording is in progress will now raise a
  RuntimeError.
- [#77] Have the Django integration capture parameters of `http_server_request`s,
  recording them in the `message` attribute of the `call` event.
- [#83] Capture HTTP request headers in django and flask.
- [#53] Module-scoped functions are now recorded.
- [#64] Capture SQL queries in SQLAlchemy.
- [#58] Capture database type and version in Django and SQLAlchemy.

### Changed
- When using `pytest` to run `unittest` test cases, start recording by hooking the test
  case functions, rather than relying on our `unittest` integration.
- [#94] Drop support for python 3.5.
- Initialize settings controlled by environment variables on startup.
- Use repr() instead of str() for object stringification.

### Fixed
- `unittest` test cases run by the `unittest` test loader (e.g. by running `python -m
  unittest`) are now recorded correctly.
- `setUp` and `teardown` of `unittest` test cases are no longer captured.
- Fixed a crash when HTTP request doesn't match any route in Flask.
- Avoid capturing SQL queries run when fetching object representation in Django.

## [0.8.0] - 2021-04-04
### Fixed
- [#74] pytest integration works again
- [#72] Multiple calls into a shallow-tracked package are now recorded.

## [0.8.0.dev2] - 2021-03-26
### Added
- [#68] Support `APPMAP_DISPLAY_PARAMS`.

### Fixed
- [#69] django integration handles responses with missing `Content-Type`.

## [0.8.0.dev1] - 2021-03-25
### Added
- [#66] Path and line number of test function is now included in AppMap metadata, as
  `metadata.recording.source_location`.

### Fixed
- [#65] Wrapped functions with mismatched signatures no longer cause mapping failures.

## [0.7.0] - 2021-03-15
### Added
- [#2] [#28] Add flask integration

## [0.6.0] - 2021-03-10
### Added
- The `appmap.labels` decorator can now be applied to a function to specify labels that
  should appear in the AppMap.

### Fixed
- [#61] Don't modify an instrumented function's parameters when rendering them.
- Correct the structure of the `return_value` object in a `return` event.

## [0.5.0] - 2021-03-08
### Added
- Packages in config file can now be set for 'shallow' tracking. This eliminates most of
  the intrapackage execution flow from tracking and produces lighter appmaps where we're
  only interested in surface interaction with a third-party piece of code.
- [#48] Allow specifying distributions (aka. packages) as filters in appmap.yml.

## Fixed
- Fixed a problem where some entry points were missed in shallowly traced packages.
- Subsequent Recording()s now don't contain previously recorded events.

## [0.1.0.dev12] - 2021-03-05
### Fixed
- [#29] `call` events now show the parameters the function was called with.
- `return` events show the function's return value.
- The `exceptions` attribute of a `return` event now has the correct structure.
- [#46] Source file locations in an AppMap are now relative to the starting directory.
- [#54] Write metadata even if `git` can't be found on `PATH`.

## [0.1.0.dev11] - 2021-02-28
### Added
- [#5] *unittest* integration.

### Fixed
- [#50] Make sure we protect against rewrapping a metapath finder's exec_module function.

## [0.1.0.dev10] - 2021-02-24
### Fixed
- Choose the output directory on startup, make sure it's an absolute path.

### ## [0.1.0.dev9] - 2021-02-23
### Added
- Use tox for testing multiple versions of Python.

### Changed
- Relax the python version requirement to 3.5.

### Fixed
- Fix handling of builtin functions assigned as attributes of a class. They look like
  static methods, (i.e. `isinstance(m, (staticmethod, types.BuiltinMethodType))` is
  `True`), but they don't have a `__func__` attribute.

## [0.1.0.dev8] - 2021-02-22
- [#27] Capturing HTTP requests and responses when testing Django apps.

## [0.1.0.dev7] - 2021-02-18
### Added
- [#26] Capturing SQL queries when testing Django apps.

## [0.1.0.dev6] - 2021-02-16
### Added
- [#17] Add elapsed attribute to ReturnEvent
- [#8] Add git to metadata
- pytest integration
- Support `APPMAP_OUTPUT_DIR` environment variable. If set, specifies the root directory
  for writing AppMaps. If not set, defaults to `tmp/appmap`.

### Changed
- Added `About` section to the README

- Python 3.9.0 is now the minimum supported version.

- Use repr() instead of str() for receiver

  Use repr() instead of str() to get a string representation of an event's receiver. This
  works properly for flaskbb, and seems more correct in general.

  Also, add Event.__repr__.

- Simplify (and fix) logging configuration

  The code that configured logging was overly complex, and also buggy.  These changes
  simplify it, keep duplicate messages from being emitted, and properly allow per-module
  configuration of log level.

- Don't use inspect.isclass

  When testing to see if an object is a class, use type() instead of inpect.isclass. See
  the comment on appmap._implementation.recording.is_class for details.  Also, make sure
  ConfigFilter.wrap doesn't call the next filter for a function that it finds has already
  been wrapped.

### Fixed
- Fix classmap `function` entries

  Entries of type `function` in the classmap must have an attribute called "location", not
  "path" and "lineno" attributes. Now they do.

- Fix support for function exclusions specified in the config.

## [0.1.0.dev4] - 2021-01-11
### Added
- Add a deploy stage to the build
  With these changes, tagged versions will now be deployed to PyPI.
- Set the version from the git tag
  Before pushing a release, set the version based on the tag for the
  current build.

## [0.1.0.dev3] - 2021-01-09
### Added
- Configure stream for logging
  Allow the user to specify which stream (stdout, stderr) to use for
  logging. Also, raise a RuntimeError if an `excludes` attribute in
  `appmap.yml` is something other than an array.

### Changed
- Avoid recursion when inspecting a call's receiver.
  To generate a call event, `str()` and `repr()` are used to create the
  `receiver` attribute. These methods may have been instrumented, or may
  call instrumented methods. These changes add protection to make sure
  we avoid infinite recursion.
- Simplify classmap classes
  ClassMapDict now just subclasses dict, and ClassMapEntry and its
  subclasses are all dataclasses.
  Also fix a couple of minor issues identified during review. Thanks
  @virajkanwade for the suggestions.

### Fixed
- Handle missing source info
  Make sure we can generate CallEvents even if `inspect` can't find the
  source or line number information.
- Reinitialize implementation before each test
  Make sure appmap._implementation.initialize gets called before each
  test, to start with a clean slate. To make this easier, package the
  tests in classes that inherit from a base class that implements
  setup_method.
- Fix handling of sys.meta_path
  The elements of sys.meta_path can be either classes or objects. These
  changes ensure that instances are handled correctly. When an instance is
  encountered, its find_spec method will be wrapped. Additionally, it will
  be marked to ensure that it won't be wrapped again if it's revisited.

## [v0.1.0.dev1] - 2021-01-08
### Added
- Add package mgmt, linting, and testing. Use poetry to manage dependencies, pylint for linting, and pytest for
testing. Also adds a Travis config to run them all.
- Completely rework recording. Generates AppMaps with `metadata`, `event`, and `classMap`
  sections. Currently missing significant parts of each, but they're complete enough to
  upload to [https://app.land](https://app.land).
- Add contributor documentation
- Deploy release to PyPI


[1.2.1]: https://github.com/applandinc/appmap-python/compare/1.1.0...1.2.1
[1.1.0]: https://github.com/applandinc/appmap-python/compare/1.0.0...1.1.0
[1.0.0]: https://github.com/applandinc/appmap-python/compare/0.10.0...1.0.0
[0.10.0]: https://github.com/applandinc/appmap-python/compare/0.9.0...0.10.0
[0.9.0]: https://github.com/applandinc/appmap-python/compare/0.8.0...0.9.0
[0.8.0]: https://github.com/applandinc/appmap-python/compare/0.8.0.dev2...0.8.0
[0.8.0.dev2]: https://github.com/applandinc/appmap-python/compare/0.8.0.dev1...0.8.0.dev2
[0.8.0.dev1]: https://github.com/applandinc/appmap-python/compare/0.7.0...0.8.0.dev1
[0.7.0]: https://github.com/applandinc/appmap-python/compare/0.6.0...0.7.0
[0.6.0]: https://github.com/applandinc/appmap-python/compare/0.5.0...0.6.0
[0.5.0]: https://github.com/applandinc/appmap-python/compare/0.1.0.dev12...0.5.0
[0.1.0.dev12]: https://github.com/applandinc/appmap-python/compare/0.1.0.dev11...0.1.0.dev12
[0.1.0.dev11]: https://github.com/applandinc/appmap-python/compare/0.1.0.dev10...0.1.0.dev11
[0.1.0.dev10]: https://github.com/applandinc/appmap-python/compare/0.1.0.dev9...0.1.0.dev10
[0.1.0.dev9]: https://github.com/applandinc/appmap-python/compare/0.1.0.dev8...0.1.0.dev9
[0.1.0.dev8]: https://github.com/applandinc/appmap-python/compare/0.1.0.dev7...0.1.0.dev8
[0.1.0.dev7]: https://github.com/applandinc/appmap-python/compare/0.1.0.dev6...0.1.0.dev7
[0.1.0.dev6]: https://github.com/applandinc/appmap-python/compare/0.1.0.dev4...0.1.0.dev6
[0.1.0.dev4]: https://github.com/applandinc/appmap-python/compare/0.1.0.dev3...0.1.0.dev4
[0.1.0.dev3]: https://github.com/applandinc/appmap-python/compare/v0.1.0.dev1...0.1.0.dev3
[v0.1.0.dev1]: https://github.com/applandinc/appmap-python/releases/tag/v0.1.0.dev1
