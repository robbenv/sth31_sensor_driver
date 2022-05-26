from SHT31 import SHT31
import json
import socket
import time
import machine
import sys

class Observer(object):
    def __init__(self):
        self.sht31 = SHT31()
        self.sht31.start_measurement()

    def post_result(self, timer_id):
        # if self.scd40.check_data_available():
        temp, humi = self.sht31.read_data()
        print("temp = " + str(temp) + "  " + "humi = " + str(humi))
        rest_sock = self.rest_init()
        self.rest_write(
            rest_sock,
            json.dumps(
                # {"records": [
                # {"resource": "temperature", "data": temp},
                # {"resource": "humidity", "data": humi}]}), )
                {"temperature": temp, "humidity": humi}))
        rest_sock.close()

    def start_periodic_measurement(self, interval):
        timer = machine.Timer(-1)
        timer.init(
            mode=machine.Timer.PERIODIC,
            period=interval,
            callback=self.post_result)

    def rest_init(self):
        sock = socket.socket()
        addr = socket.getaddrinfo(self.rest_server, 7896)[0][-1]
        for i in range(8):
            try:
                sock.connect(addr)
                break
            except OSError as e:
                time.sleep(2)
            else:
                print("server unreachable", file=sys.stderr)
                return None
        return sock   
    
    def rest_write(self, socket, payload):
        header = (
            "POST {}?k={}&i={} HTTP/1.1\r\n"
            "Host: {}\r\n"
            "Content-Length: {}\r\n"
            "Content-Type: application/json\r\n\r\n".format(
                self.rest_path, self.api_key, self.device_id,
                self.rest_server,
                len(payload)))
        if socket is not None:
            try:
                req = header + payload
                print(req)
                resp = socket.send(req)
                
                print("resp = " + str(socket.recv(4096)))
                return resp
            except Exception as e:
                print("server unreachable [{}]".format(e),
                    file=sys.stderr)
        return None

    def set_rest_params(self, server, path, api_key, device_id):
        self.rest_server = server
        self.rest_path = path
        self.api_key = api_key
        self.device_id = device_id     
