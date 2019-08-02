import sys
import os
import re
import importlib

def get_package_root(fileOrFolder):
  absoluteFileOrFolder = os.path.realpath(fileOrFolder)
  if not os.path.exists(absoluteFileOrFolder):
    return None

  def walkToPackage(fileOrFolder):
    if fileOrFolder == '/':
      return None
    if os.path.isfile(fileOrFolder):
      p, f = fileOrFolder.rsplit('/', 1)
      return walkToPackage(p)
    elif os.path.isdir(fileOrFolder):
      if os.path.isfile(fileOrFolder + '/__init__.py'):
        p, f = fileOrFolder.rsplit('/', 1)
        return walkToPackage(p) or (p, f)
      else:
        p, f = fileOrFolder.rsplit('/', 1)
        return walkToPackage(p)
  return walkToPackage(absoluteFileOrFolder)

def require(callerpath, name):
  mod = None
  callerpath = os.path.realpath(os.path.abspath(callerpath))
  current_folder = os.path.dirname(callerpath)
  canonical = os.path.realpath(current_folder + '/' + name)

  # types of imports
  # 1. ./
  # these import a file relative to the immediate caller
  # 2. ../../
  # this pattern is used to load the root Bleno package...
  # 3. name
  # generally used to load built-in packages. In our case, they come from our 'builtin' folder...
  # this relies on loaded package names - gonna have to prepend it with bleno package "lib.bleno.", and see if it loads.
  # if not, fallback..?

  if name in sys.modules:
    mod = sys.modules[name]
  else:
    if name.startswith('..'):
      name = canonical
    elif name.startswith('./'):
      caller_parent = os.path.dirname(callerpath)
      pkg_path, pkg_name = get_package_root(caller_parent)
      if pkg_path:
        name = pkg_name + '/' + caller_parent[len(pkg_path + '/' + pkg_name) + 1:] + name[1:]
        while '//' in name:
          name = name.replace('//', '/')
        name = name.replace('/', '.')
      else:
        name = os.path.dirname(os.path.realpath(callerpath)) + pkg_name
    else: 
      # must  be in current package
      # are we a pckage?
      name =  'bleno.supporting.' + name
    # elif os.path.isfile(canonical + '/__init__.py'):
    #   name = canonical
    # elif os.path.isfile(callerpath + '.py'):
    #   name = callerpath

    if '/' in name:
        p, f = name.rsplit('/', 1)
        if not p in sys.path:
          sys.path.append(p)
        name = f

    mod = importlib.import_module(name)

    locals()[name] = mod
    sys.modules[name] = mod
  return mod.exports if hasattr(mod, 'exports') else mod