from machine import Pin, Timer,UART
from time import sleep, sleep_ms, ticks_ms, ticks_diff
from devices import Motor, Sensor

loopflag = True
debugflag = False
startsignal = False
lasterror = (0,0) #error, timestamp
basespeed = 70
Kp = 30
Kd = 200
prevval = []
#---------------------------------------------------------------------
def measure(tim):
    global prevval
    exestart = ticks_ms()
    #val = [LL.inpin.read(),L.inpin.read(),M.inpin.read(),R.inpin.read(),RR.inpin.read()]
    val = [LL.check(),L.check(),M.check(),R.check(),RR.check()]
    if val != prevval:
        uart.write(str(val) + str(ticks_ms() - exestart) + '\n\r')
    prevval = val
    return val

# ---------------------------------------------------------------

def incommand(cmd):
    cmd = cmd.decode().strip()
    uart.write(cmd + '\n\r') # echo
    
    if cmd == 'led':
        led.value(not led.value())
        
    if cmd[:4] == 'move':
        speed = int(cmd[4:])
        uart.write('moving with speed ' + str(speed) + '\n\r')
        uart.write(str(rm.mv(speed)) + '\n\r')
        uart.write(str(lm.mv(speed)) + '\n\r')
        
    if cmd == 'b':    #break
        global loopflag
        loopflag = False
        
    if cmd == 'start':
        global startsignal
        global Kp
        global Kd
        global basespeed
        startsignal = True
        uart.write("Started with: Kp = {}, Kd = {}, base speed = {}\n\r".format(Kp,Kd,basespeed))
        
    if cmd == 's':    #stop
        global startsignal
        startsignal = False
        rm.mv(0)
        lm.mv(0)
        lasterror = (0,0)
        
    if cmd[:2] == 'kp':
        global Kp
        try:
            Kp = int(cmd[2:])
            uart.write('Kp set as: ' + str(Kp) + '\n\r')
        except:
            uart.write('Kp value error: ' + cmd[2:] + '\n\r')
            
    if cmd[:2] == 'kd':
        global Kd
        try:
            Kd = int(cmd[2:])
            uart.write('Kd set as: ' + str(Kd) + '\n\r')
        except:
            uart.write('Kd value error: ' + cmd[2:] + '\n\r')
            
    if cmd[:2] == 'bs':
        global basespeed
        try:
            basespeed = int(cmd[2:])
            uart.write('basespeed set as: ' + str(basespeed) + '\n\r')
        except:
            uart.write('basespeed value error: ' + cmd[2:] + '\n\r')
    
    if cmd == 'db':
        global debugflag
        debugflag = not debugflag
        uart.write('Debugging messages: ' + str(debugflag) + '\n\r')

# ---------------------------------------------------------------
def regulator():
    global basespeed
    global Kp
    global Kd
    global lasterror
    readings = [LL.check(),L.check(),M.check(),R.check(),RR.check()]
    #uart.write(str(readings) + '\n\r')
    weights = [-2, -1, 0, 1, 2]
    error = 0
    counter = 0
    for i in range(len(weights)):
        if readings[i] == 1:
            error += weights[i]
            counter += 1
    if counter != 0:
        error = error/counter
    elif counter == 0 and (lasterror[0] < 0):	# v2.1 change
        error = -3
    elif counter == 0 and (lasterror[0] > 0):	# v2.1 change
        error = 3
    else:
        error = 0
    
    timenow = ticks_ms()
    derror = 0
    if error != lasterror[0] and lasterror[1] != 0:
        timenow = ticks_ms()
        dt = timenow - lasterror[1] + 1
        derror = (error - lasterror[0])/dt
        if debugflag:
            x = Kd*derror
            uart.write("Differential correction = {}\n\r".format(x))
        
    lasterror = (error,timenow)
    if error == 0:
        rm.mv(basespeed)
        lm.mv(basespeed)
        if debugflag:
            uart.write('error: ' + str(error) + ' Lmv: ' + str(basespeed) +' Rmv: ' + str(basespeed) + '\n\r')
            
    if error > 0:
        rmv = int(basespeed - Kp*error - Kd*derror)
        rm.mv(rmv)
        lm.mv(basespeed)
        if debugflag:
            uart.write('error: ' + str(error) + ' Lmv: ' + str(basespeed) +' Rmv: ' + str(rmv) + '\n\r')
        
    if error < 0:
        lmv = int(basespeed + Kp*error + Kd*derror)
        lm.mv(lmv)
        rm.mv(basespeed)
        if debugflag:
            uart.write('error: ' + str(error) + ' Lmv: ' + str(lmv) +' Rmv: ' + str(basespeed) + '\n\r')

            
    
    
    
#----------------------------------------------------------------

led = Pin(2,Pin.OUT)
LL = Sensor(32)
L = Sensor(35,threshold=100)
M = Sensor(34)
R = Sensor(39)
RR = Sensor(36)
rm = Motor(5,18,19)
lm = Motor(17,16,4)
uart.write("Initialized. Kp = {}, Kd = {}, base speed = {}\n\r".format(Kp,Kd,basespeed))

#tim = Timer(0)
#tim.init(mode=Timer.PERIODIC, period=50, callback=measure)

#---MAIN LOOP---------------------------------------------
while True:
    if uart.any(): #handle incoming commands
        incommand(uart.read())
    if loopflag == False: #stop the motors and break the loop
        rm.mv(0)
        lm.mv(0)
        break
    
    if startsignal:
        regulator()
    

    
    


#---------------------------------------------------------
# led = Pin(2,Pin.OUT)
# led.on()
# sleep(1)
# led.off()
    