import Jetson.GPIO as GPIO
class Control():
    def __init__(self, yellow, green, blue):
        GPIO.setmode(GPIO.BOARD)
        self.yellowPin = yellow
        self.greenPin = green
        self.bluePin = blue
        GPIO.setup(self.yellowPin, GPIO.OUT)
        GPIO.setup(self.greenPin, GPIO.OUT)
        GPIO.setup(self.bluePin, GPIO.OUT)


    def update_leds(self, command):
        yellow, green, blue, = command
        GPIO.output(self.yellow, yellow)
        GPIO.output(self.green, green)
        GPIO.output(self.blue, blue)

    def shutdown(self):
        GPIO.cleanup()