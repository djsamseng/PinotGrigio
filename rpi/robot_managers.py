import time
import math
import smbus

class ServoManager():
    def __init__(self):
        self.pwm = Servo()

    def look_right(self, right_degrees):
        if (20 <= right_degrees and right_degrees <= 160):
            self.pwm.setServoPwm('0', right_degrees)
        else:
            print("Invalid look_right=", right_degrees)

    def look_down(self, down_degrees):
        diff_from_90 = down_degrees - 90
        up_degrees = 90 - diff_from_90 # 90 = 90  70,90,140
        if (10 <= up_degrees and up_degrees <= 110):
            self.pwm.setServoPwm('1', up_degrees)
        else:
            print("Invalid look_down=", down_degrees, "up_degrees=", up_degrees)


class MotorManager():
    def __init__(self):
        pass


class PCA9685:
    # ============================================================================
    # Raspberry Pi PCA9685 16-Channel PWM Servo Driver
    # ============================================================================

    # Registers
    __SUBADR1            = 0x02
    __SUBADR2            = 0x03
    __SUBADR3            = 0x04
    __MODE1              = 0x00
    __PRESCALE           = 0xFE
    __LED0_ON_L          = 0x06
    __LED0_ON_H          = 0x07
    __LED0_OFF_L         = 0x08
    __LED0_OFF_H         = 0x09
    __ALLLED_ON_L        = 0xFA
    __ALLLED_ON_H        = 0xFB
    __ALLLED_OFF_L       = 0xFC
    __ALLLED_OFF_H       = 0xFD

    def __init__(self, address=0x40, debug=False):
        self.bus = smbus.SMBus(1)
        self.address = address
        self.debug = debug
        self.write(self.__MODE1, 0x00)
    
    def write(self, reg, value):
        # Writes an 8-bit value to the specified register/address 
        self.bus.write_byte_data(self.address, reg, value)
      
    def read(self, reg):
        # Read an unsigned byte from the I2C device
        result = self.bus.read_byte_data(self.address, reg)
        return result
    
    def setPWMFreq(self, freq):
        prescaleval = 25000000.0 # 25MHz
        prescaleval /= 4096.0 # 12-bit
        prescaleval /= float(freq)
        prescaleval -= 1.0
        prescale = math.floor(prescaleval + 0.5)


        oldmode = self.read(self.__MODE1);
        newmode = (oldmode & 0x7F) | 0x10 # sleep
        self.write(self.__MODE1, newmode) # go to sleep
        self.write(self.__PRESCALE, int(math.floor(prescale)))
        self.write(self.__MODE1, oldmode)
        time.sleep(0.005)
        self.write(self.__MODE1, oldmode | 0x80)

    def setPWM(self, channel, on, off):
        # Sets a single PWM channel
        self.write(self.__LED0_ON_L + 4 * channel, on & 0xFF)
        self.write(self.__LED0_ON_H + 4 * channel, on >> 8)
        self.write(self.__LED0_OFF_L + 4 * channel, off & 0xFF)
        self.write(self.__LED0_OFF_H + 4 * channel, off >> 8)
    def setMotorPwm(self, channel, duty):
        self.setPWM(channel, 0, duty)
    def setServoPulse(self, channel, pulse):
        # Sets the Servo Pulse. The PWM frequency must be 50HZ. Period is 20ns
        pulse = pulse * 4096 / 20000
        self.setPWM(channel, 0, int(pulse))

class Servo:
    def __init__(self):
        self.PwmServo = PCA9685(0x40, debug=True)
        self.PwmServo.setPWMFreq(50)
        self.PwmServo.setServoPulse(8,1500)
        self.PwmServo.setServoPulse(9,1500)
    def setServoPwm(self,channel,angle,error=10):
        angle=int(angle)
        if channel=='0':
            self.PwmServo.setServoPulse(8,2500-int((angle+error)/0.09))
        elif channel=='1':
            self.PwmServo.setServoPulse(9,500+int((angle+error)/0.09))
        elif channel=='2':
            self.PwmServo.setServoPulse(10,500+int((angle+error)/0.09))
        elif channel=='3':
            self.PwmServo.setServoPulse(11,500+int((angle+error)/0.09))
        elif channel=='4':
            self.PwmServo.setServoPulse(12,500+int((angle+error)/0.09))
        elif channel=='5':
            self.PwmServo.setServoPulse(13,500+int((angle+error)/0.09))
        elif channel=='6':
            self.PwmServo.setServoPulse(14,500+int((angle+error)/0.09))
        elif channel=='7':
            self.PwmServo.setServoPulse(15,500+int((angle+error)/0.09))


