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

@app.route('/')
def root():
    # Bounds for each track - hardcoded for now
    Adelaide_South = {"latitude":[-41.34311939,-41.3200],"leds":20}
    Adelaide_North = {"latitude":[-41.3197,-41.318],"leds":5}
    Luxford = {"longitude":[174.7757236,174.7775174],"leds":5}
    Russell = {"latitude":[-41.3392639,-41.31706437],"leds":20}
    Rintoul = {"latitude":[-41.31962957,-41.31706437],"leds":5}
    South_Coast = {"longitude": [174.7845709,174.7706202],"leds":5}
    
    # The routes from the mqtt code
    Routes = { 10: {"route":[Adelaide_South,Luxford,Rintoul],"direction_id":0,"output_route":"1"},
    320: {"route":[South_Coast,Adelaide_South,Adelaide_North],"direction_id":1,"output_route":"32x"},
        290: {"route":[Russell],"direction_id":1,"output_route":"29"}
           }
    
    # Build an object that is:
    """
    lines = [[[-41.343,174],[-41.343,175]], ...]
    
    from
    
    {'latitude': [-41.34311939, -41.32], 'leds': 20}
    {'longitude': [174.7757236, 174.7775174], 'leds': 5}
    {'latitude': [-41.31962957, -41.31706437], 'leds': 5}
    {'longitude': [174.7845709, 174.7706202], 'leds': 5}
    {'latitude': [-41.34311939, -41.32], 'leds': 20}
    {'latitude': [-41.3197, -41.318], 'leds': 5}
    {'latitude': [-41.3392639, -41.31706437], 'leds': 20}
    
    The positions script calculates it like this:
    def get_display_led(segment,bus,measure):
    	lowbound = min(segment[measure])
    	highbound = max(segment[measure])
    	div = segment["leds"]
    	led = int( (bus[measure] - lowbound) / ((highbound - lowbound)/div) )
    	return led
    
    """
    
    LAT_LINE = [-41.34,-41.35]
    LON_LINE = [174.75,174.78]
    
    polylines = []
    
    for k,v in Routes.items():
        if v["output_route"] == '29':
            for segment in v.get("route",[]):
                if "latitude" in segment.keys():
                    lowbound = min(segment["latitude"])
                    highbound = max(segment["latitude"])
                    for i in range(segment['leds']):
                        ledposition = (i*(highbound - lowbound)/segment["leds"]) + lowbound
                        polyline = [[ledposition,LON_LINE[0]],[ledposition,LON_LINE[1]]]
                        polylines.append(polyline)
                elif "longitude" in segment.keys():
                    lowbound = min(segment["longitude"])
                    highbound = max(segment["longitude"])
                    for i in range(segment['leds']):
                        ledposition = (i*(highbound - lowbound)/segment["leds"]) + lowbound
                        polyline = [[LAT_LINE[0],ledposition],[LAT_LINE[1],ledposition]]
                        polylines.append(polyline)
    
    return render_template('index.html',polylines=polylines)
    

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
