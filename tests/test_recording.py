"""Test recording context manager"""
import os
import sys
from importlib import reload

import orjson

def test_recording_works(monkeypatch, tmp_path):
    # the appmap.yml
    appmap_yml = """
name: SrcApp
packages:
- path: Src
"""
    # the source file
    src_py = """
import sys


class Src:
    def instance_method(self):
        print(f'Src#instance_method({self})', file=sys.stderr)
"""
    expected_appmap = {
            'metadata': {
                'language': {
                    'name': 'python',
                    'engine': 'CPython',
                    'version': '3.9.0'
                },
                'client': {
                    'name': 'appmap',
                    'url': 'https://github.com/applandinc/appmap-python'
                }
            },
            'events': [
                {
                    'defined_class': 'Src',
                    'method_id': 'instance_method',
                    'path': 'src.py',
                    'lineno': 6,
                    'static': False,
                    'id': 2,
                    'event': 'call',
                    'thread_id': 1
                },
                {
                    'parent_id': 2,
                    'id': 3,
                    'event': 'return',
                    'thread_id': 1
                }
            ]
        }

    config = tmp_path / 'appmap.yml'
    config.write_text(appmap_yml)
    src = tmp_path / 'src.py'
    src.write_text(src_py)
    sys.path.append(str(tmp_path))


    monkeypatch.setenv("APPMAP", "true")
    monkeypatch.setenv("APPMAP_CONFIG", str(config))

    # import here to use the environment variables set above
    import appmap
    from appmap._implementation import generation
    r = appmap.Recording()
    with r:
        from src import Src
        Src().instance_method()

    generated_appmap = orjson.loads(generation.dump(r))
    for event in generated_appmap['events']:
        for k, v in event.items():
            if k == 'path':
                event[k] = os.path.basename(v)

    assert generated_appmap == expected_appmap
