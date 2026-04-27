from postoolspy.gnss_stream import serial_gnss
from postoolspy.pos_outstream import websocket_client


import time
import yaml
import asyncio
from pathlib import Path
import sys

async def main():
    p = Path(__file__).resolve()
    while True:
        cand = p.parent / "rf-tools-settings.yaml"
        if cand.is_file():
            with open(cand, "r", encoding="utf-8") as f:
                settings = yaml.safe_load(f)['postoolspy'] or sys.exit("settings.yaml has no `postoolspy` field.")
            break
        if p.parent == p:
            sys.exit("settings.yaml not found anywhere above this script")
        p = p.parent


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