"""01_spatial_data.ipynb — 강좌 개요 + 서울 공간 데이터 다루기 (학부 3학년)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nbgen import MD, CODE, write_both

cells = [
MD("""# Lecture 1 — 강좌 개요 + 서울 공간 데이터 다루기

> 서울의 공간 단위 (필지·OA·admdong·자치구) 와 좌표계 3종을 익혀
> 이후 모든 모듈의 raw 데이터를 읽을 수 있게 한다.

**왜** : 통행수요 분석은 "어떤 공간 단위에서 하는가" 로 시작·끝남.
단위·코드 체계·좌표계를 모르면 raw 데이터 한 줄도 못 읽음.

**4단계 모형 위치** : 강좌 도입 — 1·2단계 (Generation·Distribution)
의 분석 단위를 결정짓는 단계

**사전지식** : 없음 (강좌 시작)

**이번 시간 산출** : 개념 정리만 (파일 산출 X)

```
강좌 전체 흐름
─────────────────────────────────────────────────────────────
Lec1 ──→ Lec2 ──→ Lec3 ──→ Lec4         메인 (통행 수요)
공간     OA       P/A      OD
데이터   마스터    발생     추정·검증

             └─→ Lec5 (부록 트랙, 도시 형태)
                 superblock + 토지이용
```

다룰 항목:
- 서울 공간 데이터 위계 이해 (시군구 → 행정동 → 집계구 → 필지)
- 좌표계 3종 (EPSG:5179 / 5186 / 4326) 사용 흐름
- `geopandas` 로 폴리곤 로딩 + 시각화 기본기"""),

MD("""## 1. 4단계 통행수요모형 — 무엇을 만드나

```
4단계 통행수요모형
────────────────────────────────────────
1. Trip Generation (발생·유인량)   ←── 본 강좌 Lecture 3
   P_i = 지역 i 에서 출발하는 통행 수
   A_j = 지역 j 로 도착하는 통행 수

2. Trip Distribution (분포)        ←── 본 강좌 Lecture 4
   T_ij = 지역 i → j 통행 행렬

3. Mode Choice (수단 분담)         ── 강좌 외
4. Network Assignment (배정)       ── 강좌 외
```

- 본 강좌 = 1·2 단계
- 이론은 교재 참조. 강좌는 **실데이터 적용의 어려움** 에 집중
  - 공간 단위 통합
  - 코드 체계 변환
  - proxy vs 관측 비교
  - 정량 검증"""),

MD("""## 2. 두 트랙 구조

같은 raw 데이터 → 두 갈래 분석.

```
공통 (Lec1, Lec2)           분기 (Lec3·Lec4 메인 / Lec5 부록)
───────────────────         ──────────────────────────
공간 데이터 ──┐
SGIS 통계  ──┼─→ oa_master ─┬─→ Lec3: P/A admdong
LOCAL_PEOPLE ┘  (OA 마스터)  │     Lec4: OD admdong
                             │     (통행 수요 메인)
                             │
                             └─→ Lec5: superblock + LU
                                 (도시 형태 부록)
```

| 트랙 | 분석 단위 | 왜 | 산출 |
|---|---|---|---|
| **통행 수요 메인 (Lecture 3·4)** | admdong 426 | 관측 OD 단위 | `pi_aj_v1`, `od_matrix_v1` |
| **도시 형태 부록 (Lecture 5)** | superblock 907 | 도로 자연 경계 | `block_master.parquet` |

- 분석 단위는 **데이터의 입도** 가 결정
- 도로 데이터 = superblock, 관측 OD = admdong"""),

MD("""## 3. 서울 공간 단위 위계

```
서울 공간 단위 (작은 → 큰)
─────────────────────────────────────────────────
필지 parcel        89.9만개   필지·용도지역
   ↑ centroid                 (LSMD)
집계구 OA          19,097개   통계 원자
   ↑ groupby ADM_CD[:8]       (SGIS)
행정동 admdong     426개      통행 수요 단위
   ↑ groupby [:5]             (Lec3·Lec4)
시군구 sgg         25개       정책 단위
   ↑                          (자치구 = KTDB TAZ)
시도 sido          1개        서울특별시
```

- 상위 단위 = 하위 단위의 묶음 (코드 체계로 위계 표현)
- 본 강좌 사용 단위 : OA (통계) + admdong (통행) + superblock (도로)
- ⚠️ admdong 코드 체계 두 종류 (행안부 vs SGIS) — Lecture 3 에서 다룸"""),

MD("""## 0. 환경 설정 + Imports"""),

CODE("""import os, sys, warnings
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore')
%matplotlib inline
plt.rcParams['figure.figsize'] = (10, 7)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

ROOT = r'F:\\research\\TAZ'
RAW  = os.path.join(ROOT, 'data', 'raw')
DRV  = os.path.join(ROOT, 'data', 'derived')
print('OK')"""),

