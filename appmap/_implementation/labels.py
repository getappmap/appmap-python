

class labels:
    def __init__(self, *args):
        self._labels = args

    def __call__(self, fn):
        # For simplicity, set _appmap_labels right on the
        # function. We'll delete it when we instrument the function.
        setattr(fn, '_appmap_labels', self._labels)
        return fn
