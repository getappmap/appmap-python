"""Test recording context manager"""
import os
import platform
import sys

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

    expected_appmap['metadata']['language']['engine'] = platform.python_implementation()
    expected_appmap['metadata']['language']['version'] = platform.python_version()

    config = tmp_path / 'appmap.yml'
    config.write_text(appmap_yml)
    src = tmp_path / 'src.py'
    src.write_text(src_py)
    sys.path.append(str(tmp_path))

    monkeypatch.setenv("APPMAP", "true")
    monkeypatch.setenv("APPMAP_CONFIG", str(config))

    # import here to use the environment variables set above
    import appmap
    r = appmap.Recording()
    with r:
        from src import Src
        Src().instance_method()

    generated_appmap = orjson.loads(r.dumps())
    for event in generated_appmap['events']:
        event.update((k, os.path.basename(v)) for k, v in event.items() if k == 'path')

    assert generated_appmap == expected_appmap
