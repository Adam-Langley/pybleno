from distutils.core import setup
setup(
  name = 'pybleno',
  packages = ['pybleno', 'pybleno/hci_socket',  'pybleno/hci_socket/BluetoothHCI'], # this must be the same as the name above
  version = '0.3',
  description = 'A direct port of the Bleno bluetooth LE peripheral role library to Python2/3',
  author = 'Adam Langley',
  author_email = 'github.com@irisdesign.co.nz',
  url = 'https://github.com/Adam-Langley/pybleno', # use the URL to the github repo
  download_url = 'https://github.com/Adam-Langley/pybleno/archive/0.3.tar.gz', # I'll explain this in a second
  keywords = ['bluetooth', 'ble'], # arbitrary keywords
  classifiers = [],
)