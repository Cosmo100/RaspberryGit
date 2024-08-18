"""Empfängt die Werte der Gruppenadressen alle 2 Minuten, wenn dies an Vitogate über ETS5 eingestellt ist"""
#Pfad: /usr/local/lib/python3.5/dist-packages/xknx-0.8.5-py3.5.egg/xknx/knx/telegram.py

import asyncio
import getopt
import sys
import time

from xknx import XKNX
from xknx.knx import AddressFilter

#Bytposition (null basierend)
BytNr = [92,94,96,98,99,101,103,104,106,110,112,114,115,116,117,118,120,122,124,126,127,129,131,133,134,135,136,137,138,140,142,144,146,147,148,149,151,152,156]
Byts = 180*[0]

async def telegram_received_cb(telegram):
    global BytNr
    #print(time.strftime("%H:%M:%S"), telegram)
    Z=str(telegram)
    Teilen= Z.split('-')
    GrAdr = int(Teilen[0])
    Wert = Teilen[1].split(',')
    #print ("Gruppenadresse=",GrAdr,"BytNr=",BytNr[GrAdr-1])
    #print ("Wert =",Wert)
    #print ("BytNr=",BytNr[GrAdr-1])
    #print ("Länge",len(Wert))
    
    #an der richtigen Stelle im Array ablegen
    for n in range(len(Wert)):  
        Byts[BytNr[GrAdr-1]+n]= int(Wert[n])
        #print (n,BytNr[GrAdr-1]+n,int(Wert[n]))
    
    if GrAdr == 36:
        print(time.strftime("%d.%m.%Y %H:%M:%S"))
        outstr=', '.join(str(x) for x in Byts[92:151])
        print (outstr)
    
    return True

async def monitor(address_filters):
    """Set telegram_received_cb within XKNX and connect to KNX/IP device in daemon mode."""
    xknx = XKNX()
    xknx.telegram_queue.register_telegram_received_cb(telegram_received_cb, address_filters)
    await xknx.start(daemon_mode=True)
    await xknx.stop()


async def main(argv):
    """Parse command line arguments and start monitor."""
    try:
        opts, _ = getopt.getopt(argv, "hf:", ["help", "filter="])
    except getopt.GetoptError:
        show_help()
        sys.exit(2)
    address_filters = None
    for opt, arg in opts:
        if opt == '-h' or opt == '--help':
            show_help()
            sys.exit()
        if opt == '-f' or opt == '--filter':
            address_filters = list(map(AddressFilter, arg.split(',')))
    await monitor(address_filters)


if __name__ == "__main__":
    # pylint: disable=invalid-name
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(sys.argv[1:]))
    loop.close()
