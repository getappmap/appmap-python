"""Test django.utils.functional.SimpleLazyObject handling"""

import pytest
import appmap

@pytest.mark.appmap_enabled
@pytest.mark.usefixtures("with_data_dir")
def test_recording_simplelazyobject_does_not_evaluate():
    """Test if recording a django.utils.functional.SimpleLazyObject does not force evaluation.

    SimpleLazyObject is a simple delayed instantiation utility.
    It only lazily instantiates an object when needed by evaluating a function.
    Since it can be used not only for performance, but also to delay
    instantiating objects until after some setup has been completed, we
    need to make sure simply recording a function which returns it
    doesn't cause incorrect premature evaluation.
    """
    with appmap.Recording():
        import appmap_testing.django_simplelazyobject as ecds  # pylint: disable=import-outside-toplevel
        ecds.lazy()

    # if we're here and the exception wasn't thrown, we're good
