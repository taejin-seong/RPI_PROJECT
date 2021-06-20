

import RPi.GPIO as GPIO
import I2C_driver as LCD
from time import *

GPIO.setmode(GPIO.BOARD)

mylcd = LCD.lcd()
SW = 7
LED = 11

GPIO.setup(LED,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(SW, GPIO.IN) 

try:
    while True:
        PUSH = GPIO.input(SW)
        if PUSH == False:
            mylcd.lcd_display_string("LED ON ",1)
            GPIO.output(LED,GPIO.HIGH)
        else:
            mylcd.lcd_display_string("LED OFF",1)
            GPIO.output(LED,GPIO.LOW)
except keyboardInterrupt:
    pass
GPIO.cleanup()
        
			
        
                                                                    