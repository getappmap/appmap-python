from importlib_metadata import distribution, PackageNotFoundError

def has_dist(dist):
    try:
        distribution(dist)
        return True
    except PackageNotFoundError:
        pass
    return False
