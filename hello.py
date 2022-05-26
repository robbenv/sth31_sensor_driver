
from SHT31 import SHT31
import time
import network
from Observer import Observer

HOST = 'fiware.kerryman.systems'
PORT = 7896
RESOURCE = '/iot/json'
ID = 'urn:ngsi-ld:WeatherObserved:2110112'
Device_ID = 2110112
PATH = '/iot/json'
API_KEY = '1e34796d-1813-4a0a-bd89-a9aa6cb5752f'

def main():

    setup_lan()
    observer = Observer()
    observer.set_rest_params(
            HOST, PATH, API_KEY, Device_ID)
    observer.start_periodic_measurement(5000)
    while True:
      time.sleep(1)

def setup_lan():
  network.LAN().active(True)
  time.sleep_ms(500)



