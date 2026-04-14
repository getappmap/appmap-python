_appmap_noappmap = "_appmap_noappmap"


def decorator(obj):
    setattr(obj, _appmap_noappmap, True)
    return obj


def disables(test_fn, cls=None):
    return hasattr(test_fn, _appmap_noappmap) or (
        cls is not None and hasattr(cls, _appmap_noappmap)
    )
