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
