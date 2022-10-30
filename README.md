# urban-journey

## Purpose

Makes use of an extended Metlink-Python module to bring together all approaching buses for a point

Supplies output by MQTT for consumption by IOT devices around the house

## Method

Metlink supplies:

Stops - with lat/long
Routes at those stops
Vehicle positions on those routes

We supply: 
a point on the map
walking radius
approaching bus zone (bounded GPS box)
'gates' through which the buses are plotted
