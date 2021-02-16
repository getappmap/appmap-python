import importlib
import os
import platform
import re

import json

import appmap._implementation


class AppMapTestBase:
    def setup_method(self, _):
        appmap._implementation.initialize()  # pylint: disable=protected-access

    @staticmethod
    def normalize_git(git):
        git.pop('repository') # = 'git@github.com:applandinc/appmap-python.git'
        git.pop('branch') # = 'master'
        git.pop('commit') # = 'xyz'
        status = git.pop('status')
        assert isinstance(status, list)
        git.pop('git_last_tag') # = ''
        commits_since_last_tag = git.pop('git_commits_since_last_tag')
        assert isinstance(commits_since_last_tag, int)
        git.pop('git_last_annotated_tag') # = None
        commits_since_last_annotated_tag = git.pop(
            'git_commits_since_last_annotated_tag'
        )
        assert isinstance(commits_since_last_annotated_tag, int)

    @staticmethod
    def normalize_metadata(metadata):
        engine = metadata['language'].pop('engine')
        assert engine == platform.python_implementation()
        version = metadata['language'].pop('version')
        assert version == platform.python_version()

        if 'frameworks' in metadata:
            frameworks = metadata['frameworks']
            for f in frameworks:
                if f['name'] == 'pytest':
                    v = f.pop('version')
                    assert v == importlib.metadata.version('pytest')

    def normalize_appmap(self, generated_appmap):
        """
        Normalize the data in generated_appmap, removing any
        environment-specific values.

        Note that attempts to access required keys will raise
        KeyError, causing the test to fail.
        """

        def normalize(dct):
            if 'elapsed' in dct:
                elapsed = dct.pop('elapsed')
                assert isinstance(elapsed, float)
            if 'git' in dct:
                self.normalize_git(dct.pop('git'))
            if 'location' in dct:
                path, line = dct['location'].split(':')
                path = os.path.basename(path)
                dct['location'] = ':'.join([path, line])
            if 'metadata' in dct:
                self.normalize_metadata(dct['metadata'])
            if 'object_id' in dct:
                object_id = dct.pop('object_id')
                assert isinstance(object_id, int)
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
