import time
import socket
import machine
import urequests
#import json
import _thread
import ntptime

from machine import Pin
from machine import ADC
from machine import Timer

NOTIFICATION_LED = Pin(16, Pin.OUT)
NOTIFICATION_LED.value(0)

WATER_SIGNAL = ADC(Pin(26))
WATER_POWER = Pin(22, Pin.OUT)
WATER_POWER.value(0)

BUZZER_PIN = 10

#TIME_API = "https://timeapi.io/api/Time/current/zone?timeZone=Europe/Berlin"
IP_BULB = "192.168.189.28"

LOW = 10000
DURATION = 10000#300000

UTC_OFFSET = 1 * 60 * 60

#rtc = machine.RTC()

shutdown = False
new_measurement = False
water_data = LOW

tones = {
    "B0": 31,
    "C1": 33,
    "CS1": 35,
    "D1": 37,
    "DS1": 39,
    "E1": 41,
    "F1": 44,
    "FS1": 46,
    "G1": 49,
    "GS1": 52,
    "A1": 55,
    "AS1": 58,
    "B1": 62,
    "C2": 65,
    "CS2": 69,
    "D2": 73,
    "DS2": 78,
    "E2": 82,
    "F2": 87,
    "FS2": 93,
    "G2": 98,
    "GS2": 104,
    "A2": 110,
    "AS2": 117,
    "B2": 123,
    "C3": 131,
    "CS3": 139,
    "D3": 147,
    "DS3": 156,
    "E3": 165,
    "F3": 175,
    "FS3": 185,
    "G3": 196,
    "GS3": 208,
    "A3": 220,
    "AS3": 233,
    "B3": 247,
    "C4": 262,
    "CS4": 277,
    "D4": 294,
    "DS4": 311,
    "E4": 330,
    "F4": 349,
    "FS4": 370,
    "G4": 392,
    "GS4": 415,
    "A4": 440,
    "AS4": 466,
    "B4": 494,
    "C5": 523,
    "CS5": 554,
    "D5": 587,
    "DS5": 622,
    "E5": 659,
    "F5": 698,
    "FS5": 740,
    "G5": 784,
    "GS5": 831,
    "A5": 880,
    "AS5": 932,
    "B5": 988,
    "C6": 1047,
    "CS6": 1109,
    "D6": 1175,
    "DS6": 1245,
    "E6": 1319,
    "F6": 1397,
    "FS6": 1480,
    "G6": 1568,
    "GS6": 1661,
    "A6": 1760,
    "AS6": 1865,
    "B6": 1976,
    "C7": 2093,
    "CS7": 2217,
    "D7": 2349,
    "DS7": 2489,
    "E7": 2637,
    "F7": 2794,
    "FS7": 2960,
    "G7": 3136,
    "GS7": 3322,
    "A7": 3520,
    "AS7": 3729,
    "B7": 3951,
    "C8": 4186,
    "CS8": 4435,
    "D8": 4699,
    "DS8": 4978,
}

song = [
    "C4",
    "F4",
    "F4",
    "F4",
    "G4",
    "A4",
    "A4",
    "A4",
    "A4",
    "G4",
    "A4",
    "B4",
    "E4",
    "G4",
    "F4",
    "P",
    "C5",
    "C5",
    "A4",
    "D5",
    "C5",
    "C5",
    "B4",
    "B4",
    "B4",
    "B4",
    "G4",
    "C5",
    "B4",
    "B4",
    "A4",
    "A4",
    "P",
    "C4",
    "F4",
    "F4",
    "F4",
    "G4",
    "A4",
    "A4",
    "A4",
    "A4",
    "G4",
    "A4",
    "B4",
    "E4",
    "G4",
    "F4",
    "P",
]

timing = [
    "a",
    "a",
    "s",
    "v",
    "a",
    "a",
    "s",
    "v",
    "a",
    "a",
    "a",
    "v",
    "v",
    "v",
    "v",
    "a",
    "a",
    "a",
    "a",
    "v",
    "a",
    "a",
    "a",
    "v",
    "a",
    "a",
    "a",
    "v",
    "a",
    "a",
    "a",
    "v",
    "a",
    "a",
    "a",
    "s",
    "v",
    "a",
    "a",
    "s",
    "v",
    "a",
    "a",
    "a",
    "v",
    "v",
    "v",
    "v",
    "a",
]


