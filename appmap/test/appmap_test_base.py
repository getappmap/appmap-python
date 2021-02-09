import importlib
import os
import re

import json

import appmap._implementation


class AppMapTestBase:
    def setup_method(self, _):
        appmap._implementation.initialize()  # pylint: disable=protected-access

    def normalize_appmap(self, generated_appmap):
        """
        Normalize the data in generated_appmap, any
        environment-specific values.
        """
        object_id = 1
        pytest_version = importlib.metadata.version('pytest')

        def normalize(dct):
            nonlocal object_id, pytest_version

            if 'elapsed' in dct:
                assert isinstance(dct['elapsed'], float)
                dct['elapsed'] = 0.0
            if 'frameworks' in dct:
                for d in dct['frameworks']:
                    if d['name'] == 'pytest':
                        # 'version' is required, so this will raise if
                        # it's missing
                        v = d.pop('version')
                        assert v == pytest_version
            if 'git' in dct:
                git = dct['git']
                if 'repository' in git:
                    git['repository'] = 'git@github.com:applandinc/appmap-python.git'
                if 'branch' in git:
                    git['branch'] = 'master'
                if 'commit' in git:
                    git['commit'] = 'xyz'
                if 'status' in git:
                    assert isinstance(git['status'], list)
                    git['status'] = []
                if 'git_last_tag' in git:
                    git['git_last_tag'] = ''
                if 'git_commits_since_last_tag' in git:
                    assert isinstance(git['git_commits_since_last_tag'], int)
                    git['git_commits_since_last_tag'] = 0
                if 'git_last_annotated_tag' in git:
                    git['git_last_annotated_tag'] = None
                if 'git_commits_since_last_annotated_tag' in git:
                    assert isinstance(git['git_commits_since_last_annotated_tag'], int)
                    git['git_commits_since_last_annotated_tag'] = 0
            if 'location' in dct:
                path, line = dct['location'].split(':')
                path = os.path.basename(path)
                dct['location'] = ':'.join([path, line])
            if 'object_id' in dct:
                assert isinstance(dct['object_id'], int)
                dct['object_id'] = object_id
                object_id += 1
            if 'path' in dct:
                dct['path'] = os.path.basename(dct['path'])
            if 'value' in dct:
                # This maps all object references to the same
                # location. We don't actually need to verify that the
                # locations are correct -- if they weren't, the
                # instrumented code would be broken, right?
                v = dct['value']
                dct['value'] = re.sub(r'<(.*) object at 0x.*>',
                                      r'<\1 object at 0xabcdef>',
                                      v)
            return dct

        return json.loads(generated_appmap, object_hook=normalize)
