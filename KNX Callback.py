

from knxip.ip import KNXIPTunnel
from knxip.timeupdater import KNXDateTimeUpdater

tun = KNXIPTunnel()
print("Connected to KNX interface")
upd = KNXDateTimeUpdater(tun,
                         dateaddr="0/0/1",
                         timeaddr="0/0/2",
                         updateinterval=3)
upd.send_updates()

upd.run_updater_in_background()

time.sleep(60)