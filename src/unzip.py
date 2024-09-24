from typing import Callable


def unzip(func: Callable):
    '''
    Mark property as unzipable - it will be called using `next` operator during 
    fixture injection.
    '''
    setattr(func, 'unzip', True)
    return func
