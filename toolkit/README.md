# Toolkit – render code

Python 3 + Pillow + numpy, and ffmpeg for reels. Fonts are in `fonts/`. Track outlines in `geo/` come from [bacinger/f1-circuits](https://github.com/bacinger/f1-circuits) (see lic.txt): us = COTA, mx = Mexico City, br = Interlagos, jp = Suzuka.

## Carousels (1080x1350)
- `pp.py`: base layout with fonts, text(), page, framed, contact_sheet.
- `pp2.py`: layout A+ with page(), headline(), cover_image() (with GPS HUD), fig(), body(), box(), fact_file(), footer().
- `post_usgp.py` (hx, r, GREEN), `post_slater.py` / `post_cota.py` (3x5 `tx` + `FONT3`), `mock_v2.py` (track()).
- Example: `examples/post_fri.py` builds a complete 3x3 carousel (gap tower, slope chart, notes board, team-mate gaps, …). `cd examples && python3 post_fri.py` writes to `examples/out_fri/`.
- Example: `examples/post_mertitle.py` (title maths).

Note: some helper modules render their own demo posts when imported (into `out_*`). That is harmless, and those folders are git-ignored.

## Results reels (1080x1920, ~21.5 s)
```python
from reel_v4 import make
rows = [("VER","Red Bull","1:11.622"), ("ANT","Mercedes","+0.025"), ...]  # top 10
make("FP3", rows, "fp3br_reel", gp="SAO PAULO", rookies=("LIN",), insight=["LINE 1","LINE 2","LINE 3"])
```
- Output goes to `out_reel/`. Tracks are in `TRACKS` in reel_v4.py; add a new GP with its GeoJSON there.
- Example: `examples/reel_fp3br.py`.
- Publish to `reels/YYYY-MM-DD_session/reel.mp4` and post via Buffer as a reel (thumbnailOffset 2700).

## Lap-1 reel (season stats, ~29 s)
- `reel_lap1.py`: places gained on lap 1 over a season. Data from `data/jolpica_YYYY/` (fetch with `data/fetch_jolpica.py 2026 20`).
- Scenes: start-light gantry → diverging block chart (1 block = 1 place, pixel cars) → best/worst single start (position ladders) → takeaway → outro.
- `python3 reel_lap1.py` writes `out_reel/lap1_2026.mp4`.

## Other
- `pixcar.py`: side-view car sprites (1991 McLaren/Williams).
- The map-replay engine for the shorts lives in `../shorts/engine/`.
