'''
This is running on an adafruit feather M0 Express PRODUCT ID: 3403
Other adafruit accessories:
    INA219B breakout board for high side voltage and DC current draw over I2C  PRODUCT ID: 904
    Monochrome 128x32 I2C OLED graphic display with driver chip SSD1306  PRODUCT ID: 931
    Rotary Encoder  PRODUCT ID: 377


'''


import board
import busio
import digitalio
#from digitalio import DigitalInOut
import time
#import rotaryio
import adafruit_ssd1306
import adafruit_ina219

i2c = busio.I2C(board.SCL, board.SDA)

#reset_pin = DigitalInOut(board.D5) # any pin!
oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

ina219 = adafruit_ina219.INA219(i2c)

led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT


LIT_TIMEOUT = 5 

# Encoder button is a digital input with pullup on D2
button = digitalio.DigitalInOut(board.D12)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP
 
# Rotary encoder inputs with pullup on D3 & D4
rot_a = digitalio.DigitalInOut(board.D11)
rot_a.direction = digitalio.Direction.INPUT
rot_a.pull = digitalio.Pull.UP
rot_b = digitalio.DigitalInOut(board.D6)
rot_b.direction = digitalio.Direction.INPUT
rot_b.pull = digitalio.Pull.UP

# time keeper, so we know when to turn off the LED
timestamp = time.monotonic()

######################### MAIN LOOP ##############################
 
# the counter counts up and down, it can roll over! 16-bit value
encoder_counter = 0
# direction tells you the last tick which way it went
encoder_direction = 0
 
# constants to help us track what edge is what
A_POSITION = 0
B_POSITION = 1
UNKNOWN_POSITION = -1  # initial state so we know if something went wrong
 
rising_edge = falling_edge = UNKNOWN_POSITION

# get initial/prev state and store at beginning
last_button = button.value
rotary_prev_state = [rot_a.value, rot_b.value]
 
while True:
    # reset encoder and wait for the next turn
    encoder_direction = 0
 
    # take a 'snapshot' of the rotary encoder state at this time
    rotary_curr_state = [rot_a.value, rot_b.value]
 
    if rotary_curr_state != rotary_prev_state:
        #print("Changed")
        if rotary_prev_state == [True, True]:
            # we caught the first falling edge!
            if not rotary_curr_state[A_POSITION]:
                #print("Falling A")
                falling_edge = A_POSITION
            elif not rotary_curr_state[B_POSITION]:
                #print("Falling B")
                falling_edge = B_POSITION
            else:
                # uhh something went deeply wrong, lets start over
                continue
 
        if rotary_curr_state == [True, True]:
            # Ok we hit the final rising edge
            if not rotary_prev_state[B_POSITION]:
                rising_edge = B_POSITION
                # print("Rising B")
            elif not rotary_prev_state[A_POSITION]:
                rising_edge = A_POSITION
                # print("Rising A")
            else:
                # uhh something went deeply wrong, lets start over
                continue
 
            # check first and last edge
            if (rising_edge == A_POSITION) and (falling_edge == B_POSITION):
                encoder_counter -= 1
                encoder_direction = -1
                #print("%d dec" % encoder_counter)
            elif (rising_edge == B_POSITION) and (falling_edge == A_POSITION):
                encoder_counter += 1
                encoder_direction = 1
                #print("%d inc" % encoder_counter)
            else:
                # (shrug) something didn't work out, oh well!
                encoder_direction = 0
 
            # reset our edge tracking
            rising_edge = falling_edge = UNKNOWN_POSITION
 
    rotary_prev_state = rotary_curr_state

    # Check if rotary encoder went down
    #if encoder_direction == -1:
    #    kbd.press(Keycode.CONTROL, Keycode.DOWN_ARROW)
    #    kbd.release_all()
 
    # Button was 'just pressed'
    if (not button.value) and last_button:
        oled.fill(0)
        oled.text('Button pressed!', 0, 0)
        oled.show()
        encoder_counter = 0
        print("Button pressed!")
        #kbd.press(44) #Keycode.SPACE
        #kbd.release_all()
        #ring[dot_location] = PRESSED_DOT_COLOR # show it was pressed on ring
        timestamp = time.monotonic()        # something happened!
    elif button.value and (not last_button):
        oled.fill(0)
        oled.text('Button released!', 0, 0)
        oled.show()
        #print("Button Released!")
        # kbd.press(Keycode.SHIFT, Keycode.SIX)
        #kbd.release_all()
        #ring[dot_location] = DOT_COLOR      # show it was released on ring
        timestamp = time.monotonic()        # something happened!
    last_button = button.value
 
    if encoder_direction != 0:
        timestamp = time.monotonic()        # something happened!
        encoder_counter_txt = str(encoder_counter)
        # spin neopixel LED around!
        #previous_location = dot_location
        #dot_location += encoder_direction   # move dot in the direction
        #dot_location += len(ring)           # in case we moved negative, wrap around
        #dot_location %= len(ring)
        #print("Bus Voltage:   {} V".format(ina219.bus_voltage))
        #print("Shunt Voltage: {} mV".format(ina219.shunt_voltage / 1000))
        #print("Current:       {} mA".format(ina219.current))
        if encoder_direction == 1:
            oled.fill(0)
            oled.text(encoder_counter_txt, 10, 0)
            oled.text(str(ina219.bus_voltage), 30, 25)
            oled.show()
            #ring[dot_location] = DOT_COLOR  # turn on new dot
        else:
            #ring[dot_location] = PRESSED_DOT_COLOR # turn on new dot
            #ring[previous_location] = 0         # turn off previous dot
            oled.fill(0)
            oled.text(encoder_counter_txt, 10, 0)
            oled.text(str(ina219.bus_voltage), 30, 25)
            oled.show()

    if time.monotonic() > timestamp + LIT_TIMEOUT:
        #ring[dot_location] = 0   # turn off ring light temporarily
        oled.fill(0)
        oled.text('waiting', 20, 10)
        oled.show()
