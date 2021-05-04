# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Capture HTTP client request and response.

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


[Unreleased]: https://github.com/applandinc/appmap-python/compare/0.10.0...HEAD
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
