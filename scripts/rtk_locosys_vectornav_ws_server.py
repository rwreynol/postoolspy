from postoolspy.imu_stream import vectornav_imu
from postoolspy.gnss_stream import locosys_gnss
from postoolspy.pos_outstream import websocket_client
from postoolspy.gnss_corrections import ntrip_corrections
from postoolspy.pos_outstream import positioning_file

import time
import yaml
import sys
import os
import asyncio

async def main():
    settings = None

    file = os.path.join(os.path.dirname(__file__),'settings.yaml')
        
    with open(file,'r') as file:
        settings = yaml.safe_load(file)
        print(settings)

    if settings == None:
        sys.exit(1)

    rtcm = ntrip_corrections(settings['corrections']['connection']['address'],
                            settings['corrections']['connection']['mountpoint'],
                            settings['corrections']['connection']['user'],
                            settings['corrections']['connection']['password'],
                            settings['corrections']['connection']['port'],
                            org='EMSG')

    imu = vectornav_imu(settings['imu']['connection']['port'],
                        settings['imu']['connection']['baud'])
    

    gps = locosys_gnss(settings['gnss']['connection']['port'],
                       settings['gnss']['connection']['baud'],
                       rate=10)

    
    dest = (settings['output']['connection']['address'],
        settings['output']['connection']['port'])
    serv = websocket_client(dest)

     
    rtcm.add_listener(gps)
    imu.add_listener(serv)
    gps.add_listener(serv)

    rtcm.start()
    imu.start()
    gps.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('User terminated')

    gps.stop()
    imu.stop()
    rtcm.stop()

if __name__ == '__main__':
    asyncio.run(main())