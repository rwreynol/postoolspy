from threading import Thread
from pyubx2 import UBXReader
from gnss_corrections import corrections_interface

import math

import serial
import time

class gnss_interface(object):
    '''
    handler object
    '''

    def new_gnss(self,t,msg):
        '''
        new_gnss methods to override in interface
        '''
        pass

class gnss(Thread,corrections_interface):
    '''
    gnss object thread to collect output computer and write correction data
    '''

    def __init__(self):
        '''
        constructor for gnss thread
        '''
        super().__init__()
        self._conn = None # connection
        self._connected = False # connected flag
        self._listeners = [] # listeners 

    def add_listener(self,listener):
        '''
        adds a listener
        '''
        self._listeners.append(listener)

    def send_gnss(self,t,msg):
        '''
        interface methods to share data
        '''

        # send incoming message to all listeners
        for l in self._listeners: l.new_gnss(t,msg)

    def new_rtcm(self,msg):
        '''
        new_rtcm method to override
        '''
        self.write(msg)

    def connect(self):
        '''
        connect method to override
        '''
        pass

    def write(self,msg):
        '''
        write method to override
        '''
        pass

    def disconnect(self):
        '''
        disconnect method to override
        '''
        pass

    def receive(self):
        '''
        reveice method to override
        '''
        pass

    def setup(self):
        '''
        setup method to override
        '''
        pass

    def stop(self):
        '''
        stops the thread
        '''
        self._connected = False
        print('Stopping the stream')

    def run(self):
        '''
        main thread. connects, setups up, reads messages and shuts down
        '''

        # connect to device
        self.connect()

        # setup device
        self.setup()

        # read device in a loop
        while self._connected:
            # receive new message
            (t,msg) = self.receive()

            # check for errors
            if msg is not None: self.send_gnss(t,msg)

        # disconnect from the device
        self.disconnect()
            
class serial_gnss(gnss):
    '''
    gnss object over serial connection
    '''

    def __init__(self,port,baud,rate=10):
        '''
        constructor
        port: port address
        baud: port baud rate
        rate: gnss output data rate
        '''
        super().__init__()
        self._port = port
        self._baud = baud
        self._rate = rate

    def setup(self):
        '''
        setups up the serial port
        '''
        self._parser = UBXReader(self._conn,protfilter=1)
        
    def connect(self):
        '''
        connects to the serial port
        '''
        try:
            self._conn = serial.Serial(self._port,self._baud)
            self._connected = True
            print('Connected to (%s:%d)' % (self._port,self._baud))
        except Exception as e:
            print(str(e))
            print('Error connecting to serial gps')
            self._connected = False

    def disconnect(self):
        '''
        disconnects from serial port
        '''
        try:
            self._conn.close()
            self._conn = None
            print('Disconnected from gnss stream')
        except Exception:
            print('Error closing serial gps')

        self._connected = False

    def receive(self):
        '''
        Receive new message
        '''
        try:
            (raw,msg) = self._parser.read()# read the serial port
            t = time.time()# computer timestamp
            if msg.msgID == 'GGA':# ensure nmea string
                print(raw)# output the raw data
                return (t,raw)
                #if not msg.lat:
                #    return (t,raw)#(time.time(),msg.time,math.nan,math.nan,math.nan,msg.quality,0)
                #return (t,raw)#(time.time(),msg.time,msg.lat,msg.lon,msg.alt,msg.quality,msg.numSV)
            else:
                return (t,None)# return nothing
        except Exception as e:
            print(self.__class__.__name__ + ' ' + str(e))
            return (None,None)
        
    def write(self,msg):
        '''
        writes the message to the serial gps
        '''
        try:
            self._conn.write(msg)
        except Exception as e:
            print(self.__class__.__name__ + ' ' + str(e))

    def checksum(self,string):
        '''
        calculates the nmea checksum for the given string
        '''
        csum = 0
        for s in string:
            csum = csum ^ ord(s)
        return csum
    
class ublox_zedf9p(serial_gnss):
    '''
    ublox zedf9p over serial
    '''

    def setup(self):
        # need to enable NMEA, set data rate and 
        pass



class locosys_gnss(serial_gnss):
    '''
    locosys gps over serial
    '''

    def setup(self):
        '''
        Programs the locosys GPS to RTK at a specified rate
        '''
        # calculate the rate of acquisition
        rate = round(1/self._rate*1000) 
        rate = min(max(100,rate),1000)

        # initialize all commands
        cmds = ['PAIR410,1', # enable SBAS
                'PAIR400,1', # DGPS = RTCM
                'PAIR104,1', # dual band
                'PAIR050,%d' % rate # rate
                ]
        
        # send all commands
        for cmd in cmds:
            string = '$%s*%X\r\n' % (cmd,self.checksum(cmd))
            self._conn.flush()
            self._conn.write(string.encode('utf-8'))
            line = self._conn.readline().decode('utf-8').strip()
            print(string,line)

        # finish the setup
        super().setup()

    def write(self,msg):
        '''
        writes the message to the serial port
        '''
        super().write(msg + b'\r\n')