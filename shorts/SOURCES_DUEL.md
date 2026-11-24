# Sources: quali duel Las Vegas 2026

Data: [OpenF1](https://openf1.org) session 11416: laps (official lap and sector times), location and car_data (~3.7 Hz) for both laps.
The data is unofficial and licensed CC BY-NC-SA 4.0, for non-commercial use only. The raw data is not committed.

| On screen | Source |
|---|---|
| Antonelli fastest, 1:33.893; Verstappen +0.258 (1:34.151) | OpenF1 laps/session_result; formula1.com, Autosport, PlanetF1 |
| Sectors: ANT 26.987 / 32.121 / 34.785, VER 26.701 / 31.757 / 35.693 | OpenF1 laps (official timing) |
| VER ahead by 0.650 s after two sectors; S3 ANT -0.908 s | Sums of the official sectors |
| Antonelli in the tow, 351 km/h (VER max 340) | OpenF1 car_data; RaceFans ("exploited the power of the slipstream"); Antonelli quote on the tow (Autosport live) |
| 5-place grid penalty for ANT (power unit), Verstappen on pole | formula1.com, GrandPrix.com, PlanetF1 |

Accuracy: each car's time-over-distance curve is pinned to its official sector times, so the gap is exact at the sector lines.
Between them it comes from ~3.7 Hz position data (a few hundredths of a second). Below 0.05 s the HUD shows "LEVEL" instead of a leader.
Visual licence: the cars are drawn side by side (each on its own half of the track), as in a ghost overlay; cars and track are exaggerated in size.

## v2 additions (overlay version)
- **Tow:** OpenF1 `location` for all cars during Antonelli's Q3 lap: Lindblad (LIN) was 14–120 m ahead of ANT for the entire lap (~75–86 m on the Strip at 340+ km/h ≈ 0.8 s). During Verstappen's lap no car was within ~225 m for most of the lap → no tow. Matches RaceFans ("exploited the power of the slipstream"), GrandPrix.com ("last-gasp tow") and Antonelli's quote "the tow is so powerful here". LIN is drawn at his real distance gap to ANT (58–74 s of the lap).
- **Top speed:** OpenF1 `car_data`: ANT 351 km/h, VER 340 km/h on their fastest laps.
- **Landmarks:** circuit outline (bacinger/f1-circuits, `toolkit/geo/lv.geojson`) aligned to the data line (similarity fit, rms 16 m). Sphere 36.1208 N, 115.1617 W, 157 m diameter (Wikipedia); Bellagio fountain lake ≈ 36.1127 N, 115.1741 W (OSM), drawn as a ~250 × 80 m lake.
- **Smoothing (display only):** distance-over-time gaussian-smoothed (0.35 s), cars drawn on the shared centre line; delta smoothed 0.25 s. Sector/lap times shown are the official values.
