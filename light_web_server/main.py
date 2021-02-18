try:
    import usocket as socket
except:
    import socket

response_404 = """HTTP/1.0 404 NOT FOUND

<h1>404 Not Found</h1>
"""

response_500 = """HTTP/1.0 500 INTERNAL SERVER ERROR

<h1>500 Internal Server Error</h1>
"""

response_template = """HTTP/1.0 200 OK

%s
"""

import machine
import ntptime, utime
from machine import RTC
from time import sleep

pin = machine.Pin(16, machine.Pin.OUT)
sw_pin = machine.Pin(10, machine.Pin.IN)
adc = machine.ADC(0)
pwm = machine.Pin(5, machine.Pin.OUT)
pwm = machine.PWM(pwm)

rtc = RTC()
try:
    seconds = ntptime.time()
except:
    seconds = 0
rtc.datetime(utime.localtime(seconds))

def time():
    body = """<html>
<body>
<h1>Time</h1>
<p>%s</p>
</body>
</html>
""" % str(rtc.datetime())

    return response_template % body



def dummy():
    body = "This is a dummy endpoint"

    return response_template % body

def light():
    body = "{value:" 
    body += str(adc.read())
    body += "}"
    print(body)
    return response_template % body

def led_on():
    pin.value(0)
    body = 'Light ON!'
    print(body)
    return response_template % body

def led_off():
    pin.value(1)
    body = 'Light OFF!'
    print(body)
    return response_template % body

def pwm_cycle():
    for i in range(1000):
        pwm.duty(i)
        sleep(0.005)
    for i in range(1000,0,-1):
        pwm.duty(i)
        sleep(0.005)
    pwm.duty(0)
    body = 'PWM Cycled!'
    print(body)
    return response_template % body

def switch():
    val = sw_pin.value()
    if val == 0:
        body = 'Switch OFF!'
    elif val == 1:
        body = 'Switch ON!'
    print(body)
    return response_template % body

handlers = {
    'time': time,
    'dummy': dummy,
    'led_on': led_on,
    'led_off': led_off,
    'switch': switch,
    'light': light,
    'pwm':pwm_cycle,
}

def main():
    

    s = socket.socket()
    ai = socket.getaddrinfo("0.0.0.0", 8080)
    addr = ai[0][-1]

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind(addr)
    s.listen(5)
    print("Listening, connect your browser to http://<this_host>:8080")

    while True:
        sleep(1)
        res = s.accept()
        client_s = res[0]
        client_addr = res[1]
        req = client_s.recv(4096)
        print("Request:")
        print(req)

        try:
            path = req.decode().split("\r\n")[0].split(" ")[1]
            handler = handlers[path.strip('/').split('/')[0]]
            response = handler()
        except KeyError:
            response = response_404
        except Exception as e:
            response = response_500
            print(str(e))

        client_s.send(b"\r\n".join([line.encode() for line in response.split("\n")]))

        client_s.close()
        print()

main()
