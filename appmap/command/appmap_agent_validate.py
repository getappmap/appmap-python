import json
import sys

from packaging.version import Version, parse
from importlib_metadata import PackageNotFoundError, version

from .._implementation.py_version_check import check_py_version, AppMapPyVerException

class ValidationFailure(Exception):
    def __init__(self, message, level='error', detailed_message=None, help_urls=None):
        self.message = message
        self.level = level
        self.detailed_message = detailed_message
        self.help_urls = help_urls

    def to_dict(self):
        return {k: v for k, v in vars(self).items() if v is not None}


def check_python_version():
    try:
        check_py_version()
    except AppMapPyVerException as e:
        raise ValidationFailure(str(e))

def _check_version(dist, versions):
    dist_version = None
    for v in versions:
        try:
            dist_version = version(dist)

            required = parse(v)
            actual = parse(dist_version)
            if required.major != actual.major:
                dist_version = None
                continue

            if actual < required:
                raise ValidationFailure(f'{dist} must have version >= {required}, found {actual}')

            return dist_version
        except PackageNotFoundError:
            dist_version = None

    return dist_version

# Note that, per https://www.python.org/dev/peps/pep-0426/#name,
# comparison of distribution names are case-insensitive.
def check_django_version():
    return _check_version('django', ['2.2', '3.2'])

def check_flask_version():
    return _check_version('flask', ['1.1', '2.0'])

def check_pytest_version():
    return _check_version('pytest', ['6.2'])

def _run():
    errors = [ValidationFailure('internal error')] # shouldn't ever see this
    try:
        check_python_version()
        django_version = check_django_version()
        flask_version = check_flask_version()
        if not (django_version or flask_version):
            raise ValidationFailure(f'No web framework found. Expected one of: Django, Flask')

        check_pytest_version()
        errors = []
    except ValidationFailure as e:
        errors = [ e ]

    print(json.dumps([e.to_dict() for e in errors] , indent=2))

    return 0 if len(errors) == 0 else 1

def run():
    sys.exit(_run())