def playtone(frequency, buzzer):
    buzzer.duty_u16(6000)
    buzzer.freq(frequency)


def bequiet(buzzer):
    buzzer.duty_u16(0)


def playsong(mysong, mytiming, buzzerpin):
    notelength = 3
    buzzer = machine.PWM(Pin(buzzerpin))
    print(len(mysong), len(mytiming))

    for i in range(len(mysong)):
        if mysong[i] == "P":
            bequiet(buzzer)

        else:
            playtone(tones[mysong[i]], buzzer)

        if mytiming[i] == "v":
            time.sleep(notelength / 4)

        elif mytiming[i] == "a":
            time.sleep(notelength / 8)

        elif mytiming[i] == "s":
            time.sleep(notelength / 16)

        bequiet(buzzer)
        time.sleep(0.04)  # A little between-note pause


def read_water_level():
    total = 0
    readings = 1000

    # 3.3V output to sensor
    WATER_POWER.value(1)

    time.sleep_ms(10)

    for i in range(readings):
        raw = WATER_SIGNAL.read_u16()
        total += raw

    WATER_POWER.value(0)

    return total / readings


def interrupt_new_data(timer):
    global new_measurement
    global water_data

    water_data = read_water_level()
    new_measurement = True

    print(water_data)

    return


def interrupt_blinking(timer):
    water_data = read_water_level()

    if water_data > LOW:
        NOTIFICATION_LED.value(0)
        timer.deinit()
        return

    NOTIFICATION_LED.toggle()

    return


def notify_bulb():
    toggle_url = "http://" + IP_BULB + "/relay/0?turn=toggle"

    for i in range(4):
        try:
            urequests.get(toggle_url)
        except:
            print("no connection to bulb")

        time.sleep(1.5)


def notify(timer_led):#rtc, timer_led):
    global water_data

    if water_data > LOW:
        return

    hour = time.localtime(time.time() + UTC_OFFSET)[3]
    print("hour", hour)

    if hour >= 22 or hour <= 6:
        return

    # play buzzer song
    try:
        print("do a song")
        _thread.start_new_thread(playsong, (song, timing, BUZZER_PIN))

    except Exception as err:
        print(err)

    # start blinking led
    timer_led.init(mode=Timer.PERIODIC, period=1000, callback=interrupt_blinking)

    notify_bulb()

    return


def set_time_from_network():#time_url, rtc):
    print("pulling time...")

    synced = False
    attempts = 0
    while synced == False and attempts < 10:
        print("waiting for time...")
        time.sleep(0.5)
        try:
            ntptime.settime()
            synced = True
            print("time synced from network with", attempts, "attempts")
        except:
            print("time not synced")

        attempts += 1

    print(time.localtime())


def setup_server():
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]

    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setblocking(False)
    s.bind(addr)
    s.listen(1)

    print("listening on", addr)

    return s


def handle_req(uri):
    global water_data

    if uri == "/shutdown":
        global shutdown
        shutdown = True
        return "server is stopping..."

    if uri == "/":
        sensor_data = f"(raw: {water_data})"

        if water_data <= LOW:
            return "i need water, pls " + sensor_data

        return "i'm fine " + sensor_data


def listen_and_serve(s):
    try:
        cl, addr = s.accept()
        cl.setblocking(True)

        print("client connected from", addr)

        request = cl.recv(1024)
        req = request.decode().split()
        uri = req[1]
        print(req)

        msg = handle_req(uri)

        cl.send("HTTP/1.0 200 OK\r\nContent-type: text/plane\r\n\r\n")
        cl.send(str(msg))

        cl.close()
        print("connection closed")

    except OSError as e:
        pass


def debug_mode():
    debug = Pin(6, Pin.IN, Pin.PULL_UP)

    if debug() == 0:
        print("Debugging...")
        return True

    return False


def main():
    global shutdown
    global new_measurement
    #global rtc

    if debug_mode():
        return

    set_time_from_network()#TIME_API, rtc)
    print("localtime:", time.localtime(time.time() + UTC_OFFSET))
    s = setup_server()

    sensor_timer = Timer(
        mode=Timer.PERIODIC, period=DURATION, callback=interrupt_new_data
    )
    blinking_timer = Timer()

    while not shutdown:
        if new_measurement:
            notify(blinking_timer) #rtc,
            new_measurement = False

        listen_and_serve(s)


if __name__ == "__main__":
    main()
