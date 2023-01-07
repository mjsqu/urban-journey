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

window.addEventListener('load', function () {


    var map = L.map('map').setView([-41.29379439,174.7823273], 14);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);


    // shapes
    for (const [key, value] of Object.entries(shapes)) {
        
    var firstpolyline = new L.Polyline(value['shape'], {
	  // set a className so styling can be handled (and modified) by CSS
	  className: 'wiggle'
});
    // define a mouseover that displays information
    firstpolyline.on('mouseover',(e)=>{
  document.getElementById('testspan').innerHTML = JSON.stringify(value['trip_info']);
});


  firstpolyline.addTo(map);
    }
     
    // store the old markers so they can be removed on each call
    var old_markers = [];
    const intervalID = setInterval(myCallback, 3000);
    // Now fetch and plot on the map
    function myCallback() {
     fetch('https://api.opendata.metlink.org.nz/v1/gtfs-rt/vehiclepositions', {
        method: 'GET',
        headers: {
            'X-API-KEY': '',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    })
    .then((response) => response.json())
    .then((data) => 
          {
         // loop over the last list of markers and remove them all
         for (var m of old_markers) {
            m.remove();
         };
         // loop over the new data and add it to the map - store the markers in a list for removal next time 
         for (const vehicle of data['entity']) {
            console.log(vehicle['vehicle']['position']);
            var position = vehicle['vehicle']['position'];
            var marker = L.marker([position['latitude'],position['longitude']])
            old_markers.push(marker);
            marker.addTo(map);
         };
     });
    }
   
>>>>>>> 506705e65c8e614a90270b957e656c9a55d5600c
});
// [END gae_python3_log]
// [END gae_python38_log]
