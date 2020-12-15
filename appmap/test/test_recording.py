"""Test recording context manager"""
import json
import os
import platform
import sys
from importlib import reload

import pytest

FIXTURE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'data'
    )

@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, 'appmap.yml'),
    os.path.join(FIXTURE_DIR, 'src.py')
    )
def test_recording_works(monkeypatch, datafiles):
    expected_appmap = {
        'classMap': [
            {
                'children': [
                    {
                        'children': [
                            {
                                'lineno': 5,
                                'name': 'static_method',
                                'path': 'src.py',
                                'static': True,
                                'type': 'function',
                            },
                            {
                                'lineno': 9,
                                'name': 'class_method',
                                'path': 'src.py',
                                'static': True,
                                'type': 'function',
                            },
                            {
                                'lineno': 13,
                                'name': 'instance_method',
                                'path': 'src.py',
                                'static': False,
                                'type': 'function',
                            },
                        ],
                        'name': 'Src',
                        'type': 'class',
                    },
                ],
                'name': 'src',
                'type': 'package',
            },
        ],
        'events': [
            {
                'defined_class': 'src.Src',
                'event': 'call',
                'id': 2,
                'lineno': 5,
                'method_id': 'static_method',
                'parameters': [],
                'path': 'src.py',
                'receiver': {
                    'class': 'class',
                    'object_id': 1,
                    'value': 'src.Src',
                },
                'static': True,
                'thread_id': 1,
            },
            {'event': 'return', 'id': 3, 'parent_id': 2, 'thread_id': 1},
            {
                'defined_class': 'src.Src',
                'event': 'call',
                'id': 4,
                'lineno': 9,
                'method_id': 'class_method',
                'parameters': [],
                'path': 'src.py',
                'receiver': {
                    'class': 'class',
                    'object_id': 2,
                    'value': 'src.Src',
                },
                'static': True,
                'thread_id': 1,
            },
            {'event': 'return', 'id': 5, 'parent_id': 4, 'thread_id': 1},
            {
                'defined_class': 'src.Src',
                'event': 'call',
                'id': 6,
                'lineno': 13,
                'method_id': 'instance_method',
                'parameters': [],
                'path': 'src.py',
                'receiver': {
                    'class': 'src.Src',
                    'object_id': 3,
                    'value': "It's a src.Src!",
                },
                'static': False,
                'thread_id': 1,
            },
            {'event': 'return', 'id': 7, 'parent_id': 6, 'thread_id': 1},
        ],
        'metadata': {
            'client': {
                'name': 'appmap',
                'url': 'https://github.com/applandinc/appmap-python',
            },
            'language': {
                'engine': 'CPython',
                'name': 'python',
                'version': '3.9.0',
            },
        },
        'version': '1.4',
    }

    # Setting these outside the definition of expected_appmap makes it
    # easier to update when the expected appmap changes
    py_impl = platform.python_implementation()
    py_version = platform.python_version()
    expected_appmap['metadata']['language']['engine'] = py_impl
    expected_appmap['metadata']['language']['version'] = py_version


    sys.path.append(str(datafiles))

    monkeypatch.setenv("APPMAP", "true")
    monkeypatch.setenv("APPMAP_CONFIG", str(datafiles / 'appmap.yml'))
    monkeypatch.setenv("APPMAP_LOG_LEVEL", "debug")

    import appmap
    reload(appmap._implementation.recording)  # pylint: disable=protected-access
    r = appmap.Recording()
    with r:
        from src import Src  # pylint: disable=import-error
        Src.static_method()
        Src.class_method()
        Src().instance_method()

    # Normalize paths
    object_id = 1

    def normalize(dct):
        nonlocal object_id
        if 'path' in dct:
            dct['path'] = os.path.basename(dct['path'])
        if 'object_id' in dct:
            assert isinstance(dct['object_id'], int)
            dct['object_id'] = object_id
            object_id += 1
        return dct

    generated_appmap = json.loads(appmap.generation.dump(r),
                                  object_hook=normalize)
    for event in generated_appmap['events']:
        for k, v in event.items():
            if k == 'path':
                event[k] = os.path.basename(v)

    from pprintpp import pprint as pp
    pp(generated_appmap)
    assert generated_appmap == expected_appmap
