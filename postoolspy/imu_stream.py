from vnpy import *
import time
from threading import Thread

class imu_interface(object):

    def new_imu(self,t,msg):
        pass

class imu(Thread):

    def __init__(self):
        super().__init__()
        self._conn = None
        self._connected = False
        self._listeners = []

    def add_listener(self,listener):
        self._listeners.append(listener)

    def send_imu(self,t,msg):
        for l in self._listeners: l.new_imu(t,msg)

    def connect(self):
        pass

    def disconnect(self):
        pass

    def setup(self):
        pass

    def stop(self):
        self._connected = False

    def run(self):
        self.connect()

        self.setup()

        while self._connected:
            (t,msg) = self.receive()
            time.sleep(.099)

            if msg is not None: self.send_imu(t,msg)

    def checksum(self,string):
        '''
        calculates the nmea checksum for the given string
        '''
        csum = 0
        for s in string:
            csum = csum ^ ord(s)
        return csum

class vectornav_imu(imu):

    def __init__(self,port,baud,rate=10):
        super().__init__()
        self._port = port
        self._baud = baud
        self._rate = rate
        
    def setup(self):
        try:
            self._conn = VnSensor()
            self._conn.connect(self._port,self._baud)
            print('Connected to (%s:%d)' % (self._port,self._baud))
            print('Found %s SN:%d' % (self._conn.read_model_number(),self._conn.read_serial_number()))
            #self._conn.write_async_data_output_type()
            self._conn.write_async_data_output_frequency(self._rate)
            self._conn.write_settings()
            time.sleep(0.1)
            print('Setting rate to %f' % self._conn.read_async_data_output_frequency())
            self._connected = True
        except Exception as e:
            print(str(e))
            print('Error connecting to serial imu')
            self._connected = False

    def disconnect(self):
        try:
            self._conn.disconnect()
            self._conn = None
        except Exception as e:
            print('error disconnected from serial imu')

        self._connected = False

    def receive(self):
        try:
            t = time.time()
            ypr = self._conn.read_yaw_pitch_roll()
            nmea = 'IMU,%f,%f,%f' % (ypr.x,ypr.y,ypr.z)
            nmea = '$%s*%X\r\n' % (nmea,self.checksum(nmea))
            return (t,nmea.encode('utf-8') )
        except Exception as e:
            print(self.__class__.__name__ + ' ' + str(e))
            return (None,None)

