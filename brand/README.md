# Brand – The Pixel Paddock

Very clean, nerdy, diary-like, infographic-first. Dark mode, pixel fonts, neon-green accent.

## Logo / profile picture
- **Final:** `logo/profile_picture.png` (1080x1080, Instagram shows it as a circle). It is a solid pixel "P" inside a double 1-cell pixel ring, with a neon-green square full stop ("P.").
- Source: `src/logo6.py` (needs logo.py, logo4.py, logo5.py). `python3 logo6.py` writes the variants to `src/out_logo/`.
- The reels use the logo in the outro (`toolkit/reel_v3.py` loads it from here).

## Other account assets
- `highlights/` holds the story-highlight covers (1080x1920): NEWS, RACE WEEK, TECH, STATS, HISTORY.
- `start_here/` holds the pinned "Start here" carousel (3 slides).
- `ACCOUNT_SETUP.txt` has the username, bio, category and Buffer/GitHub setup (status at launch, October 2026).

## Palette
| Token | Hex | Use |
|---|---|---|
| paper | `#14120f` | background |
| speckle | `#1b1814` | 5x5 background speckles |
| box | `#1f1b16` | boxes / panels |
| ink | `#ece3cf` | readable text |
| mute | `#b8ad96` | secondary labels only |
| rule | `#3a352c` | rules / lines |
| accent | `#39ff14` | neon green, used sparingly: "F1 NEWS", FIG.n, box titles, REC dot, single highlighted rows. Text on green is set in paper. |
| signal red | `#e05050` / `#e8233f` | data signal only: red flag, DNF, penalty, positions lost |
| sectors | S1 `#a855f7` · S2 `#39ff14` · S3 `#facc15` · S4 `#38bdf8` · S5 `#f43f5e` | pagination |

## Fonts (in `toolkit/fonts/`, from fontsource, OFL)
- **Press Start 2P** for headlines (size 8, scaled x5)
- **Silkscreen** (regular and bold) for labels, wordmark, date, FIG, footer, HUD (caps only)
- **Jersey 10** for body text (size 18.6667, scaled x3)
- A hand-made 3x5 pixel font for text inside the 200x120 cover scenes (`FONT3` in the toolkit)
- Never use VT323 or Tiny5.

## Rules
- No F1, team or sponsor logos. No real helmet designs. Liveries only as plain colours.
- Car numbers are written "No. 12", never "#12".
- International audience: give local time plus UTC and several time zones, and don't highlight Berlin.
- Full post standard: the `pixel-paddock-post` skill.
