from machine import Pin, PWM, ADC, UART
from time import sleep

class Motor():
    def __init__(self,gpionum_in1,gpionum_in2, gpionum_pwm, minpwm = 340):
        self.minpwm = minpwm
        self.in1 = Pin(gpionum_in1,Pin.OUT)
        self.in2 = Pin(gpionum_in2,Pin.OUT)
        self.pwm = PWM(Pin(gpionum_pwm))
    
    def mv(self, mv):
        if mv == 0:
            self.in1.off()
            self.in2.off()
            #print('motor stopped')
            return
        
        if mv > 100:
            mv = 100
        if mv < -100:
            mv = -100
        
        
        #uart.write('converted mv: {}\n\r'.format(mv))
                    
        if mv > 0:
            self.in1.on()
            self.in2.off()
            mv = int(self.minpwm + (1023-self.minpwm)*mv/100)
            self.pwm.duty(mv)
            return(mv)
            
        if mv < 0:
            self.in1.off()
            self.in2.on()
            mv = int(self.minpwm + (1023-self.minpwm)*(-mv)/100)
            self.pwm.duty(mv)
            return(mv)

#---------------------------------------------------------
class Sensor():
    def __init__(self,gpionum,threshold=300):
        self.inpin = ADC(Pin(gpionum))
        self.inpin.atten(ADC.ATTN_11DB)
        self.thr = threshold
        
    def check(self):
        val = self.inpin.read()
        if val < self.thr:
            return 0
        else:
            return 1
    
    
