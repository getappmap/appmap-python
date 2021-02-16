# appmap-python

## Configuration
Add your modules as `path` entries in `appmap.yml`:

```yaml
name: my_python_app
packages:
- path: app.mod1
- path: app.mod2
  exclude:
  - MyClass
  - MyOtherClass.my_instance_method
  - MyOtherClass.my_class_method
```

Note that `exclude`s are resolved relative to the associated path. So, for example, this
configuration excludes `app.mod2.MyClass`

## Environment Variables

* `APPMAP` if `true`, code will be instrumented and AppMaps will be generated. Not
  case-sensitive, defaults to 'false'.

* `APPMAP_CONFIG` specifies the configuration file to use. Defaults to `appmap.yml` in the
  current directory
  
* `APPMAP_LOG_LEVEL` specifies log level to use, from the set `CRITICAL`, `ERROR`,
  `WARNING`, `INFO`, `DEBUG`. Not case-sensitive, defaults to `WARNING`.
  
* `APPMAP_OUTPUT_DIR` specifies the root directory for writing AppMaps. Defaults to
  `tmp/appmap`.
  
## Test Frameworks
`appmap-python` supports recording [pytest](https://pytest.org) and `unittest`[future
work] test cases.

### pytest
`appmap-python` is a `pytest` plugin. When it's installed in a project that uses
`pytest`, it will be available to generate AppMaps.

```shell
root@e9987eaa93c8:/src/appmap/test/data/pytest# pip show appmap
Name: appmap
Version: 0.0.0
Summary: Create AppMap files by recording a Python application.
Home-page: None
Author: Alan Potter
Author-email: alan@app.land
License: None
Location: /usr/local/lib/python3.9/site-packages
Requires: orjson, PyYAML, inflection
Required-by:
root@e9987eaa93c8:/src/appmap/test/data/pytest# APPMAP=true APPMAP_LOG_LEVEL=info pytest -svv
[2021-02-10 11:37:59,345] INFO root: appmap enabled: True
[2021-02-10 11:37:59,350] INFO appmap._implementation.configuration: ConfigFilter, includes {'simple'}
[2021-02-10 11:37:59,350] INFO appmap._implementation.configuration: ConfigFilter, excludes set()
===================================================================== test session starts =====================================================================
platform linux -- Python 3.9.1, pytest-6.2.2, py-1.10.0, pluggy-0.13.1 -- /usr/local/bin/python
cachedir: .pytest_cache
rootdir: /src, configfile: pytest.ini
plugins: appmap-0.0.0
collected 1 item

test_simple.py::test_hello_world [2021-02-10 11:37:59,482] INFO appmap.pytest: starting recording /tmp/pytest/test_hello_world.appmap.json
[2021-02-10 11:37:59,484] INFO appmap._implementation.configuration: included class simple.Simple
[2021-02-10 11:37:59,484] INFO appmap._implementation.configuration: included function simple.Simple.hello
[2021-02-10 11:37:59,489] INFO appmap._implementation.configuration: included function simple.Simple.hello_world
[2021-02-10 11:37:59,490] INFO appmap._implementation.configuration: included function simple.Simple.world
[2021-02-10 11:37:59,828] INFO appmap.pytest: wrote recording /tmp/pytest/test_hello_world.appmap.json
PASSED

====================================================================== 1 passed in 0.45s ======================================================================
```

### unittest [future work]
`import appmap.unittest`. Instruments subclasses of `unittest.TestCase` and records each
`test_*` function in the subclasses.

### Run your tests
Once you've configured your tests to generate AppMaps, run the tests with the
`APPMAP=true` in the environment. For example, to run a pytest test suite:

```sh
$ APPMAP=true pytest
```


## Remote Recording [future work]
`appmap-python` supports remote recording of Django and Flask web applications. Import the
appropriate remote recording support into your web app.

### Django
`import appmap.django`. Adds `/_appmap/record` routes to a Django app.

## Flask
`import appmap.flask`. Adds `/_appmap/record` routes to a Flask app.

## Run your web app [future work]
Once you've configured your web app to add the remote-recording routes, you can use the
routes to manage recordings. The browser extension, appland CLI, or just plain cURL will
all work for this.

As when running tests, start the web server with `APPMAP=true` in the environment. For
example, to start a Django app:

```sh
$ APPMAP=true python manage.py runserver
```

An app with remote recording enabled supports these routes:

* `POST /_appmap/record`
  Starts a new recording

  200 if the recording was started successfully
  409 if there's already a recording in progress

* `GET /_appmap/record`
  Returns JSON describing current recording state
  200 with body

  ```json
  {
    "enabled": true
  }
  ```
  `enabled` indicates whether recording has been enabled

* `DELETE /_appmap/record`
  Returns AppMap as JSON
  200 with AppMap as body
  404 if there's no recording in progress

## Development

### Dependency management

[poetry](https://https://python-poetry.org/) for dependency management:

```
% brew install poetry
% cd appmap-python
% poetry install
```

### Linting
[pylint](https://www.pylint.org/) for linting:

```
% cd appmap-python
% poetry run pylint appmap

--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

```

[Note that the current configuration requires a 10.0 for the Travis build to pass. To make
this easier to achieve, convention and refactoring checks have both been disabled. They
should be reenabled as soon as possible.]


### Testing
[pytest](https://docs.pytest.org/en/stable/) for testing:

```
% cd appmap-python
% APPMAP=true poetry run pytest
```

### Code Coverage
[coverage](https://coverage.readthedocs.io/) for coverage:

```
% cd appmap-python
% APPMAP=true poetry run coverage run -m pytest
% poetry run coverage html
% open htmlcov/index.html
```
