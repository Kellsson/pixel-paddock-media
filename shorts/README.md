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

## Race replays (real data)
Recent races replayed from OpenF1 position data: all cars on the real racing line, fast-forward with a top-5 tower, slow-down and zoom for highlights, then the podium.
| Race | Video |
|---|---|
| Mexico City 2026 (Verstappen, Antonelli champion, 88 s) | [replays/2026_mexico/replay.mp4](replays/2026_mexico/replay.mp4) |

Brand look (replays): the Pixel Paddock palette (paper, speckles, ink, neon green, signal red) and the brand fonts drawn at full resolution (Press Start 2P for big text, Silkscreen for small labels; `apply_brand()` + `finish_frame()`). The title and outro cards follow the brand guide. Fact boxes stay at least 2.4 s on screen.

Engine: `engine/replay.py`, race config `engine/replay_mexico26.py`, sources [SOURCES_REPLAY.md](SOURCES_REPLAY.md).
New race: `replay_fetch.py` -> `replay_prep.py` -> copy a config, find highlight times in the data, render. The raw data is not in the repo (OpenF1 CC BY-NC-SA, non-commercial).

## Quali duels (real data)
The two fastest laps overlaid on one line (leader on top, the other as a ghost), pinned to the official sector times, with a live gap, speeds, a mini map, real landmarks, a freeze at the finish line and a sector table at the end.
| Session | Video |
|---|---|
| Las Vegas 2026 quali: Antonelli vs Verstappen (56 s, scheduled 26 Nov) | [duels/2026_lasvegas/duel.mp4](duels/2026_lasvegas/duel.mp4) |

Engine: `engine/duel.py`, config `engine/duel_lasvegas26.py`, sources [SOURCES_DUEL.md](SOURCES_DUEL.md).

## Style rules from feedback (all short formats)
Brand and layout
- Everything on-brand and recognisable across Instagram and YouTube: Pixel Paddock palette, speckled paper background, Press Start 2P / Silkscreen at full resolution.
- Title cards: format name big ("F1 RACE REPLAY", "F1 QUALI DUEL"), place + year (no full date), no Pixel Paddock logo (YouTube shows the channel logo). Always say "F1".
- Text in boxes vertically centred, on dark panels; fact boxes at least 2.4 s on screen and ended when the fact stops being true (e.g. SC in).
- Nothing important in the bottom ~30 % or the right edge (YouTube overlay). Text never covers the action.

Story
- One fact per beat, callout next to the action, max 2 lines. Easy to follow, nerdy, exciting, no clickbait.
- Every on-screen claim sourced (SOURCES*.md) or proven in the data and explained on screen (e.g. "LINDBLAD AHEAD = ANT'S TOW").
- Always check plausibility: no cars backwards, off track, facing the wrong way at standstill, flying across the track.

Race replays
- Zoom out slowly and only after enough time; slow down + zoom for highlights.
- Crashes shown where they happened, with damage animation; wreck removed when it really was.
- Lap counter big and prominent (News-Flash style), no driver name beside it. Chiptune music, mixed loud enough.

Quali duels
- Overlay, never side by side (looks like a race). Leader on top, trailing car as a ghost.
- Line across the track at each car's nose in its team colour + gap line between them; gap in s and metres in the HUD.
- Smooth everything (positions, gap readout, speeds, labels); "LEVEL" below 0.05 s.
- Mini track map stays. Real landmarks at real positions/scale (aligned GeoJSON).
- Title: both cars in team colours with surnames, "VS" between them, no extra name box.
- Freeze both cars when the first crosses the line, zoom in, show the gap to the loser.
