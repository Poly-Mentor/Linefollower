
# This file is executed on every boot (including wake-boot from deepsleep)

#import esp

#esp.osdebug(None)

from machine import UART


def do_connect():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('***', '***')
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())


do_connect()
import webrepl
webrepl.start()

uart = UART(1)
uart.init(rx=13,tx=12,baudrate=115200,bits=8,parity=None,stop=1)
uart.write('initialized\n\r')



