The tables below describe how the variable environment variables control the various
recording types. In each case, ✓ means that the corresponding recording type
will be produced, ❌ means that it will not.

## Web Apps
These tables describe how `APPMAP_RECORD_REQUESTS` and `APPMAP_RECORD_REMOTE` are
handled when running a web app. "web app, debug on" means a Flask app run as `flask --debug`,
a FastAPI app run using `uvicorn --reload` and, a Django app run with `DEBUG = True` in `settings.py`.

|                      | `APPMAP_RECORD_REQUESTS` is unset | `APPMAP_RECORD_REQUESTS` == "true" | `APPMAP_RECORD_REQUESTS` == "false" |
| -------------------- | :----------------------------: | :------------------------------: | :-------------------------------: |
| "web app, debug on"  |               ✓                |                ✓                 |                 ❌                 |
| "web app, debug off" |               ✓                |                ✓                 |                 ❌                 |


|                      | `APPMAP_RECORD_REMOTE` is unset | `APPMAP_RECORD_REMOTE` == "true" | `APPMAP_RECORD_REMOTE` == "false" |
| -------------------- | :---------------------------: | :----------------------------: | :------------------------------: |
| "web app, debug on"  |               ✓               |               ✓                |                ❌                 |
| "web app, debug off" |               ❌               |        ✓(with warning)         |                ❌                 |


## Testing
This table shows how `APPMAP_RECORD_PYTEST`, `APPMAP_RECORD_UNITTEST`, and
`APPMAP_RECORD_REQUESTS` are handled when running tests in. Note that in v2, in
v2, `APPMAP_RECORD_PYTEST` and `APPMAP_RECORD_UNITTEST` will be replaced with
`APPMAP_RECORD_TESTS`.

|        | `APPMAP_RECORD_PYTEST` is unset | `APPMAP_RECORD_PYTEST` == "true" | `APPMAP_RECORD_PYTEST` == "false" | `APPMAP_RECORD_REQUESTS` is unset | `APPMAP_RECORD_REQUESTS` == "true" | `APPMAP_RECORD_REQUESTS` == "false" |
| ------ | :---------------------------: | :-----------------------------: | :------------------------------: | :----------------------------: | :-----------------------------: | :------------------------------: |
| pytest |               ✓               |                ✓                |                ❌                 |        ❌         |                ignored in v1, ✓ in v2                |                ❌                 |




## Process Recording
`APPMAP_RECORD_PROCESS` creates recordings as described in this table. Note
that, in v1, `APPMAP_RECORD_PROCESS` doesn't change the handling of any of the
other variables. As a result, setting it when running a either web app or when
running tests will result in an error. Whether this behavior should change in v2
is TBD.

|                   | `APPMAP_RECORD_PROCESS` is unset | `APPMAP_RECORD_PROCESS` == "true" | `APPMAP_RECORD_PROCESS` == "false" |
| ----------------- | :----------------------------: | :---------------------------------: | :----------------------------------: |
| process recording |               ❌                |                  ✓                  |                  ❌                   |