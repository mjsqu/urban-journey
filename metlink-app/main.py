# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python38_render_template]
# [START gae_python3_render_template]
import datetime

from flask import Flask, render_template, request, jsonify, abort

from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)

METLINK_API_KEY=""

ROUTE_TYPES = {
    "0" :"Tram",
    "1" :"Metro",
    "2" : "Rail",
    "3" : "Bus",
    "4" : "Ferry",
    "5" : "Cable tram",
    "6" : "Aerial lift",
    "7" : "Funicular",
    "11" : "Trolleybus",
    "12" : "Monorail",
}

BUS_REGIONS = {
    100:"Wellington",
    200:"Hutt Valley",
    210:"Wairarapa",
    250:"Porirua",
    300:"Kāpiti",
    }

@app.route('/')
def sqlite_version():
    import sqlite3,json,re
    
    gtfs_db_file = './static/gtfs.db'
    conn = sqlite3.connect(gtfs_db_file)
    
    cur = conn.cursor()
    
    # This query needs to have distinct shapes
    sql_query = """
WITH qr1 as (
SELECT DISTINCT routes.route_id||'_'||ifnull(direction_id,'_') as route_key
                ,json_object(
                  'direction_id',direction_id,
                  'route_type',route_type,
                  'route_description',
                        case
                        when direction_id = '0' then route_desc
                        else route_long_name end,
                  'route_color',route_color,
                  'route_text_color',route_text_color,
                  'route_short_name',route_short_name
                ) as route_info
                ,shape_id
                
FROM   routes
       INNER JOIN
       trips
ON routes.route_id = trips.route_id),
qr2 as (
select
  route_key
  
  ,json(route_info) as route_info
  
  ,shapes.shape_id
  
  ,json_group_array(json_array(
  shapes.shape_pt_lat,
  shapes.shape_pt_lon)) as points
from qr1
INNER JOIN
shapes
ON shapes.shape_id = qr1.shape_id
group by 1,2,3),
qr3 as (
select
  route_key
  ,json(route_info) as route_info
  ,json_group_array(json_object('shape_id',shape_id,'points',json(points))) as shapes
from qr2
group by 1,2)
select route_key, json(route_info), json(shapes) from qr3;
    """
    
    cur.execute(sql_query)
    
    rows = cur.fetchall()
    
    app.logger.info(f"Passing {len(rows)} routes to template")
    
    bus_regions = [v for k,v in BUS_REGIONS.items()]
    
    bus_regions.append('Night')
    
    shapes = {}
    route_types = []
    
    # Loop over results and construct the shapes object and category lists for the template
    for row in rows:
        route_key = row[0]
        lat_lon = json.loads(row[2])
        trip_info = json.loads(row[1])
        route_type = trip_info.get('route_type')
        route_type_name = ROUTE_TYPES.get(route_type)
        route_number = trip_info.get('route_short_name')
        
        shapes[route_key] = {}
        shapes[route_key]['shapes'] = lat_lon
        shapes[route_key]['trip_info'] = trip_info
        shapes[route_key]['route_type_name'] = route_type_name
        
        if (route_type not in route_types):
            route_types.append(route_type)
        
        """
        Parse out the route number (if it is a number)
        
        Then get the region it is based in, using BUS_REGIONS
        
        e.g. <100 - Wellington, <200 Hutt Valley etc.
        """
        parsed_route_number = re.match('^(?P<parsed_route_number>\d+)',route_number)
        
        if parsed_route_number:
            parsed_route_number = parsed_route_number.groupdict().get('parsed_route_number')
            
            for route_num_max,region_name in BUS_REGIONS.items():
                if int(parsed_route_number) < route_num_max:
                    
                    bus_region = BUS_REGIONS[route_num_max]
                    
                    shapes[route_key]['bus_region'] = bus_region
                    
                    app.logger.debug(f"{route_number} - {parsed_route_number} in region {bus_region}")
                    # If we have found the route is less than a particular maximum then stop
                    # e.g. if we are <100 then Wellington
                    break


    """
    shapes = {"10_1":{"shapes":[[x,y][z,w]],"trip_info":}}
    
                      'direction_id',direction_id,
                  'route_type',route_type,
                  'route_description',
                        case
                        when direction_id = '0' then route_desc
                        else route_long_name end,
                  'route_color',route_color,
                  'route_text_color',route_text_color,
                  'route_short_name',route_short_name
    
    """
    
    return render_template(
        'index.html',
        shapes=shapes,
        route_types=route_types,
        bus_regions=bus_regions,
    )
        
@app.route('/vehicle_locations', methods=['POST'])
def vehicle_locations():
    import os, requests
    METLINK_API_KEY = os.environ.get('METLINK_API_KEY')
    
    selected_routes = request.get_json()
    
    # Do not allow empty/blank selections
    if selected_routes == None:
        abort(400)
        
    app.logger.info(f"Requested routes: {selected_routes}")

    metlink_response = requests.get(
    'https://api.opendata.metlink.org.nz/v1/gtfs-rt/vehiclepositions',
    headers={
            'X-API-KEY': METLINK_API_KEY,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    )
    
    """
    Filter the requests
    """
    metlink_response_json = metlink_response.json()
    
    filtered_results = [vehicle for vehicle in metlink_response_json.get('entity') if (f"{vehicle.get('vehicle').get('trip').get('route_id')}_{vehicle.get('vehicle').get('trip').get('direction_id')}" in selected_routes)]
    
    """
    Construct a new object with just:
    route_direction, bearing, position
    """
    vehicle_locations = []
    for vehicle_info in [r.get('vehicle') for r in filtered_results]:
        
        vehicle_response = {}
        
        vehicle_response['route_and_direction'] = f"{vehicle_info.get('trip').get('route_id')}_{vehicle_info.get('trip').get('direction_id')}"
        vehicle_response['position'] = vehicle_info.get('position')
        
        vehicle_locations.append(vehicle_response)

    return jsonify(vehicle_locations)

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python3_render_template]
# [END gae_python38_render_template]
