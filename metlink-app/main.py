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
def root():
    import requests
    import csv
    from metlink import Metlink
    
    # Try out 25 points and add them to the map
    trips = {}
    with open('static/trips.txt','r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            shape_id = row['shape_id']
            if shape_id not in trips.keys():
                trips[shape_id] = {'direction_id':row['direction_id'],
                               'route_id':row['route_id'],
                               'service_id':row['service_id']}
            else:
                print('Unexpected')
    
    shapes = {}
    with open('static/shapes.txt','r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            shape_id = row['shape_id']
            if shape_id not in shapes.keys():
                shapes[shape_id] = {}
                shapes[shape_id]['shape'] = []
                shapes[shape_id]['trip_info'] = trips.get(shape_id,{})
            shapes[shape_id]['shape'].append([float(row['shape_pt_lat']),float(row['shape_pt_lon'])])

    # For the sake of example, use static information to inflate the template.
    # This will be replaced with real information in later steps.
    return render_template('index.html', shapes=shapes)


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
