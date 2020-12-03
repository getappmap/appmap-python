import platform


class Metadata:
    @staticmethod
    def dump():
        return {
            'language': {
                'name': 'python',
                'engine': platform.python_implementation(),
                'version': platform.python_version()
            },
            'client': {
                'name': 'appmap',
                'url': 'https://github.com/applandinc/appmap-python'
            }
        }
