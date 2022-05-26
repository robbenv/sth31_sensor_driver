import machine 
import time
import struct

class SHT31(object):

    I2C_ADDR = 0x44 
    SINGLE_SHOT_MODE = 0x2C06
    PERIODIC_DATA_ACQUISITION_MODE =  0x2236
    FETCH_DATA = 0xE000
    
    def __init__(self):
        self.i2c = machine.SoftI2C(
            scl=machine.Pin(
                machine.Pin.cpu.B8, machine.Pin.OUT, machine.Pin.PULL_UP),
            sda=machine.Pin(
                machine.Pin.cpu.B9, machine.Pin.OUT, machine.Pin.PULL_UP),
            freq=100000,
            timeout = 255)

    def __crc(self, data):
        crc = 0xFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc <<= 1
                    crc ^= 0x31
                else:
                    crc <<= 1
        return crc & 0xFF

    #check crc, if no error, return 4 byte data value
    def __unpack(self, data):
        length = len(data)
        crc = [None] * (length // 3)
        word = [None] * (length // 3)
        for i in range(length // 6):
            word[i * 2], crc[i * 2], word[(i * 2) + 1], crc[(i * 2) + 1] = struct.unpack(
                ">HBHB", data[i * 6 : (i * 6) + 6]
            )
            if crc[i * 2] == self.__crc(data[i * 6 : (i * 6) + 2]):
                length = (i + 1) * 6
        for i in range(length // 3):
            if crc[i] != self.__crc(data[i * 3 : (i * 3) + 2]):
                raise RuntimeError("CRC mismatch")
        return word[: length // 3]        

    def __single_shot_measure(self):
        self.__issue_command(
            self.SINGLE_SHOT_MODE.to_bytes(
                2, "big"))
    
    def __issue_command(self, command):
            self.i2c.writeto(
                self.I2C_ADDR, bytes(command), True)
            
            

            # for x in raw_data:
            #     xx = "0x{:02x}".format(x)
            #     print(xx)
            #     print(xx)
            
            # data = (raw_data[0] << 8) + raw_data[1], (raw_data[3] << 8) + raw_data[4]
            # print(str(data))
    
    def __periodic_measure(self):
        self.__issue_command(
            self.PERIODIC_DATA_ACQUISITION_MODE.to_bytes(
                2, "big"))

    def read_data(self):
        raw_data = self.__issue_command(
            self.FETCH_DATA.to_bytes(
                2, "big"))
        raw_data = self.i2c.readfrom(
                self.I2C_ADDR, 6, True)

        try:
             data = self.__unpack(raw_data)
        except RuntimeError:
            print("CRC mismatch") 

        temp = -45 + (175 * (data[0] / 65535))
        humi = 100 * (data[1] / 65535)
        return temp, humi

    # def start_read_data(self, timer_id):
    #     self.__single_shot_measure()
    #     time.sleep_ms(15)
    #     return self.__read_data()
    
    def start_measurement(self):
        self.__periodic_measure()
        
    # def read_datßa(self, interval):
    #     timer = machine.Timer(-1)
    #     timer.init(
    #         mode=machine.Timer.PERIODIC,
    #         period=interval,
    #         callback = self.start_read_data)        
