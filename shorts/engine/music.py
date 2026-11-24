"""Small chiptune generator for the Pixel Paddock shorts: 4 channels like an old console
(pulse lead, pulse arpeggio, triangle bass, noise drums), A minor, ~132 bpm.
sections: list of (start_seconds, kind) with kind in title, race, tension, finish, podium, outro."""
import numpy as np

SR = 44100
BPM = 132
STEP = 60 / BPM / 4                      # 16th note
NOTE = lambda m: 440 * 2 ** ((m - 69) / 12)

CHORDS = {"Am": (57, [0, 3, 7]), "F": (53, [0, 4, 7]), "C": (48, [0, 4, 7]), "G": (55, [0, 4, 7]),
          "Dm": (50, [0, 3, 7]), "E": (52, [0, 4, 7]), "D": (50, [0, 4, 7]), "A": (57, [0, 4, 7])}
PROG = {"title": ["Am", "F", "C", "G"], "race": ["Am", "F", "C", "G", "Am", "F", "G", "E"],
        "tension": ["Dm", "Am", "Dm", "E"], "finish": ["F", "G", "Am", "Am", "F", "G", "E", "E"],
        "podium": ["C", "G", "Am", "F", "C", "G", "F", "G"], "outro": ["Am", "F", "C", "G"]}
# 2-bar lead phrases as (step, semitone above chord root + 12, length in steps)
LEAD = [[(0, 12, 3), (4, 15, 2), (6, 19, 2), (8, 17, 3), (12, 15, 4)],
        [(0, 19, 2), (2, 17, 2), (4, 15, 2), (6, 12, 6), (12, 14, 2), (14, 15, 2)]]

def osc_pulse(f, n, duty):
    ph = (np.arange(n) * f / SR) % 1
    return np.where(ph < duty, 1.0, -1.0)
def osc_tri(f, n):
    ph = (np.arange(n) * f / SR) % 1
    return 2 * np.abs(2 * ph - 1) - 1
def env(n, a=.004, d=.08, s=.6, r=.03, length=None):
    t = np.arange(n) / SR; L = length or n / SR
    e = np.where(t < a, t / a, np.where(t < a + d, 1 - (1 - s) * (t - a) / d, s))
    return e * np.clip((L - t) / r, 0, 1)

def add(buf, sig, at):
    i = int(at * SR); j = min(len(buf), i + len(sig))
    if 0 <= i < len(buf): buf[i:j] += sig[:j - i]

def song(total_s, sections):
    buf = np.zeros(int(total_s * SR) + SR)
    rng = np.random.default_rng(7); noise = rng.uniform(-1, 1, SR)
    bar = STEP * 16; nbars = int(total_s / bar) + 1
    kind_at = lambda t: [k for s, k in sections if s <= t + 1e-6][-1] if sections else "race"
    count = {}
    for b in range(nbars):
        t0 = b * bar; kind = kind_at(t0); i = count.get(kind, 0); count[kind] = i + 1
        prog = PROG[kind]; root, iv = CHORDS[prog[i % len(prog)]]
        full = kind in ("race", "finish", "podium")
        # triangle bass: 8ths, root / octave bounce
        for st in range(0, 16, 2):
            m = root - 12 + (12 if st % 4 == 2 and full else 0)
            n = int(STEP * 2 * SR * .9); add(buf, osc_tri(NOTE(m), n) * env(n, d=.05, s=.8) * .22, t0 + st * STEP)
        # pulse arpeggio (12.5 % duty), quiet
        for st in range(16):
            m = root + 12 + iv[st % 3] + (12 if st % 6 == 5 else 0)
            n = int(STEP * SR * .85); add(buf, osc_pulse(NOTE(m), n, .125) * env(n, d=.04, s=.35) * (.05 if kind != "title" else .045), t0 + st * STEP)
        # lead melody (25 % duty) on race/finish/podium/outro, phrase alternates every bar
        if kind in ("race", "finish", "podium", "outro") and (kind != "race" or (i // 4) % 2 == 1):
            for st, semi, ln in LEAD[i % 2]:
                n = int(STEP * ln * SR * .92); f = NOTE(root + semi)
                vib = np.sin(np.arange(n) / SR * 2 * np.pi * 5.5) * .004
                ph = np.cumsum(f * (1 + vib) / SR) % 1; w = np.where(ph < .25, 1.0, -1.0)
                add(buf, w * env(n, d=.1, s=.7, r=.05) * .07, t0 + st * STEP)
        # drums
        if kind != "title":
            for st in range(16):
                at = t0 + st * STEP
                if st in (0, 8) or (full and st in (10,)):                      # kick: falling sine
                    n = int(.12 * SR); tt = np.arange(n) / SR; f = 120 * np.exp(-tt * 30) + 40
                    add(buf, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 25) * .28, at)
                if st in (4, 12) and kind != "tension":                         # snare: noise burst
                    n = int(.1 * SR); add(buf, noise[:n] * np.exp(-np.arange(n) / SR * 30) * .12, at)
                if st % 2 == 0 and full:                                        # closed hat
                    n = int(.025 * SR); h = np.diff(noise[:n + 1]); add(buf, h * np.exp(-np.arange(n) / SR * 120) * .035, at)
    # gentle low-pass, soft clip
    buf = np.convolve(buf, np.ones(4) / 4, mode="same")
    return np.tanh(buf * 1.4) * .7

if __name__ == "__main__":
    import wave, sys
    y = song(32, [(0, "title"), (4, "race"), (16, "tension"), (20, "finish"), (26, "podium")])
    with wave.open(sys.argv[1] if len(sys.argv) > 1 else "music_demo.wav", "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y * 32767).astype(np.int16).tobytes())
