import pytest

from _appmap import generation
import appmap

@pytest.mark.appmap_enabled()
@pytest.mark.usefixtures("with_data_dir")
def test_recording_numpy_int64_does_not_fail():
    r = appmap.Recording()
    with r:
        from example_numpy_class import ExampleNumpyClass
        ExampleNumpyClass.go()
    assert len(r.events) == 8
    # TODO: This would throw the error at json.JSONEncoder.default()
    # in generation.py and the fix would handle the error.
    # However it seems that this test case is not able to reproduce
    # the JSON serialization error by creating appmaps which include
    # int64 values. This test case will pass even if the fix is not
    # applied.
    generation.dump(r)
