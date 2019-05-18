from distutils.core import setup
setup(
  name = 'pybleno',
  packages = ['pybleno', 'pybleno/hci_socket',  'pybleno/hci_socket/BluetoothHCI'], # this must be the same as the name above
  version = '0.11',
  description = 'A direct port of the Bleno bluetooth LE peripheral role library to Python2/3',
  author = 'Adam Langley',
  author_email = 'github.com@irisdesign.co.nz',
  url = 'https://github.com/Adam-Langley/pybleno', # use the URL to the github repo
  download_url = 'https://github.com/Adam-Langley/pybleno/archive/0.9.tar.gz', # I'll explain this in a second
  keywords = ['Bluetooth', 'Bluetooth Smart', 'BLE', 'Bluetooth Low Energy'], # arbitrary keywords
  classifiers=[
      'Programming Language :: Python :: 2.7',
      'Programming Language :: Python :: 3.3',
      'Programming Language :: Python :: 3.4'
  ]
)
