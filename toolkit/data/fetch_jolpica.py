"""Fetch season data from Jolpica (Ergast successor, https://api.jolpi.ca/ergast/f1/).
Usage: python fetch_jolpica.py 2026 20   -> races.json, res_N.json, lap1_N.json in jolpica_2026/
Needs api.jolpi.ca on the session allowlist. Rate limit ~4 req/s, 500/h.
Also available: api.openf1.org (pit stops, lap times, live timing)."""
import sys, json, time, urllib.request, pathlib
year, last = sys.argv[1], int(sys.argv[2])
out = pathlib.Path(__file__).parent / f"jolpica_{year}"; out.mkdir(exist_ok=True)
B = "https://api.jolpi.ca/ergast/f1"
def get(path, name):
    (out / name).write_bytes(urllib.request.urlopen(f"{B}/{path}").read()); time.sleep(0.4)
get(f"{year}/races.json?limit=30", "races.json")
for r in range(1, last + 1):
    get(f"{year}/{r}/results.json?limit=40", f"res_{r}.json")
    get(f"{year}/{r}/laps/1.json?limit=40", f"lap1_{r}.json")
