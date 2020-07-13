"""
Quick, dirty and copied cache decorators
"""

import os
import pickle




def cached(cachefile):
    """
    A function that creates a decorator which will use "cachefile" for caching the results of the decorated function
    """

    def decorator(fn):  # define a decorator for a function "fn"
        def wrapped(*args, **kwargs):  # define a wrapper that will finally call "fn" with all arguments
            # if cache exists -> load it and return its content
            if os.path.exists(cachefile):
                with open(cachefile, 'rb') as cachehandle:
                    print("using cached result from '%s'" % cachefile)
                    return pickle.load(cachehandle)

            # execute the function with all arguments passed
            res = fn(*args, **kwargs)

            # write to cache file
            with open(cachefile, 'wb') as cachehandle:
                print("saving result to cache '%s'" % cachefile)
                pickle.dump(res, cachehandle)

            return res

        return wrapped

    return decorator  # return this "customized" decorator that uses "cachefile"


def arg_cached(cachefile):
    """
    A function that creates a decorator which will use "cachefile-arg[0].pkl" for caching the results of f(*args,**kwargs)
    """

    def decorator(fn):  # define a decorator for a function "fn"
        def wrapped(*args, **kwargs):  # define a wrapper that will finally call "fn" with all arguments
            # if cache exists -> load it and return its content
            path = f"{cachefile}-{args[0]}.pkl"
            if os.path.exists(path):
                with open(path, 'rb') as cachehandle:
                    print("using cached result from '%s'" % path)
                    return pickle.load(cachehandle)

            # execute the function with all arguments passed
            res = fn(*args, **kwargs)

            # write to cache file
            with open(path, 'wb') as cachehandle:
                print("saving result to cache '%s'" % path)
                pickle.dump(res, cachehandle)

            return res

        return wrapped

    return decorator  # return this "customized" decorator that uses "cachefile"
