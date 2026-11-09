import sys


class C:
    @staticmethod
    def static(p):
        return p

    @classmethod
    def cls(cls, p):
        return p

    def zero(self):
        return "Hello world!"

    def one(self, p):
        return p

    def args_kwargs(self, *args, **kwargs):
        return "%s %s" % (args, kwargs)

    def with_defaults(self, p1=1, p2=2):
        return "%s %s" % (p1, p2)

    def mixed(self, a, b=None, c="dflt", *args, d, e="e", **kwargs):
        return "%s %s %s %s %s %s %s" % (a, b, c, args, d, e, kwargs)


if sys.version_info >= (3, 8):
    exec(
        """
def positional_only(self, p1, p2, /):
    return '%s %s' % (p1, p2)
C.positional_only = positional_only

def keyword_only(self, *, p1, p2):
    return '%s %s' % (p1, p2)
C.keyword_only = keyword_only

def positional_only_kwargs(self, a, b="dflt", /, **kwargs):
    return '%s %s %s' % (a, b, kwargs)
C.positional_only_kwargs = positional_only_kwargs
    """
    )
