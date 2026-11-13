# Historic race recap shorts (map replay)

YouTube Shorts (v2): top-down pixel cars on the real track layout, told chronologically. Time skips are full-screen LAP XX / YY cards; inside a scene the cars move at a believable speed. Lap counter and leader sit in a compact strip at the top. The bottom and right edge stay free for the YouTube overlay. Ends with an animated podium result (top 3 cars on the steps, P4-P6 list, one key note, confetti). Every on-screen fact is listed with sources in [SOURCES.md](SOURCES.md).

| Race | Video | Contact sheet |
|---|---|---|
| Brazil 1991, Interlagos (Senna, 71 laps, 75 s) | [1991_interlagos/recap.mp4](1991_interlagos/recap.mp4) | [sheet.png](1991_interlagos/sheet.png) |
| Japan 2005, Suzuka (Räikkönen, 53 laps, 70 s) | [2005_suzuka/recap.mp4](2005_suzuka/recap.mp4) | [sheet.png](2005_suzuka/sheet.png) |

Raw URLs (e.g. for Buffer):
- https://raw.githubusercontent.com/Kellsson/pixel-paddock-media/main/shorts/1991_interlagos/recap.mp4
- https://raw.githubusercontent.com/Kellsson/pixel-paddock-media/main/shorts/2005_suzuka/recap.mp4

## Status
v5 (13 Nov 2026): real-world sizing. Each race sets track_m (below the closest gap between two separate track sections, so parts never merge) and car_m (= track_m / 1.25). Zoom only changes how big it looks. Grid facts sit in a header panel with blinking highlights instead of a box over the grid. Safety car is a banner in the top bar. Spins only slide just off the edge.
v5.2: podium result instead of the green timing board.
v5.1: track drawn as one continuous band from a distance field (no notches or gaps at joints); outro holds 5 s.

## Engine
- `engine/map_recap.py`
  - Track class: GeoJSON resampled, rotation, at()/heading().
  - Camera: over / frac / car / pan.
  - Procedural top-down cars, TEAMS liveries (MCL91, WIL91, MCL05, REN05, FER05, TOY05, WIL05, GEN).
  - Top HUD strip, text panels, lap-skip cards, grid diagram, strategy card, results board, slope chart, 8-bit audio.
  - Safe zone constants SAFE_X0/X1/Y0/Y1: keep text and key action inside.
- `engine/races.py`: one config dict per race (geo, laps, rot, cars, results, segments). Segment kinds: racing scene (laps/cam/set/gaps/lat/spin/pit/call), jump, gridcard (head/call/fire), compare, strategy, note, board, outro. Callouts: call=[(frame, target, lines, side)], target = car code or ("slot", n). Copy R91/R05 as a template for new races.
- `engine/font3.py`: 3x5 pixel font.
- `engine/geo/`: track outlines from [bacinger/f1-circuits](https://github.com/bacinger/f1-circuits) (see lic.txt).

Render: `cd shorts/engine && python3 races.py 91|05|both` writes to `engine/out_short/`. Needs Pillow, numpy and ffmpeg.

## Rules
- Render prints CHECK lines (plausibility): car moving backwards, car off track, cars overlapping, car faster/slower than 0.7-1.3x the reference car, callout covering a car or label. Fix them or have a reason (contact, hairpin/crossover geometry).
- Gaps are real metres. Cars on the same line need at least car_m between them; side by side needs a lat difference of about 1.3 or more.
- Scenes written with old zoom values are converted by to_real_scale() in races.py. Use noscale=True for scenes whose set/gaps are already in real metres.
- Liveries use plain colours only, historically researched, no logos.
- Text always sits on dark panels.
- Cars must never cross the line backwards.
- Every race fact needs a source in SOURCES.md; lap numbers need two agreeing sources or the official result. If sources disagree, leave it out.
- No present-day tie-ins; just tell the race.
- One fact per beat, as a callout next to the action; max 2 lines of ~13 characters at scale 2.
- Time skips only via LAP cards, never by cars racing through many laps.
- Nothing important in the bottom ~30% or the right edge (YouTube overlay).
- Attractive, but no clickbait.
