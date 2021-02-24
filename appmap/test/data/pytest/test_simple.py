import os

def test_hello_world():
    import simple
    os.chdir('/tmp')
    assert simple.Simple().hello_world() == 'Hello world!'
