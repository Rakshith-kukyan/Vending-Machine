# Servos and the Pico
import board, pwmio, time
from adafruit_motor import servo
# setup servo
pwm = pwmio.PWMOut(board.GP16, frequency=50)
servo_1 = servo. Servo (pwm, min_pulse = 650, max_pulse = 2500)
# set angle property in range 0 to 180
servo_1.angle = 180
time.sleep(2.0)
servo_1.angle = 160
time.sleep(2.0)
servo_1.angle = 140
time.sleep(2.0)