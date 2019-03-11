# pybleno
[![Downloads](https://pepy.tech/badge/pybleno)](https://pepy.tech/project/pybleno)

A direct port of the Bleno bluetooth LE peripheral role library to Python2/3

The logic of this library was originally written by Sandeep Mistry (https://github.com/sandeepmistry/bleno),
and this repository is a direct port of that code-base. A huge thanks to Sandeep for his solid library.

Effort has been made to maintain the same code structure to aid in parallel maintenance with Bleno.

__Note:__ Currently only tested on Linux Raspbian

## Prerequisites
Please read the [original nodejs Bleno prerequisites](https://github.com/noble/bleno#prerequisites), failure to meet these may result in 'Operation not permitted' errors at runtime.

## Install

```sh
pip install pybleno
```

## Usage

```python
from pybleno import *

bleno = Bleno()
```

See [examples folder](https://github.com/Adam-Langley/pybleno/blob/master/examples) for code examples.

See the original nodejs Bleno documentation for usage.

## Troubleshooting
 * Symptoms: Peripheral stops responding, notifications not going through - pi must be rebooted. Kernel log contains `hci0: Frame reassembly failed`
   * Cause: Bugs in bluetooth kernel module - manifests whe running Raspbian <= 2018-11-13. 
   * Fix: `apt-get upgrade`

## Licenses and Attribution

### Sandeep Mistry's Bleno
https://github.com/sandeepmistry/bleno

### Wayne Keenan's BluetoothHCI
https://github.com/TheBubbleworks/python-hcipy

### Mike Ryan's BluetoothSocket taken from Python control for Leviton Decora Bluetooth switches
https://github.com/mjg59/python-decora

## License

Copyright (C) 2017 Adam Langley

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
