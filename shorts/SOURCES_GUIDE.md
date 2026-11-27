# Sources: F1 Track Guide shorts

## Lusail (Qatar) – Piastri 2025 pole lap (`guides/2025_lusail/guide.mp4`)
| On screen | Value | Source |
|---|---|---|
| Pole lap | PIA 1:19.387, NOR +0.108 | FIA classification 2025 Qatar GP qualifying; formula1.com results |
| Main straight | 1,068 m | Wikipedia (Lusail International Circuit); ferrari.com Qatar circuit page |
| Top speed 327 km/h, T1 175 km/h 4th, T6 99 km/h 3rd (slowest), T12 292 km/h 7th, T12–T15 all 7th, T16 174 km/h 4th | min speed / gear per corner | OpenF1 `car_data` of this lap (~3.7 Hz; minima can be a few km/h off) |
| Flat out 69 %, on the brakes 12 % | share of telemetry samples with throttle ≥ 98 % / brake on | OpenF1 `car_data` of this lap (~3.7 Hz, approximate) |
| Built in 2004 for MotoGP | Qatar motorcycle Grand Prix held there since 2004 | Wikipedia (Lusail International Circuit) |
| DRS detection 40 m after T15, DRS zone from 305 m after T16 (2025) | FIA stewards document 4, "Circuit Map – Qatar 2025" (27 Nov 2025); also formularapida.net, motorsportweek.com | HUD DRS lamp = OpenF1 `car_data` drs ≥ 10 (flap open) |
| 1,000 light poles | "nearly 4,000 reflectors on 1,000 light poles" | ferrari.com (Hypercar, Qatar circuit page) |
| World's longest pit building | new pit building (50 garages) certified longest in world motorsport by Guinness World Records | racingcircuits.info; 50 garages also motorsportweek.com, gulf-times.com |
| Main grandstand opposite the pit building | "located directly on the Main Straight immediately facing the pit garages" | grandprixgrandtours.com |

Map: centre line from OpenF1 positions (PIA + NOR flying laps); corner numbers/positions from the F1 timing circuit map (api.multiviewer.app, circuit 150); pit lane position, side and exit merge from OpenF1 positions of all 41 pit stops of the 2025 race; at pit entry the timing positions jump straight into the lane, so the entry ramp is drawn as a 150 m taper ending where the data first shows cars in the lane (satellite imagery was not reachable from the build environment). Drawn schematically: track ~2x real width (lateral offsets of pit lane/buildings shifted out accordingly), pit entry ramp, light-pole positions (evenly spaced), building depth, 50 garage doors evenly spaced. The artificial-grass verges were left out of the drawing.
2025 car (pre-2026 rules); data © OpenF1 (CC BY-NC-SA 4.0, non-commercial).
