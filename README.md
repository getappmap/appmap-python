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
  - MyOtherClass#my_instance_method
  - MyOtherClass.my_class_method
```
  
## Test Frameworks
`appmap-python` supports recording `unittest` and `pytest` test cases. Import the
appropriate test framework support into your tests.

### unittest
`import appmap.unittest`. Instruments subclasses of `unittest.TestCase` and records each
`test_*` function in the subclasses.

### pytest 
`import appmap.pytest`. Instruments and records `test_*` functions.

### Run your tests
Once you've configured your tests to generate AppMaps, run the tests with the
`APPMAP=true` in the environment. For example, to run a unittest test suite:

```sh
$ APPMAP=true python -m unittest
```


## Remote Recording
`appmap-python` supports remote recording of Django and Flask web applications. Import the
appropriate remote recording support into your web app.

### Django
`import appmap.django`. Adds `/_appmap/record` routes to a Django app.

## Flask
`import appmap.flask`. Adds `/_appmap/record` routes to a Flask app.

## Run your web app
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
