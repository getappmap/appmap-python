import appmap
from appmap._implementation import generation

r = appmap.Recording()
with r:
    from src import Src
    print(Src.static_method())
    print(Src.class_method())
    print(Src().instance_method())

print(generation.dump(r))
