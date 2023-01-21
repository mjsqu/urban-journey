/**
 * Copyright 2018, Google LLC
 * Licensed under the Apache License, Version 2.0 (the `License`);
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an `AS IS` BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// [START gae_python38_log]
// [START gae_python3_log]
'use strict';

window.addEventListener('load', function() {

    // Setting up the map, centred on Wellington
    var southWest = L.latLng(-41.372086, 174.653876),
    northEast = L.latLng(-40.557293, 175.843588),
    bounds = L.latLngBounds(southWest, northEast);
    
    var map = L.map('map',{maxBounds:bounds}).setView([-41.29379439, 174.7823273], 13);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        minZoom: 12,
        maxZoom: 17,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);


    // Add a polyline to the map for each route shape found in shapes (passed from main.py)
    var polylines = [];
    var selectedRoutes = [];
    
    console.log(`Found ${Object.entries(shapes).length} routes to plot`);
    
     for (const [key, value] of Object.entries(shapes)) {

        // Route List Setup
        var route_type = value.trip_info.route_type;
        var route_short_name = value.trip_info.route_short_name;
        
        var cbdiv = document.getElementById('sidebar');
        var checkbox = document.createElement('input');
        checkbox.type = "checkbox";
        checkbox.name = key;
        checkbox.value = "value";
        checkbox.id = key;

        var label = document.createElement('label')
        label.htmlFor = key;
        label.style.color = '#'+value.trip_info.route_text_color;
        label.style.backgroundColor = '#'+value.trip_info.route_color;
        label.appendChild(document.createTextNode(route_short_name+' - '+value.trip_info.route_description+' ('+route_type+')'));
        
        document.body.appendChild(cbdiv);
        
        if (document.getElementById('route_type_'+route_type)) {
          if (route_type == 3) {
            if (route_short_name.startsWith('N')) {
              document.getElementById('Night').appendChild(checkbox);
              document.getElementById('Night').appendChild(label);
            }
            else if (parseInt(route_short_name) < 100) {
              document.getElementById('Wgn').appendChild(checkbox);
              document.getElementById('Wgn').appendChild(label);
            }
            else if (parseInt(route_short_name) < 200) {
              document.getElementById('Hutt').appendChild(checkbox);
              document.getElementById('Hutt').appendChild(label);
            }
            else if (parseInt(route_short_name) < 210) {
              document.getElementById('Wai').appendChild(checkbox);
              document.getElementById('Wai').appendChild(label);
            }
            else if (parseInt(route_short_name) < 250) {
              document.getElementById('Por').appendChild(checkbox);
              document.getElementById('Por').appendChild(label);
            }
            else if (parseInt(route_short_name) < 300) {
              document.getElementById('Kap').appendChild(checkbox);
              document.getElementById('Kap').appendChild(label);
            }
            else {
            document.getElementById('route_type_'+route_type).appendChild(checkbox);
            document.getElementById('route_type_'+route_type).appendChild(label);
            }
          }
          
          else {
            document.getElementById('route_type_'+route_type).appendChild(checkbox);
            document.getElementById('route_type_'+route_type).appendChild(label);
          }
        }
        else {
          document.getElementById('spare').appendChild(checkbox)
          document.getElementById('spare').appendChild(label)
        }
        //cbdiv.appendChild(checkbox);
        //cbdiv.appendChild(label);
        // END of route list setup

        for (const shape of value.shapes) {
          
        var firstpolyline = new L.Polyline(shape.points, {
            // set a className so styling can be handled (and modified) by CSS
            //className: 'wiggle',
            color: '#'+value.trip_info.route_color,
            id: key
        });
        // define a mouseover that displays information
        firstpolyline.on('mouseover', (e) => {
            //document.getElementById('testspan').innerHTML = JSON.stringify(value.trip_info);
        });


        firstpolyline.addTo(map);
        polylines.push(firstpolyline);
        }
    }

    // store the old markers so they can be removed on each call
    var old_markers = [];
    
    // repeating function getting vehicle positions
    function updateVehicles() {
        fetch('/vehicle_locations', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify(selectedRoutes)
            })
            .then((response) => response.json())
            .then((data) => {
                console.log(data);
                // loop over the last list of markers and remove them all
                for (var m of old_markers) {
                    m.remove();
                };
                // loop over the new data and add it to the map - store the markers in a list for removal next time
                for (const vehicle of data) {
                    var position = vehicle.position;
                    var marker = L.marker([position.latitude, position.longitude])
                    old_markers.push(marker);
                    // only add to the map if the route polyline is visible
                    if ( selectedRoutes.includes(vehicle.route_and_direction) ) {
                      marker.addTo(map);
                    }
                }
            });
    }
    
    updateVehicles();
    console.log("Vehicles updated - polling...");
    const intervalID = setInterval(updateVehicles, 30000);
    
    const shapeCheckBoxes = document.querySelectorAll('input');
    
    for (const shapeCheckBox of shapeCheckBoxes) {
      shapeCheckBox.addEventListener('click', updateDisplay);
    }
    
    function getPolylinebyID(polylineid) {
      for (const polyline of polylines) {
        if (polyline.options.id == polylineid) {
          return polyline;
        }
      }
    }
    
    function updateDisplay() {
      for (const polyline of polylines) {
        //console.log("Removing:"+polyline.options.id);
        polyline.remove();
      }
      selectedRoutes = [];
      for (const shapeCheckBox of shapeCheckBoxes) {
        if (shapeCheckBox.checked) {
          getPolylinebyID(shapeCheckBox.id).addTo(map);
          selectedRoutes.push(shapeCheckBox.id);
        }
      }
      updateVehicles();
    }
});
// [END gae_python3_log]
// [END gae_python38_log]