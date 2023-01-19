import os
import pprint
from time import sleep
from dotenv import load_dotenv
from metlink import Metlink
import paho.mqtt.client as mqtt

mqttc = mqtt.Client()

load_dotenv()

mqttc.username_pw_set(os.environ['MQTT_USER'],os.environ['MQTT_PASS'])
mqttc.connect("milton18.asuscomm.com")

metlink = Metlink(os.environ['METLINK_API_KEY'])

# Bounds for each track:
Adelaide_South = {"latitude":[-41.34311939,-41.3200],"leds":20}
Adelaide_North = {"latitude":[-41.3197,-41.318],"leds":5}
Luxford = {"longitude":[174.7757236,174.7775174],"leds":5}
Russell = {"latitude":[-41.3392639,-41.31706437],"leds":20}
Rintoul = {"latitude":[-41.31962957,-41.31706437],"leds":5}
South_Coast = {"longitude": [174.7845709,174.7706202],"leds":5}

Routes = { 10: {"route":[Adelaide_South,Luxford,Rintoul],"direction_id":0,"output_route":"1"},
    320: {"route":[South_Coast,Adelaide_South,Adelaide_North],"direction_id":1,"output_route":"32x"},
        290: {"route":[Russell],"direction_id":1,"output_route":"29"}
           }

# For each track part on our routes, look for the maximum latitude to act as a northerly filter
max_lat = max([max(track.get('latitude',[-180])) for k,v in Routes.items() for track in v["route"]])
print(f"{max_lat=}")
# for Route 1, direction_id = 1 is Southbound, 0 is Northbound
# for Route 29, direction_id = 1 is Brooklyn - Berhampore - Newtown - Wellington
# for Route 32x, confirmed, direction_id = 1 is Northbound

def get_display_led(segment,bus,measure):
	lowbound = min(segment[measure])
	highbound = max(segment[measure])
	div = segment["leds"]
	led = int( (bus[measure] - lowbound) / ((highbound - lowbound)/div) )
	return led

while True:

    livedata = metlink.get_vehicle_positions()

    mqtt_payload = {}

    for k,v in Routes.items():
        bus_list = []
        active_buses = [buses for buses in livedata if buses['route_id'] == k and buses['latitude'] < max_lat and buses['direction_id'] == v['direction_id']]
        for bus in active_buses:
            print(f"{v['output_route']}: {bus} {v['route']}")
            # v['route'] will contain some segments, go through these and check where the bus is
            for i,segment in enumerate(v['route']):
                if "latitude" in segment.keys():
                    if (
                        bus["latitude"] >= min(segment["latitude"]) 
                        and bus["latitude"] <= max(segment["latitude"])
                   ):
                        led = get_display_led(segment,bus,"latitude")
                        # Now add on the previous segment LED total
                        led += sum([w['leds'] for w in v['route'][:i]])
                        bus_list.append(led)
                if "longitude" in segment.keys():
                   if (
                        bus["longitude"] >= min(segment["longitude"])
                        and bus["longitude"] <= max(segment["longitude"])
                    ):
                        led = get_display_led(segment,bus,"longitude")
		        # Now add on the previous segment LED totals
                        led += sum([w['leds'] for w in v['route'][:i]])
                        bus_list.append(led)

        if len(bus_list) > 0:
            mqtt_payload[v['output_route']] = bus_list

    print(f"{mqtt_payload=}")
    mqttc.publish('bus/positions',str(mqtt_payload))
    sleep(10)

