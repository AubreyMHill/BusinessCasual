#!/usr/bin/env python
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

class PayphoneReader:
    trigger_pin = 17
    hook_pin = 4

    pins = [18, 23, 24, 25]

    mapping = { (0,0,0,0):"1",
                (1,0,0,0):"2",
                (0,1,0,0):"3",
                (1,0,1,0):"5",
                (0,0,1,0):"4",
                (0,1,1,0):"6",
                (1,0,0,1):"8",
                (0,0,0,1):"7",
                (0,1,0,1):"9",
                (1,0,1,1):"0",
                (0,0,1,1):"*",
                (0,1,1,1):"#"}

    def __init__(self, hook_callback = None, button_callback = None):
        self.hook_callback = hook_callback
        self.button_callback = button_callback
        
        GPIO.setup(PayphoneReader.hook_pin, GPIO.IN)
        GPIO.setup(PayphoneReader.trigger_pin, GPIO.IN)
        
        for pin in PayphoneReader.pins:
            GPIO.setup(pin, GPIO.IN)

        self.last_trigger_value = 0
        self.last_hook_value = 0

        self.read_values = []
        
    def read(self):

        # Process the hook trigger
        current_hook_value = GPIO.input(PayphoneReader.hook_pin)
        if self.last_hook_value != current_hook_value:
            # Do something if the hook has changed value
            if self.hook_callback is not None:
                self.hook_callback(current_hook_value)
        self.last_hook_value = current_hook_value
        

        # Process the general key trigger
        current_trigger_value = GPIO.input(PayphoneReader.trigger_pin)
        if self.last_trigger_value == 0 and current_trigger_value == 1:
            # We've caught a button being pressed
            values = tuple([GPIO.input(pin) for pin in PayphoneReader.pins])
            key_value = PayphoneReader.mapping.get(values, "unknown")
            if self.button_callback is not None:
                self.button_callback(key_value)
        self.last_trigger_value = current_trigger_value

        return True 


def sample_hook_callback(hook_value):
    if hook_value:
        print("The hook was pressed")
    else:
        print("The hook was released")

def sample_button_callback(button_value):
    print("Key {} was pressed".format(button_value))

if __name__ == "__main__":
    reader = PayphoneReader(sample_hook_callback, sample_button_callback)
    
    while reader.read():
        pass
