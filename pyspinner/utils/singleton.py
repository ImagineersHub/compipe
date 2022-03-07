"""
This module has generic tuner utility functions that don't depend on any other tuner moduules
"""


import functools
import threading


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(
                *args, **kwargs)
        else:
            # update property values when access obj through singleton
            if kwargs:
                for key, value in kwargs.items():
                    setattr(cls._instances[cls], key, value)
        return cls._instances[cls]


thread_lock = threading.Lock()


def synchronized(lock):
    """ Synchronization decorator """
    def wrapper(f):
        @functools.wraps(f)
        def inner_wrapper(*args, **kw):
            with lock:
                return f(*args, **kw)
        return inner_wrapper
    return wrapper


# class Singleton(type):
class ThreadSafeSingleton(type):
    _instances = {}

    @synchronized(thread_lock)
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(ThreadSafeSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