MD("""## 4. 좌표계 (CRS) 3종

```
좌표계 흐름
─────────────────────────────────────────────────────────────
원본 raw                   분석 (5179)            시각화 (4326)
──────────────────         ──────────────         ─────────────
sgis_oa  EPSG:5179 ──┐
roads    EPSG:5179 ──┼──→ EPSG:5179 ──────→ EPSG:4326
lsmd     EPSG:5186 ──┘    (KGD2002 단일평면)    (WGS84 위경도)
                          m 단위                  deck.gl·leaflet
                          면적·거리 정확
```

| EPSG | 이름 | 단위 | 용도 |
|---:|---|---|---|
| **5179** | KGD2002 / Unified | m | **분석 표준** |
| 5186 | KGD2002 / Central Belt | m | LSMD 필지 (변환 후 분석) |
| 4326 | WGS84 | degree | 웹 시각화 |

- EPSG:5179 = 분석 기본. m 단위라 면적·거리 계산 그대로
- WGS84 (4326) 로 면적 계산 금지 — degree 단위는 면적 의미 없음
- `to_crs(5179)` 한 줄로 변환"""),

MD("""## 5. 자치구 폴리곤 — 가장 단순한 사례"""),

CODE("""# 행정동 경계 geojson 에서 시작
boundary = gpd.read_file(os.path.join(RAW, 'admdong_boundary', 'admdong_2023.geojson'))
seoul_admdong = boundary[boundary['sidonm'].str.contains('서울', na=False)].copy()

print(f'서울 행정동 : {len(seoul_admdong)}')
print(f'CRS         : {seoul_admdong.crs}')
print(f'컬럼        : {list(seoul_admdong.columns)}')"""),

CODE("""# 좌표계 5179 변환 + 면적 계산
seoul_admdong = seoul_admdong.to_crs(5179)
seoul_admdong['area_km2'] = seoul_admdong.geometry.area / 1e6

print(f'서울 총 면적: {seoul_admdong["area_km2"].sum():.1f} km²')
print(f'행정동 면적 통계 (km²):')
print(seoul_admdong['area_km2'].describe().round(2))"""),

CODE("""# 자치구로 dissolve (sggnm 기준)
sgg = seoul_admdong.dissolve(by='sggnm', as_index=False, aggfunc={'area_km2': 'sum'})
print(f'서울 자치구 : {len(sgg)}')

fig, ax = plt.subplots(figsize=(11, 9))
sgg.plot(column='area_km2', ax=ax, cmap='YlOrRd',
         edgecolor='white', linewidth=1.5, legend=True,
         legend_kwds={'label': '면적 (km²)', 'shrink': 0.6})

for _, row in sgg.iterrows():
    pt = row.geometry.representative_point()
    ax.annotate(row['sggnm'], (pt.x, pt.y), fontsize=8, ha='center')

ax.set_title('서울 25개 자치구 — 면적 분포')
ax.set_axis_off()
plt.show()"""),

MD("""## 6. 집계구 (OA) — 통계의 원자

- 통계청 SGIS 가 발급하는 가장 작은 인구 통계 단위
- 서울 = 19,097개
- 모든 인구·가구·주택 통계가 OA 단위로 공개

```
SGIS OA 코드 (14자리)
─────────────────────────────
시도  시군구  동   일련번호
11    010    530  010001
─┬─   ─┬─    ─┬─  ─┬──
2자리 3자리  3자리 6자리
└── ADM_CD (8) ─┘
```"""),

CODE("""# OA 폴리곤 로딩 (19,097 폴리곤, ~5-10초)
import time
t0 = time.time()
oa = gpd.read_file(os.path.join(RAW, 'sgis_oa', 'bnd_oa_11_2025_2Q.shp'),
                   encoding='cp949')
print(f'로딩 시간 : {time.time() - t0:.1f}s')
print(f'OA 수     : {len(oa)}')
print(f'컬럼      : {list(oa.columns)}')
oa.head(3)"""),

CODE("""# OA 면적 분포 (인구 단위라 매우 다양)
oa['area_m2'] = oa.geometry.area
print(f'면적 (m²)')
print(f'  median : {oa["area_m2"].median():>10,.0f}')
print(f'  p10    : {oa["area_m2"].quantile(0.1):>10,.0f}')
print(f'  p90    : {oa["area_m2"].quantile(0.9):>10,.0f}')
print(f'  max    : {oa["area_m2"].max():>10,.0f}')

fig, ax = plt.subplots(figsize=(10, 4))
ax.hist(np.log10(oa['area_m2']), bins=60, color='steelblue', edgecolor='white')
ax.set_xlabel('log10(area m²)'); ax.set_ylabel('OA 개수')
ax.set_title('서울 OA 면적 분포 — 도심 작고 외곽 큼')
ax.grid(alpha=0.3, axis='y'); plt.show()"""),

CODE("""# 한 자치구 (예: 종로구) OA 시각화
jongno_oa = oa[oa['ADM_CD'].astype(str).str[:5] == '11010']
print(f'종로구 OA : {len(jongno_oa)}')

fig, ax = plt.subplots(figsize=(12, 10))
jongno_oa.plot(ax=ax, color='lightblue', edgecolor='steelblue', linewidth=0.4)
ax.set_title(f'종로구 OA — {len(jongno_oa)}개')
ax.set_axis_off(); plt.show()"""),

