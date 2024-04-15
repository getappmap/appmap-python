from _appmap.env import Env


def test_disable_temporarily():
    env = Env({"_APPMAP": "true"})
    assert env.enables("requests")
    try:
        with env.disabled("requests"):
            assert not env.enables("requests")
            raise 'hell'
    except:
        ...
    assert env.enables("requests")
