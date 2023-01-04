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


if sys.version_info >= (3, 8):
    exec(
        """
def positional_only(self, p1, p2, /):
    return '%s %s' % (p1, p2)
C.positional_only = positional_only

def keyword_only(self, *, p1, p2):
    return '%s %s' % (p1, p2)
C.keyword_only = keyword_only
    """
    )
