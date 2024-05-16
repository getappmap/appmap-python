import json
import sys

import yaml

from _appmap.configuration import Config


def _run():
    print(
        json.dumps(
            {
                "configuration": {
                    "filename": "appmap.yml",
                    "contents": yaml.dump(Config.current.default),
                }
            }
        )
    )

    return 0


def run():
    sys.exit(_run())


if __name__ == "__main__":
    run()
