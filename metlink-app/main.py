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

from flask import Flask, render_template

app = Flask(__name__)

METLINK_API_KEY=""

@app.route('/')
def sqlite_version():
    import sqlite3,json
    
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
    
    shapes = {}
    trips = {}
    for row in rows:
        route_key = row[0]
        shapes[route_key] = {}
        shapes[route_key]['shapes'] = json.loads(row[2])
        shapes[route_key]['trip_info'] = json.loads(row[1])

    return render_template('index.html', shapes=shapes)
        
@app.route('/vehicle_locations', methods=['GET'])
def vehicle_locations():
    import os, requests
    METLINK_API_KEY = os.environ.get('METLINK_API_KEY')

    response = requests.get(
    'https://api.opendata.metlink.org.nz/v1/gtfs-rt/vehiclepositions',
    headers={
            'X-API-KEY': METLINK_API_KEY,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    )
    
    return response.json()

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
