# LED Plotter

Used with the arduino device to show where the LEDs represent on a map

    {'latitude': [-41.34311939, -41.32], 'leds': 20}
    {'longitude': [174.7757236, 174.7775174], 'leds': 5}
    {'latitude': [-41.31962957, -41.31706437], 'leds': 5}
    {'longitude': [174.7845709, 174.7706202], 'leds': 5}
    {'latitude': [-41.34311939, -41.32], 'leds': 20}
    {'latitude': [-41.3197, -41.318], 'leds': 5}
    {'latitude': [-41.3392639, -41.31706437], 'leds': 20}
    
    The positions script calculates it like this:
    
```
def get_display_led(segment,bus,measure):
	lowbound = min(segment[measure])
	highbound = max(segment[measure])
	div = segment["leds"]
	led = int( (bus[measure] - lowbound) / ((highbound - lowbound)/div) )
	return led
```

(lat - lowbound) / ((highbound - lowbound)/div)

div(lat - low)
----------       = led
(hi - low)




led(hi - low) = div(lat - low)



led(hi - low)/div + low = lat



24/16/2

24/8
=3

48/16
=3