from postoolspy.imu_stream import vectornav_imu
from postoolspy.gnss_stream import serial_gnss
from postoolspy.pos_outstream import websocket_client
from postoolspy.gnss_corrections import ntrip_corrections
from postoolspy.pos_outstream import positioning_file

import time
import yaml
import sys
import os
import asyncio
from pathlib import Path

p = Path(__file__).resolve()
while True:
    file_name = "hfemi-rp-settings.yaml"
    cand = p.parent / file_name
    if cand.is_file():
        with open(cand, "r", encoding="utf-8") as f:
            settings = yaml.safe_load(f) or sys.exit(f"{file_name} has no `server` field.")
        break
    if p.parent == p:
        sys.exit("hfemi-rp-settings.yaml not found anywhere above this script")
    p = p.parent

async def main():


    # rtcm = ntrip_corrections(settings['postoolspy']['corrections']['connection']['address'],
    #                         settings['postoolspy']['corrections']['connection']['mountpoint'],
    #                         settings['postoolspy']['corrections']['connection']['user'],
    #                         settings['postoolspy']['corrections']['connection']['password'],
    #                         settings['postoolspy']['corrections']['connection']['port'],
    #                         org='EMSG')

    imu = vectornav_imu(settings['postoolspy']['imu']['connection']['port'],
                        settings['postoolspy']['imu']['connection']['baud'])
    

    gps = serial_gnss(settings['postoolspy']['gnss']['connection']['port'],
                       settings['postoolspy']['gnss']['connection']['baud'],
                       rate=10)

    
    dest = (settings['postoolspy']['output']['connection']['address'],
        settings['postoolspy']['output']['connection']['port'])
    serv = websocket_client(dest)

     
    # rtcm.add_listener(gps)
    imu.add_listener(serv)
    gps.add_listener(serv)

    # rtcm.start()
    imu.start()
    gps.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('User terminated')

    gps.stop()
    imu.stop()
    # rtcm.stop()

if __name__ == '__main__':
    asyncio.run(main())