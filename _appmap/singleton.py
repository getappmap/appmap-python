class SingletonMeta(type):
    def __init__(cls, *args, **kwargs):
        type.__init__(cls, *args, **kwargs)
        cls._instance = None

    @property
    def current(cls):
        if not cls._instance:
            cls._instance = cls()

        return cls._instance

    def reset(cls, **kwargs):
        cls._instance = cls(**kwargs)
