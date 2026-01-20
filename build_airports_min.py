import csv
import json
import io
import requests

URL = "https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/airports.csv"

def safe_float(x):
    try:
        return float(x)
    except Exception:
        return None

r = requests.get(URL, timeout=60)
r.raise_for_status()

out = []
reader = csv.DictReader(io.StringIO(r.text))

for row in reader:
    ident = (row.get("ident") or "").strip().upper()
    if len(ident) < 3:
        continue

    lat = safe_float((row.get("latitude_deg") or "").strip())
    lon = safe_float((row.get("longitude_deg") or "").strip())
    if lat is None or lon is None:
        continue

    # OPTIONAL: reduce file size by excluding closed airports
    # comment these 2 lines out if you want literally everything
    if (row.get("type") or "").strip().lower() == "closed":
        continue

    out.append({
        "icao": ident,
        "iata": ((row.get("iata_code") or "").strip().upper() or None),
        "name": (row.get("name") or "").strip(),
        "city": (row.get("municipality") or "").strip(),
        "country": (row.get("iso_country") or "").strip().upper(),
        "lat": lat,
        "lon": lon,
    })

with open("airports.min.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, separators=(",", ":"))

print(f"Wrote {len(out)} airports to airports.min.json")
