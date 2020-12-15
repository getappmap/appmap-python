"""Test recording context manager"""
import json
import os
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
                                'lineno': 2,
                                'name': 'static_method',
                                'path': 'src.py',
                                'static': True,
                                'type': 'function',
                            },
                            {
                                'lineno': 6,
                                'name': 'class_method',
                                'path': 'src.py',
                                'static': True,
                                'type': 'function',
                            },
                            {
                                'lineno': 10,
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
                'lineno': 2,
                'method_id': 'static_method',
                'parameters': None,
                'path': 'src.py',
                'receiver': None,
                'static': True,
                'thread_id': 1,
            },
            {'event': 'return', 'id': 3, 'parent_id': 2, 'thread_id': 1},
            {
                'defined_class': 'src.Src',
                'event': 'call',
                'id': 4,
                'lineno': 6,
                'method_id': 'class_method',
                'parameters': None,
                'path': 'src.py',
                'receiver': None,
                'static': True,
                'thread_id': 1,
            },
            {'event': 'return', 'id': 5, 'parent_id': 4, 'thread_id': 1},
            {
                'defined_class': 'src.Src',
                'event': 'call',
                'id': 6,
                'lineno': 10,
                'method_id': 'instance_method',
                'parameters': None,
                'path': 'src.py',
                'receiver': None,
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

    sys.path.append(str(datafiles))

    monkeypatch.setenv("APPMAP", "true")
    monkeypatch.setenv("APPMAP_CONFIG", str(datafiles / 'appmap.yml'))
    monkeypatch.setenv("APPMAP_LOG_LEVEL", "debug")

    import appmap
    from appmap._implementation import generation
    reload(appmap._implementation.recording)  # pylint: disable=protected-access
    r = appmap.Recording()
    with r:
        from src import Src  # pylint: disable=import-error
        Src.static_method()
        Src.class_method()
        Src().instance_method()

    # Normalize paths
    def normalize_paths(dct):
        if 'path' in dct:
            dct['path'] = os.path.basename(dct['path'])
        return dct

    generated_appmap = json.loads(generation.dump(r),
                                  object_hook=normalize_paths)
    for event in generated_appmap['events']:
        for k, v in event.items():
            if k == 'path':
                event[k] = os.path.basename(v)

    assert generated_appmap == expected_appmap
