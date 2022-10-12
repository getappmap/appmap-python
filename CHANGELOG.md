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
