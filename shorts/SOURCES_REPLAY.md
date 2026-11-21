# Sources: race replay 2026 Mexico City GP

Data: [OpenF1](https://openf1.org), session 11404. That covers car positions (~3.7 Hz), laps, running order, intervals, pit stops, race control and the classification.
OpenF1 is unofficial and licensed CC BY-NC-SA 4.0, for non-commercial fan use only. Ask OpenF1 before the channel is monetised.
Raw data is not committed. Fetch it with `engine/replay_fetch.py`, then run `engine/replay_prep.py`.

| On screen | Source |
|---|---|
| Title decider | Crash.net: "a chaotic race to decide the Formula 1 World Champion" |
| Grid: Hamilton on pole, Russell P2, Leclerc P3, Antonelli P4, Verstappen P5 | OpenF1 position at the start; Silverstone report |
| Start: both Ferraris run wide at T4, Verstappen up to P2, Leclerc leads | Silverstone report ("both Ferraris running wide at the front"); position data (VER passes HAM at ~T4, t=246-250 s) |
| Leclerc 5 s penalty | Race control, lap 12: "5 SECOND TIME PENALTY FOR CAR 16 (LEC) - LEAVING THE TRACK AND GAINING AN ADVANTAGE" |
| Antonelli leads, yet to stop (lap ~31) | OpenF1 order; Silverstone ("Hamilton pitted on Lap 28 ... left Antonelli in the lead") |
| Verstappen leads after the stops | OpenF1 order after Antonelli's stop (pit data: lap 43) |
| Bottas: suspension failure, into the barrier at T1 (lap 44). The off-track path and barrier are drawn as an illustration, because position data only shows him stopping just after T1 | Silverstone, GDN Online ("crashed at Turn One on Lap 44 following an apparent high-speed suspension failure"); position data: from ~339 km/h to standstill at T1 |
| Red flag for barrier repairs | Race control (lap 45 RED FLAG); PlanetF1 ("barrier repairs required") |
| Standing restart | Race control "STANDING START"; PlanetF1 |
| Hamilton to P2 at the restart | Silverstone ("passed Leclerc on the run to Turn 1"); position data t=6496.5 s |
| Antonelli to P3 | Silverstone ("into Turn 1 on Lap 48"); position data t=6594.8 s |
| Lindblad and Piastri contact at T2, safety car | Race control (T2 incident PIA/LIN, SC lap 59); Silverstone |
| Hamilton on the attack, Verstappen wins by 0.799 s | Silverstone; OpenF1 classification |
| Antonelli P3, world champion, youngest ever, 20 years 68 days | The Race, Silverstone, GDN Online ("20 years and 68 days") |
| Classification incl. post-race penalties | OpenF1 session_result; Crash.net |

Visual licence: cars are drawn about 3.5 times their real size and track width is exaggerated. Liveries are the official team colours from the data. Positions between samples are interpolated linearly.
