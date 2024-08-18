"""Example on how to read a value from KNX bus."""
import asyncio

from xknx import XKNX
from xknx.core import ValueReader
from xknx.knx import GroupAddress


async def LeseAdresse():
    """Connect and read value from KNX bus."""
    xknx = XKNX()
    await xknx.start()

    for GA in range(0,38):
        Adresse = '0/0/'+ str(GA)
        value_reader = ValueReader(xknx, GroupAddress(Adresse))
        telegram = await value_reader.read()
        if telegram is not None:
            print(telegram)


    await xknx.stop()


# pylint: disable=invalid-name
loop = asyncio.get_event_loop()
loop.run_until_complete(LeseAdresse())
loop.close()
#LeseAdresse()