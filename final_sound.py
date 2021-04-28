import time
import board
import digitalio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
import array
import math

try:
    from audiocore import RawSample
except ImportError:
    from audioio import RawSample

try:
    from audioio import AudioOut
except ImportError:
    try:
        from audiopwmio import PWMAudioOut as AudioOut
    except ImportError:
        pass  # not always supported by every board!

#create object for activation/data recording switch
switch = digitalio.DigitalInOut(board.D7)
switch.direction = digitalio.Direction.INPUT
switch.pull = digitalio.Pull.UP

#create object for input button
button = digitalio.DigitalInOut(board.A2)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.DOWN

#create object for light in button
led = digitalio.DigitalInOut(board.A5)
led.direction = digitalio.Direction.OUTPUT

#Light red led while code is runnning
led2 = digitalio.DigitalInOut(board.D13)
led2.direction = digitalio.Direction.OUTPUT
led2.value = True

# Enable the speaker
spkrenable = digitalio.DigitalInOut(board.SPEAKER_ENABLE)
spkrenable.direction = digitalio.Direction.OUTPUT
spkrenable.value = True

# Set the keyboard object!
# Sleep for a bit to avoid a race condition on some systems
time.sleep(1)
kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(kbd)  # US is currently only option

FREQUENCY = 440  # 440 Hz middle 'A'
SAMPLERATE = 8000  # 8000 samples/second, recommended!

# Generate one period of sine wav.
length = SAMPLERATE // FREQUENCY
sine_wave = array.array("H", [0] * length)
for i in range(length):
    sine_wave[i] = int(math.sin(math.pi * 2 * i / length) * (2 ** 15) + 2 ** 15)

audio = AudioOut(board.SPEAKER)
sine_wave_sample = RawSample(sine_wave)

while True:
    led.value = False
    led2.value = True
    if switch.value == False:
        led.value = True
        audio.play(sine_wave_sample, loop=True)
        time.sleep(0.35)
        audio.stop()
        time.sleep(0.08)
        audio.play(sine_wave_sample, loop=True)
        time.sleep(0.35)
        audio.stop()
        while switch.value == False:
            pass
            led.value = True
            if button.value == True:
                kbd.press(Keycode.LEFT_CONTROL, Keycode.M)
                time.sleep(0.001) #time between key press and release
                kbd.release_all()
                print('pressed')
                audio.play(sine_wave_sample, loop=True)
                time.sleep(0.1)
                audio.stop()
                while button.value == True:
                    pass
                    kbd.release_all()
                    print('release')
                time.sleep(0.001)#sleep for time between button value checks
            else:
                kbd.release_all()
                print('waiting')
            time.sleep(0.001) #sleep for so many seconds between measurements
    elif switch.value == True:
        led.value = False
        audio.play(sine_wave_sample, loop=True)
        time.sleep(1)
        audio.stop()
        while switch.value == True:
            pass
            led.value = False
    time.sleep(0.001)