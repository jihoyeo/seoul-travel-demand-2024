"""R1_oa2016_to_oa2025.ipynb — blocks/oa2016_to_oa2025.py 풀이."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nbgen import MD, CODE, write_notebook

cells = [
MD("""# R1 — 2016 SGIS OA → 2025 SGIS OA 면적가중 매핑

`blocks/oa2016_to_oa2025.py` 풀이.
입력: 2016 SGIS 집계구 SHP + 2025 SGIS 집계구 SHP
출력: `data/derived/oa2016_to_oa2025.parquet` (TOT_REG_CD × TOT_OA_CD × weight)

소요 ≈ 30초."""),

MD("""## 1. 두 SHP 로드

2016 = LOCAL_PEOPLE 의 권위 경계 (`TOT_REG_CD` 13자리).
2025 = SGIS census 의 권위 경계 (`TOT_OA_CD` 14자리).
2016 SHP 에는 `.prj` 가 없으므로 `EPSG:5179` 명시 부여."""),

CODE("""import os
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely import make_valid

ROOT = r'F:\\research\\TAZ'
DATA = os.path.join(ROOT, 'data')
OUT  = os.path.join(DATA, 'derived', 'oa2016_to_oa2025.parquet')

oa16_path = os.path.join(DATA, 'raw', 'sgis_oa_2016', '집계구.shp')
oa25_path = os.path.join(DATA, 'raw', 'sgis_oa', 'bnd_oa_11_2025_2Q.shp')

oa16 = gpd.read_file(oa16_path, encoding='cp949')
oa16 = oa16.set_crs(5179, allow_override=True)   # .prj 없음 → 명시
oa16 = oa16[['TOT_REG_CD', 'geometry']].copy()
oa16['TOT_REG_CD'] = oa16['TOT_REG_CD'].astype(str)
oa16['geometry']  = oa16.geometry.apply(make_valid)
oa16['oa16_area_m2'] = oa16.geometry.area.astype('float32')
print(f'2016 OA : {len(oa16):,}')

oa25 = gpd.read_file(oa25_path)
oa25 = oa25.set_crs(5179, allow_override=True)
oa25 = oa25[['TOT_OA_CD', 'geometry']].copy()
oa25['TOT_OA_CD'] = oa25['TOT_OA_CD'].astype(str)
oa25['geometry']  = oa25.geometry.apply(make_valid)
print(f'2025 OA : {len(oa25):,}')"""),

MD("""## 2. 공간 교차 (overlay intersection)

각 2016 OA × 2025 OA 가 겹치는 부분을 폴리곤으로 산출."""),

CODE("""inter = gpd.overlay(oa16[['TOT_REG_CD','oa16_area_m2','geometry']],
                    oa25[['TOT_OA_CD','geometry']],
                    how='intersection', keep_geom_type=True)
inter['inter_area_m2'] = inter.geometry.area.astype('float32')
print(f'교차 폴리곤 : {len(inter):,}')

# sliver 제거 (50 m² 미만)
inter = inter[inter['inter_area_m2'] >= 50].reset_index(drop=True)
print(f'sliver 제거 후 : {len(inter):,}')"""),

MD("""## 3. weight 계산 — `inter_area / oa16_area`

weight 합 = 1 per 2016 OA 가 되도록."""),

CODE("""inter['weight'] = (inter['inter_area_m2'] / inter['oa16_area_m2']).astype('float32')

# weight 합 = 1 검증
ws = inter.groupby('TOT_REG_CD')['weight'].sum()
print(f'weight 합 분포: median {ws.median():.4f}, p10 {ws.quantile(0.1):.4f}, p90 {ws.quantile(0.9):.4f}')
print(f'(약간 < 1 일 수 있음 — sliver 제거 영향)')

# 정규화
ws_full = inter.groupby('TOT_REG_CD')['weight'].transform('sum')
inter['weight'] = inter['weight'] / ws_full
print(f'정규화 후 합  : {inter.groupby("TOT_REG_CD")["weight"].sum().describe().round(4)}')"""),

MD("""## 4. 분포 분석 — split 패턴"""),

CODE("""out = inter[['TOT_REG_CD','TOT_OA_CD','weight','inter_area_m2','oa16_area_m2']].copy()

split_count = out.groupby('TOT_REG_CD').size()
dom_share   = out.groupby('TOT_REG_CD')['weight'].max()

print('2016 OA 매칭 분포:')
print(f'  1:1 매칭             : {(split_count == 1).sum():,}')
print(f'  분할되나 90%+ dom    : {((split_count > 1) & (dom_share >= 0.9)).sum():,}')
print(f'  진짜 split (<90% dom) : {((split_count > 1) & (dom_share < 0.9)).sum():,}')"""),

MD("""## 5. 저장"""),

CODE("""out.to_parquet(OUT, index=False)
print(f'saved : {OUT}  ({os.path.getsize(OUT)/1e6:.2f} MB, {len(out):,} rows)')
print('OK')"""),
]

if __name__ == '__main__':
    out = os.path.join(os.path.dirname(__file__), '..', 'reproduce', 'R1_oa2016_to_oa2025.ipynb')
    write_notebook(cells, out)
