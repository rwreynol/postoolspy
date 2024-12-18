from postoolspy.gnss_stream import locosys_gnss, gnss_file
from postoolspy.gnss_corrections import ntrip_corrections

import time
import yaml
import os

def main():
    settings = None

    file = os.path.join(os.path.dirname(__file__),'locosys_rtk.yaml')
    
    with open(file,'r') as file:
        settings = yaml.safe_load(file)
        print(settings)

    if settings is None:
        print('error reading settings')
        return 0
    
    # initialize all objects
    rtcm = ntrip_corrections(settings['corrections']['connection']['address'],
                            settings['corrections']['connection']['mountpoint'],
                            settings['corrections']['connection']['user'],
                            settings['corrections']['connection']['password'],
                            settings['corrections']['connection']['port'],
                            org='EMSG')
    
    gnss = locosys_gnss(settings['gnss']['connection']['port'],
                       settings['gnss']['connection']['baud'])
    
    file = gnss_file('nmea.txt')

    # add listeners for rtcm and gps data
    rtcm.add_listener(gnss)
    gnss.add_listener(file)
    
    # start the threads
    rtcm.start()
    gnss.start()

    # wait for 10 seconds
    t0 = time.time()
    try:
        # loop continuously
        while True:
            #get current time
            tnow = time.time()

            # print rtcm bytes received every seconds
            if tnow - t0 > 1:
                t0 = tnow
                print('\nReceived %d RTCM Bytes so far' % gnss.rtcmBytesRecvd)
    except KeyboardInterrupt:
        # stop threads
        rtcm.stop()
        gnss.stop()
        print('Exiting program')

    # wait for all threads to stop and close file
    if gnss.is_alive(): gnss.join()
    if rtcm.is_alive(): rtcm.join()
    file.close()

# main function
if __name__ == '__main__':
    '''
    main
    '''
    main()
