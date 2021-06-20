import RPi.GPIO as GPIO   
import smbus              
import I2C_driver as LCD  

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT

import re
import argparse
import time


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

bus = smbus.SMBus(1)


# Accelerometer inital setting...
    
address = 0x53 # IC address
    
x_adr = 0x32   # X-axis adress
y_adr = 0x34   # Y-axis adress
z_adr = 0x36   # Z-axis adress





# Accelerometer Sensro data measure
def measure_acc(adr):
    
    acc0 = bus.read_byte_data(address, adr)

    acc1 = bus.read_byte_data(address, adr + 1)

    acc = (acc1 << 8) + acc0

    if acc > 0x1FF:
        acc = (65536 - acc) * -1

    acc = acc * 3.9 / 1000

    return round(acc,2)



def dotmatrix_msg(n, block_orientation, rotate, inreverse, msg):
    # create matrix device
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, cascaded=n or 1, block_orientation=block_orientation,
                     rotate=rotate or 0, blocks_arranged_in_reverse_order=inreverse)
 
    show_message(device, msg, fill="White", font=proportional(CP437_FONT))
    



def main():
    
    # LED,SW initial setting...
    
    SW_1 = 7    # GPIO  4 (GPCLK0)
    LED_1 = 32  # GPIO 12 (PWM0)

    SW_2 =  11  # GPIO 17
    LED_2 = 33  # GPIO 13 (PWM1)


    GPIO.setup(LED_1, GPIO.OUT, initial = GPIO.LOW)  # LED_1 Output & inital LOW 
    GPIO.setup(LED_2, GPIO.OUT, initial = GPIO.LOW)  # LED_2 Output & inital LOW

    GPIO.setup(SW_1, GPIO.IN) # SW_1 Input
    GPIO.setup(SW_2, GPIO.IN) # SW_2 Input
    
   
    # LED PWM inital setting ...
    
    PWM_LED_1 = GPIO.PWM(LED_1, 100) # LED_1 frequency = 1000Hz PWM generation 
    PWM_LED_1.start(0)               # LED_1 PWM Start 0~100%
    
    PWM_LED_2 = GPIO.PWM(LED_2, 100) # LED_2 frequency = 1000Hz PWM generation
    PWM_LED_2.start(0)               # LED_2 PWM Start 0~100%  
    
    # Accelerometer inital setting...
    
    bus.write_byte_data(address, 0x2D, 0x08)

    
    # Dot Matrix inital settting...

    parser = argparse.ArgumentParser(description='matrix_demo arguments',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--cascaded', '-n', type=int, default=1, help='Number of cascaded MAX7219 LED matrices')
    parser.add_argument('--block-orientation', type=int, default=0, choices=[0, 90, -90], help='Corrects block orientation when wired vertically')
    parser.add_argument('--rotate', type=int, default=0, choices=[0, 1, 2, 3], help='Rotate display 0=0°, 1=90°, 2=180°, 3=270°')
    parser.add_argument('--reverse-order', type=bool, default=False, help='Set to true if blocks are in reverse order')

    args = parser.parse_args()


    # LCD inital setting...
    
    mylcd = LCD.lcd()


    while True:
        
        # SW_1, SW_2 Input ...
        PUSH_SW1 = GPIO.input(SW_1)
        PUSH_SW2 = GPIO.input(SW_2)
        
 
        
        if PUSH_SW1 == False: #if push SW1..
            
            # LED PWM Stop..
            PWM_LED_1.stop()
            PWM_LED_2.stop()
            
            # LED_1 ON & LED_2 OFF
            GPIO.output(LED_1, GPIO.HIGH)
            GPIO.output(LED_2, GPIO.LOW)
            
            # LCD Start
            mylcd.lcd_clear()
            mylcd.lcd_display_string('Dot Matrix Test',1)
            
            # Dot matrix Start
            dotmatrix_msg(args.cascaded, args.block_orientation, args.rotate, args.reverse_order, "Test..") # Display msg on Dot matix... 
            
        
        elif PUSH_SW2 == False: # if push SW2..
            
            # LED PWM Stop...
            PWM_LED_1.stop()
            PWM_LED_2.stop()
            
            # LED_1 OFF & LED_2 ON
            GPIO.output(LED_1, GPIO.LOW)
            GPIO.output(LED_2, GPIO.HIGH)
                
            # LCD Start
            mylcd.lcd_display_string('ACC Test',1) # Test msg...
            
            x_acc = measure_acc(x_adr) # Acc axis measure...
            y_acc = measure_acc(y_adr)
            z_acc = measure_acc(z_adr)
            
            mylcd.lcd_display_string_pos('x:',1,9)    # Display x,y,z on LCD...        
            mylcd.lcd_display_string_pos(str(x_acc),1,11)

            mylcd.lcd_display_string_pos('y:',2,0)
            mylcd.lcd_display_string_pos(str(y_acc),2,2)
            
            mylcd.lcd_display_string_pos('z:',2,9)
            mylcd.lcd_display_string_pos(str(z_acc),2,11)
            
            time.sleep(0.05)
            
        
        elif ( PUSH_SW1 and PUSH_SW2 ) == True: # if not push SW1 & SW2
            
            for Duty in range(0, 101, 5): # Duty is increases by 5% in the range of 0~100%.
                PWM_LED_2.ChangeDutyCycle(Duty)
                PWM_LED_1.ChangeDutyCycle(Duty)
                time.sleep(0.05)
            
            for Duty in range(100, -1, -5): # Duty is reduced by 5% in the range of 0~100%.
                PWM_LED_2.ChangeDutyCycle(Duty)
                PWM_LED_1.ChangeDutyCycle(Duty)
                time.sleep(0.05)
               
            
  
        elif ( PUSH_SW1 and PUSH_SW2 ) == False: # if push SW1 & SW2
            
            # LED 1 OFF & LED2 OFF
            GPIO.output(LED_1, GPIO.LOW)
            GPIO.output(LED_2, GPIO.LOW)
            
            
        

            
            

if __name__=='__main__':
    main()

