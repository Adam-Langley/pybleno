import os
import sys

from ._jshelpers import *

require(__file__, 'sys')
module = sys.modules[__name__]

def hashval(str, siz):
    hash = 0
    # Take ordinal number of char in str, and just add
    for x in str: hash += (ord(x))
    return(hash % siz) # Depending on the range, do a modulo operation.

def debug(name):
    last_time = os.times()[4]

    color_code = hashval(name, 7) + 31

    def log(message):
        if not 'DEBUG' in os.environ:
            return
        nonlocal last_time
        lines = message.split('\n')
        for i in range(0, len(lines)):
            line = lines[i]
            print('  \033[1;%d;255m%s\033[0;255;255m %s' % (color_code, name, line), end="")
            if i == len(lines) - 1:
                break
            print()

        current_time = os.times()[4]
        if last_time:
            print(" \033[0;%d;255m%+dms\033[0;255;255m" % (color_code, current_time - last_time))
        else:
            print() # newline
        last_time = current_time
    return log

module.exports = debug
