from _appmap.env import Env

logger = Env.current.getLogger(__name__)

if not Env.current.is_appmap_repo and Env.current.enables("unittest"):
    logger.debug("Test recording is enabled (unittest)")
    # pylint: disable=unused-import
    import _appmap.unittest  # pyright: ignore   # noqa: F401
