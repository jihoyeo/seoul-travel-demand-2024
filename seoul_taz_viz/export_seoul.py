import sys
import json
from pathlib import Path

import geopandas as gpd

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
SHP = ROOT / "data" / "raw" / "ktdb_taz" / "2010-TM-GR-MR-CET 교통존(2009년 기준).ZIP" / "[01]교통분석 존" / "T1110G.shp"
OUT = ROOT / "data" / "derived" / "seoul_taz.geojson"

gdf = gpd.read_file(SHP, encoding="cp949")
seoul = gdf[(gdf["UPTAZ_ID"] == "1") & (gdf["TAZ_TYPE"] == "2")].copy()
seoul = seoul.to_crs(epsg=4326)

seoul["TAZ_ID"] = seoul["TAZ_ID"].astype(int)
seoul = seoul[["TAZ_ID", "TAZ_NAME", "geometry"]].sort_values("TAZ_ID").reset_index(drop=True)

seoul.to_file(OUT, driver="GeoJSON", encoding="utf-8")

bounds = seoul.total_bounds
center = [(bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2]
print(f"rows: {len(seoul)}")
print(f"bounds (minx, miny, maxx, maxy): {bounds.tolist()}")
print(f"center (lon, lat): {center}")
print(f"saved: {OUT}")
