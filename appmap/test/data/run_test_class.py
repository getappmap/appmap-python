import appmap
from appmap._implementation import generation

r = appmap.Recording()
with r:
    from test_class import TestClass
    print(TestClass.static_method())
    print(TestClass.class_method())
    print(TestClass().instance_method())

print(generation.dump(r))
