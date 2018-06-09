from pybleno.hci_socket import Emit
import _thread
import time

PizzaCrust = {
  'NORMAL':    0,
  'DEEP_DISH': 1,
  'THIN':      2,
}

PizzaToppings = {
  'NONE':           0,
  'PEPPERONI':      1 << 0,
  'MUSHROOMS':      1 << 1,
  'EXTRA_CHEESE':   1 << 2,
  'BLACK_OLIVES':   1 << 3,
  'CANADIAN_BACON': 1 << 4,
  'PINEAPPLE':      1 << 5,
  'BELL_PEPPERS':   1 << 6,
  'SAUSAGE':        1 << 7,
}

PizzaBakeResult = {
  'HALF_BAKED': 0,
  'BAKED':      1,
  'CRISPY':     2,
  'BURNT':      3,
  'ON_FIRE':    4
}

class Pizza():
    def __init__(self):
        #events.EventEmitter.call(this)
        self.toppings = PizzaToppings['NONE']
        self.crust = PizzaCrust['NORMAL']
        
    def bake(self, temperature):
        t = temperature * 10
        print('baking pizza at %d, degrees for %s milliseconds' % (temperature, t))
        
        def on_timeout():
            time.sleep(t / 1000)
            if (temperature < 350):
                result = PizzaBakeResult['HALF_BAKED']
            elif (temperature < 450):
                result = PizzaBakeResult['BAKED']
            elif (temperature < 500):
                result = PizzaBakeResult['CRISPY']
            elif (temperature < 600):
                result - PizzaBakeResult['BURNT']
            else:
                result = PizzaBakeResult['ON_FIRE']
            self.emit('ready', [result]);
        thread.start_new_thread(on_timeout, ())

Emit.Patch(Pizza)
