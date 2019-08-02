import sys
import os
from bleno.supporting import *

module = exports(__name__)

bleno = require(__file__, '../..')

BlenoPrimaryService = bleno.PrimaryService

BatteryLevelCharacteristic = require(__file__, './batterylevelcharacteristic')

class BatteryService(BlenoPrimaryService):
  def __init__(self, *_varargs):
    BlenoPrimaryService.__init__(self, {
      'uuid': '180F', 
      'characteristics': [
        BatteryLevelCharacteristic()
    ]})

module.exports = BatteryService
