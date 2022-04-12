"""
This module has generic tuner utility functions that don't depend on any other tuner moduules
"""


import functools
import threading
import wrapt


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
    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        with lock:
            return wrapped(*args, **kwargs)
    return wrapper


class ThreadSafeSingleton(type):
    _instances = {}

    @synchronized(thread_lock)
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(ThreadSafeSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
