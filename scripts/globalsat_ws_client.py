from postoolspy.gnss_stream import serial_gnss
from postoolspy.pos_outstream import websocket_client


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

    gps = serial_gnss(settings['gnss']['connection']['port'],
                       settings['gnss']['connection']['baud'])

    
    dest = (settings['output']['connection']['address'],
        settings['output']['connection']['port'])
    
    serv = websocket_client(dest)

    gps.add_listener(serv)

    gps.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('User terminated')

    gps.stop()

if __name__ == '__main__':
    asyncio.run(main())