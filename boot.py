import webrepl
import network
import time
from machine import Pin, Timer

print("booting...")

SSID="YOUR_SSID"
PASSWORD="YOUR_PASSWORD"

def do_connect(led, ssid=SSID, password=PASSWORD, max_attempts=30):
    led.on()
    
    wifi = network.WLAN(network.STA_IF)
    
    if not wifi.isconnected():
        print("connecting to network... ")
        wifi.active(True)
        wifi.connect(ssid, password)
        
        attempts = 0
        while wifi.isconnected() == False and attempts < max_attempts:
            print("waiting for connection...")
            time.sleep(1)
            
            attempts += 1
            
        if not wifi.isconnected():
            print("creating access point...")
            start_ap(led)
            return
            
    ip = wifi.ifconfig()[0]
    print(f"connected on {ip}")
    led.off()
    

def start_ap(led, ssid='pico',password='helloworld'):
    def blink(timer):
        led.toggle()
    
    wap = network.WLAN(network.AP_IF)
    
    wap.config(essid=ssid, password=password)
    
    wap.active(True)
    
    # blinking onboard led
    timer = Timer()
    timer.init(freq=2.5, mode=Timer.PERIODIC, callback=blink)

# wifi connection
led = Pin("LED", Pin.OUT)

do_connect(led)

# webrepl
webrepl.start()