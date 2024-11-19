import appmap


def record(func, file_path='/tmp/record.appmap.json'):
    '''
    Decorator that records the execution flow.

    Usage
    -----

    @record()
    def my_function():
        pass

    You can also pass the path to save the appmap recording file

    @record(file_path='/tmp/new_file_path.json')
    def my_function():
        pass


    Parameters
    ----------
    file_path : str
        location of the path where appmap file will be saved (default: /tmp/record.appmap.json)
    '''
  
    def wrap(*args, **kwargs):
        r = appmap.Recording()
        print('Start recording...')

        with r:
            func(*args, **kwargs)

        print('End recording! Saving appmap json file...')

        with open(file_path, 'w') as f:
            f.write(appmap.generation.dump(r))

        print('Done!')
          
    return wrap
