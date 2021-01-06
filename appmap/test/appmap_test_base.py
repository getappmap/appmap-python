import appmap._implementation


class AppMapTestBase:
    def setup_method(self, _):
        appmap._implementation.initialize()  # pylint: disable=protected-access
