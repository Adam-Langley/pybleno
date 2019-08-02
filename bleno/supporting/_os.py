import sys
import platform as _platform

from ._jshelpers import require

module = sys.modules[__name__]

def bind(instance, func, as_name=None):
    """
    Bind the function *func* to *instance*, with either provided name *as_name*
    or the existing name of *func*. The provided *func* should accept the 
    instance as the first argument, i.e. "self".
    """
    if as_name is None:
        as_name = func.__name__
    bound_method = func.__get__(instance, instance.__class__)
    setattr(instance, as_name, bound_method)
    return bound_method

class MyExports:
  pass
os = MyExports()

def platform(self):
  return sys.platform
  
def release(self):
  return _platform.release()

bind(os, platform)
bind(os, release)

module.exports = os


