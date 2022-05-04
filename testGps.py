from pa1010d import PA1010D
import time

gps = PA1010D()

while(True):
    res = gps.update(wait_for="GGA", timeout=5)
    if res:
        print('Timestamp: ' + str(gps.timestamp) + ' | Lat: ' + str(round(gps.latitude, 5)) + ', Lon: ' + str(round(gps.longitude, 5)) + ' | alt: ' + str(gps.altitude) + ' | sat: ' + str(gps.num_sats) + ' | spd: ' + str(round(gps.speed_over_ground, 2)) + ' | fix: ' + str(gps.gps_qual))
    # print()