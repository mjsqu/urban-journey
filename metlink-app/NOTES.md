gtfs db query needs to end up like:


route_id
route_short_name
route_long_name
route_color
route_text_color
direction_id
shape_pt_lon
shape_pt_lat

SELECT distinct routes.route_id||'.'||direction_id,
                routes.route_id,
                case when direction_id = '0'
                then route_desc
                else route_long_name end as route_description,
                route_color,
                route_text_color,
                direction_id,
                shape_pt_lon,
                shape_pt_lat
                
FROM   routes,
       trips,
       shapes,
WHERE routes.route_id = trips.route_id
AND shapes.shape_id = trips.shape_id;
       
For the number 1:

when

Northbound

[@364.0.17528045@]10|10|1|Johnsonville West/Churton Park/Grenada Village - Island Bay|Island Bay - Johnsonville West/Churton Park/Grenada Village|e31837|ffffff|0
[@364.0.17528045@]12|10|1|Johnsonville West/Churton Park/Grenada Village - Island Bay|Island Bay - Johnsonville West/Churton Park/Grenada Village|e31837|ffffff|0
[@364.0.17528045@]7|10|1|Johnsonville West/Churton Park/Grenada Village - Island Bay|Island Bay - Johnsonville West/Churton Park/Grenada Village|e31837|ffffff|0
[@364.0.17528045@]9|10|1|Johnsonville West/Churton Park/Grenada Village - Island Bay|Island Bay - Johnsonville West/Churton Park/Grenada Village|e31837|ffffff|0

Southbound

[@364.0.17528045@]1|10|1|Johnsonville West/Churton Park/Grenada Village - Island Bay|Island Bay - Johnsonville West/Churton Park/Grenada Village|e31837|ffffff|1
[@364.0.17528045@]3|10|1|Johnsonville West/Churton Park/Grenada Village - Island Bay|Island Bay - Johnsonville West/Churton Park/Grenada Village|e31837|ffffff|1
[@364.0.17528045@]5|10|1|Johnsonville West/Churton Park/Grenada Village - Island Bay|Island Bay - Johnsonville West/Churton Park/Grenada Village|e31837|ffffff|1

Results in:

[@364.0.17528045@]10|10|Island Bay - Johnsonville West/Churton Park/Grenada Village|e31837|ffffff|0
[@364.0.17528045@]12|10|Island Bay - Johnsonville West/Churton Park/Grenada Village|e31837|ffffff|0
[@364.0.17528045@]7|10|Island Bay - Johnsonville West/Churton Park/Grenada Village|e31837|ffffff|0
[@364.0.17528045@]9|10|Island Bay - Johnsonville West/Churton Park/Grenada Village|e31837|ffffff|0

[@364.0.17528045@]1|10|Johnsonville West/Churton Park/Grenada Village - Island Bay|e31837|ffffff|1
[@364.0.17528045@]3|10|Johnsonville West/Churton Park/Grenada Village - Island Bay|e31837|ffffff|1
[@364.0.17528045@]5|10|Johnsonville West/Churton Park/Grenada Village - Island Bay|e31837|ffffff|1

When you select "Johnsonville West/Churton Park/Grenada Village - Island Bay" - all three shapes need to show up






WITH qr1 as (
SELECT DISTINCT routes.route_id||'_'||direction_id as route_key,
                case when direction_id = '0'
                then route_desc
                else route_long_name end as route_description,
                route_color,
                route_text_color,
                shape_id
                
FROM   routes,
       trips
WHERE routes.route_id = trips.route_id),
qr2 as (
select
  route_key
  ,route_description
  ,route_color
  ,route_text_color
  ,shapes.shape_id
  ,json_group_array(json_array(
  shapes.shape_pt_lat,
  shapes.shape_pt_lon)) as points
from qr1,shapes
where shapes.shape_id = qr1.shape_id
group by 1,2,3,4,5),
qr3 as (
select
  route_key
  ,route_description
  ,route_color
  ,route_text_color
  ,json_group_array(json_object('shape_id',shape_id,'points',json(points))) as shapes
from qr2
group by 1,2,3,4)
select * from qr3;