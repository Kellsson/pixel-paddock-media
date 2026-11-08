# Historic race recap shorts (map replay)

Prototypes for YouTube Shorts: accurate top-down pixel cars race (exaggeratedly fast) around the real track layout, the camera zooms into key events, a lap counter runs the whole time, and the podium is shown as a CRT timing board.

| Race | Video | Contact sheet |
|---|---|---|
| Brazil 1991, Interlagos (Senna, 71 laps) | [1991_interlagos/recap.mp4](1991_interlagos/recap.mp4) | [sheet.png](1991_interlagos/sheet.png) |
| Japan 2005, Suzuka (Räikkönen, 53 laps) | [2005_suzuka/recap.mp4](2005_suzuka/recap.mp4) | [sheet.png](2005_suzuka/sheet.png) |

Raw URLs (e.g. for Buffer):
- https://raw.githubusercontent.com/Kellsson/pixel-paddock-media/main/shorts/1991_interlagos/recap.mp4
- https://raw.githubusercontent.com/Kellsson/pixel-paddock-media/main/shorts/2005_suzuka/recap.mp4

## Status
Prototypes, still waiting for Marius's feedback. Planned next: bigger, sharper cars when zoomed in, plus a mini-map inset.
Some event lap numbers rest on a single source or an estimate. Examples: several of the 1991 events, and Alonso's pass at 130R on lap 20 in 2005. Re-verify them before publishing.

## Engine
- `engine/map_recap.py`
  - Track class: GeoJSON resampled, rotation, at()/heading().
  - Camera: over / frac / car / pan.
  - Procedural top-down cars, TEAMS liveries (MCL91, WIL91, MCL05, REN05, FER05, TOY05, WIL05, GEN).
  - HUD, text panels, results board, 8-bit audio.
- `engine/races.py`: one config dict per race (geo, laps, rot, cars, segments with frames/laps/cam/gaps/labels/text/rain/sc/board/outro). Copy R91/R05 as a template for new races.
- `engine/font3.py`: 3x5 pixel font.
- `engine/geo/`: track outlines from [bacinger/f1-circuits](https://github.com/bacinger/f1-circuits) (see lic.txt).

Render: `cd shorts/engine && python3 races.py 91|05|both` writes to `engine/out_short/`. Needs Pillow, numpy and ffmpeg.

## Rules
- Liveries use plain colours only, historically researched, no logos.
- Text always sits on dark panels.
- Cars must never cross the line backwards.
- Every race fact needs a source.
- Attractive, but no clickbait.
