import os
import os.path
import subprocess

import json

from .appmap_test_base import AppMapTestBase


class TestPytest(AppMapTestBase):
    def compose_exec(self, args, test_dir, tmpdir):
        cwd = test_dir
        env = {
            "PATH": os.getenv("PATH"),
            "APPMAP_OUTPUT_DIR": tmpdir
        }
        return subprocess.run(['docker-compose'] + args,
                              check=True,
                              cwd=cwd,
                              env=env)

    def test_basic_integration(self, pytestconfig, tmpdir):
        test_dir = os.path.join(pytestconfig.rootpath,
                                'appmap', 'test', 'data', 'pytest')
        self.compose_exec(['build'], test_dir, tmpdir)
        self.compose_exec(['run', 'test'], test_dir, tmpdir)

        appmap_json = os.path.join(
            tmpdir, 'pytest', 'test_hello_world.appmap.json'
        )
        with open(appmap_json) as appmap:
            generated_appmap = self.normalize_appmap(appmap.read())

        with open(os.path.join(test_dir, 'expected.appmap.json')) as f:
            expected_appmap = json.load(f)

        assert generated_appmap == expected_appmap
