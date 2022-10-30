import os
from dotenv import load_dotenv
from metlink import Metlink

load_dotenv()

metlink = Metlink(os.environ['METLINK_API_KEY'])
v = metlink.get_vehicle_positions()
for p in v:
  print(p['vehicle_id'])

stops = [7122,7418,7920]
v = metlink.get_stop_predictions(stop_id=7122)

exit()

active_vehicles = [services['vehicle_id'] for services in metlink.get_stop_predictions(stops)] 

vehicle_positions = [buses for buses in metlink.get_vehicle_positions() if buses['vehicle_id'] in active_vehicles]
for position in vehicle_positions:
    print( position.get('bearing'), position.get('latitude'), position.get('longitude') )