MD("""## 7. 필지 — LSMD zone_class

- 국토부 LSMD 용도지역지구도 = 서울 89.9만 필지 폴리곤 (원본 1.5 GB, EPSG:5186)
- `derived/seoul_parcels.fgb` (322 MB, 4326) 가 강좌용 사본. 11개 `zone_class` 라벨 부여 완료
- 서울 전체를 한 번에 그리면 너무 빽빽해 화면이 검어지고, 1,000개 미리보기 (`seoul_parcels_sample.geojson`) 는 반대로 너무 듬성. **bbox 스트리밍** 으로 한 자치구만 풀 필지 로딩하는 게 합리적
- FlatGeobuf 는 spatial index 가 파일에 내장돼 있어 `bbox=` 옵션을 주면 해당 영역 필지만 디스크에서 읽어옴 (전체 322 MB 안 읽음)"""),

CODE("""# 종로구 bbox 로 필지 스트리밍 로딩 (FGB spatial index 활용)
# parcels.fgb 는 EPSG:4326 이므로 bbox 도 4326 좌표로 줘야 함
jongno_bbox_4326 = tuple(jongno_oa.to_crs(4326).total_bounds)

t0 = time.time()
parcels = gpd.read_file(os.path.join(DRV, 'seoul_parcels.fgb'),
                        bbox=jongno_bbox_4326)
print(f'로딩 시간       : {time.time() - t0:.1f}s')
print(f'bbox 내 필지   : {len(parcels):,}')
print(f'컬럼            : {list(parcels.columns)}')

# 분석 표준 5179 로 변환 후, bbox 가 사각형이라 인접 자치구가 살짝 섞임 → 종로구 경계로 클립
parcels = parcels.to_crs(5179)
jongno_union = jongno_oa.geometry.union_all()
parcels = parcels[parcels.geometry.within(jongno_union)].copy()
print(f'종로구 안 필지 : {len(parcels):,}')
parcels.head(3)"""),

CODE("""# zone_class 분포 (종로구)
print('종로구 zone_class top 10:')
print(parcels['zone_class'].value_counts().head(10))"""),

CODE("""# zone_class choropleth — 11클래스 색칠
# blocks/aggregate_landuse.py LU_COLOR 와 동일 톤 (RGB 0-255 → matplotlib 0-1)
from matplotlib.patches import Patch

ZONE_COLOR = {
    '전용주거':              (1.00, 0.90, 0.60),
    '일반주거_저밀(1종)':     (1.00, 0.78, 0.47),
    '일반주거_중밀(2종)':     (1.00, 0.65, 0.31),
    '일반주거_고밀(3종)':     (0.88, 0.47, 0.20),
    '준주거':                (0.78, 0.35, 0.39),
    '중심·일반상업':          (0.86, 0.24, 0.24),
    '근린·유통상업':          (0.94, 0.43, 0.55),
    '일반·준공업':            (0.59, 0.43, 0.86),
    '보전·자연녹지':          (0.43, 0.71, 0.43),
    '생산녹지':              (0.63, 0.82, 0.39),
}

fig, ax = plt.subplots(figsize=(12, 11))
handles = []   # PatchCollection 은 legend 자동 매칭 안 됨 → Patch 핸들 수동 생성
for cls, color in ZONE_COLOR.items():
    sub = parcels[parcels['zone_class'] == cls]
    if not len(sub): continue
    sub.plot(ax=ax, color=color, edgecolor='white', linewidth=0.05)
    handles.append(Patch(facecolor=color, edgecolor='white',
                         label=f'{cls} ({len(sub):,})'))

# 종로구 외곽선
jongno_oa.dissolve().boundary.plot(ax=ax, color='black', linewidth=0.6)

ax.legend(handles=handles, loc='lower right', fontsize=8, framealpha=0.9)
ax.set_title(f'종로구 — LSMD 필지 {len(parcels):,}개 × zone_class')
ax.set_axis_off(); plt.show()"""),

MD("""## 8. 정리

- 4단계 통행수요모형 = **1·2단계** (Generation + Distribution) 가 강좌 범위
- 두 트랙 — 통행 수요 메인 (Lecture 3·4, admdong) + 도시 형태 부록 (Lecture 5, superblock)
- 공간 위계 — 필지(89만) ↑ OA(1.9만) ↑ admdong(426) ↑ 시군구(25)
- 좌표계 — EPSG:5179 분석 표준 (m), 4326 시각화 전용
- `geopandas` 기본 : `read_file`, `to_crs`, `geometry.area`, `dissolve`, `plot`

→ **다음 Lecture 2** — OA 마스터 구축 (SGIS 통계 + LOCAL_PEOPLE 시간대 생활인구 통합)."""),

CODE("""print('OK')
print(f'서울 자치구  : {len(sgg)}')
print(f'서울 행정동  : {len(seoul_admdong)}')
print(f'서울 OA      : {len(oa)}')"""),
]

if __name__ == '__main__':
    HERE = os.path.dirname(__file__)
    write_both(cells,
               os.path.join(HERE, '..', 'notebooks', '01_spatial_data.ipynb'),
               os.path.join(HERE, '..', 'slides', '01_spatial_data.md'))
