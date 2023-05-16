from _appmap.env import Env

logger = Env.current.getLogger(__name__)

if not Env.current.is_appmap_repo and Env.current.enables("unittest"):
    logger.debug("Test recording is enabled (unittest)")
    import _appmap.unittest  # pyright: ignore pylint: disable=unused-import
