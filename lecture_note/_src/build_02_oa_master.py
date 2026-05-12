"""02_oa_master.ipynb — OA 마스터 구축 (SGIS + LP 통합) (학부 3학년)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nbgen import MD, CODE, write_both

cells = [
MD("""# Lecture 2 — OA 마스터 구축

> 흩어진 SGIS 통계·LOCAL_PEOPLE 을 한 파일로 묶어
> 이후 모든 OA 분석의 출발점을 만든다.

**왜** : 모델링 변수가 여러 raw 파일에 흩어져 있어 매번 join 하면
비효율. 한 번 통합해두면 이후 Lecture 3 회귀, Lecture 5 superblock
모두 이 파일 한 줄로.

**4단계 모형 위치** : 1단계 (Trip Generation) 의 입력 변수 정비

**사전지식** : pandas pivot, GeoPandas 공간 join (Lecture 1)

**이번 시간 산출** : `oa_master.parquet` (19,097 OA × 150 컬럼)

```
raw 데이터                                derived 마스터
──────────────────────────────────       ─────────────────────
sgis_oa/         2025 OA 폴리곤  ──┐
sgis_oa_2016/    2016 OA 폴리곤  ──┤
sgis_census/     10 CSV (인구·가구·주택) ──┐
seoul_living_pop/ LOCAL_PEOPLE zip      ──┴─→ oa_master.parquet
                                              19,097 OA × 150 col
                                              (인구 + LP 시간풀 + 성연령)
```

다룰 항목:
- SGIS 10 CSV 의 long → wide 변환
- LOCAL_PEOPLE (KT 휴대전화 시그널링) 시간대 생활인구
- 2016 vs 2025 OA 코드 체계 차이 + 면적가중 매핑
- `oa_master.parquet` 한 줄로 모든 OA 변수 사용"""),

MD("""## 0. Imports & paths"""),

CODE("""import os, sys, zipfile, warnings
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore')
%matplotlib inline
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

ROOT = r'F:\\research\\TAZ'
RAW  = os.path.join(ROOT, 'data', 'raw')
DRV  = os.path.join(ROOT, 'data', 'derived')
print('OK')"""),

MD("""## 1. SGIS 인구·가구·주택 통계

```
SGIS 데이터 구조
────────────────────────────────────────────────────
파일                            행 형식
──────────────────              ─────────────────────────────
11_2024년_인구총괄(총인구).csv   long: OA × 항목
11_2024년_성연령별인구.csv       long: OA × 81 성연령
11_2024년_가구총괄.csv           long: OA × 항목
11_2024년_세대구성별가구.csv     long: OA × 세대구성
... (총 10개 CSV)
```

- 한 OA 가 여러 행으로 나뉘어 저장됨 (long format)
- 분석엔 wide 가 편함 → `pivot` 으로 변환"""),

CODE("""# SGIS 인구총괄 (총인구) — 헤더 없는 CSV
# 컬럼: 연도, OA 코드, 항목 코드, 값
pop = pd.read_csv(os.path.join(RAW, 'sgis_census', '11_2024년_인구총괄(총인구).csv'),
                  encoding='cp949', header=None,
                  names=['year', 'oa_cd', 'item_cd', 'value'])
print(f'shape : {pop.shape}')
print(f'컬럼  : {list(pop.columns)}')
print(pop.head(5))"""),

CODE("""# 항목 코드 종류
print('항목 코드 (한 OA 가 여러 행 = long format):')
print(pop['item_cd'].value_counts())
print()
print(f'NaN/N/A value 비율 : {pop["value"].isna().sum() + (pop["value"].astype(str) == "N/A").sum()} / {len(pop)}')
print('(N/A 는 통계 보호 — 인구 작아 노출 위험)')"""),

CODE("""# long → wide pivot
# 'N/A' 는 NaN 으로 (0 으로 채우면 안 됨 — 데이터 없음 ≠ 0 명)
pop['value'] = pd.to_numeric(pop['value'], errors='coerce')

wide = pop.pivot_table(index='oa_cd', columns='item_cd', values='value', aggfunc='first')
print(f'wide shape : {wide.shape}')
print(f'  rows = OA 수, cols = 항목')
print(wide.head(3))
print('\\n각 항목 NaN 개수:')
print(wide.isna().sum())"""),

MD("""## 2. LOCAL_PEOPLE — 시간대별 생활인구

```
LOCAL_PEOPLE 데이터
────────────────────────────────────────────────
출처   : 서울 열린데이터 광장 (data.seoul.go.kr)
방법   : KT 휴대전화 시그널링 → OA 단위 시간대별 추정 인구
형식   : zip 안에 일별 CSV 31개 (2024-12 한달)
크기   : zip 3.7 GB, CSV 한 개당 126 MB

한 행 (wide):
─────────────────────────────────────────────────
기준일ID  시간대구분  집계구코드(13)  행정동코드(8)
총생활인구수  남자0-9세인구  ...  여자70+세인구
   (28 컬럼 — 성연령 14 × 2 + 메타)
```

- 시간대 = 24개 (00시 ~ 23시)
- 31일 × 24 시간 × 19,000 OA ≈ **14M 행/월**
- 컬럼은 wide (성연령 28종 별 인구 컬럼)"""),

CODE("""# LP zip 한 파일만 스트리밍 로드
lp_zip = os.path.join(RAW, 'seoul_living_pop', 'LOCAL_PEOPLE_202412.zip')

with zipfile.ZipFile(lp_zip) as z:
    names = sorted(n for n in z.namelist() if n.endswith('.csv'))
    print(f'zip 내 파일 : {len(names)}개 (일별)')
    print(f'  처음 3개  : {names[:3]}')

    # 하나만 읽기 (12월 1일)
    with z.open(names[0]) as f:
        lp = pd.read_csv(f, encoding='cp949')
print(f'\\n한 파일 (1일치) shape : {lp.shape}')
print(f'  = 24시간 × 19,152 OA = {24*19152}')
print(f'컬럼 (앞 5개) : {list(lp.columns[:5])}')
print(lp.head(3))"""),

CODE("""# 시간대별 패턴 보기 — 한 OA 의 24시간 총생활인구 추이
# 종로구의 어떤 OA 하나 골라보기
sample_cd = lp['집계구코드'].iloc[0]
one_oa = lp[lp['집계구코드'] == sample_cd].sort_values('시간대구분')

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(one_oa['시간대구분'], one_oa['총생활인구수'], marker='o', color='steelblue')
ax.set_xlabel('시간대 (0-23h)')
ax.set_ylabel('생활인구 (명)')
ax.set_title(f'OA {sample_cd} — 12월 1일 시간대별 생활인구')
ax.grid(alpha=0.3); plt.show()

print(f'새벽 (3시) : {one_oa[one_oa["시간대구분"]==3]["총생활인구수"].iloc[0]:.0f}')
print(f'정오 (12시): {one_oa[one_oa["시간대구분"]==12]["총생활인구수"].iloc[0]:.0f}')
print(f'야간 (20시): {one_oa[one_oa["시간대구분"]==20]["총생활인구수"].iloc[0]:.0f}')"""),

MD("""## 3. ⚠️ 두 OA 코드 체계 — 2016 vs 2025

```
OA 코드 체계 문제
──────────────────────────────────────────────────────
LOCAL_PEOPLE 의 집계구코드(13) = 2016 SGIS TOT_REG_CD(13)
                                ↓ (공간 교차)
SGIS 2025 통계의 TOT_OA_CD(14)
                                ↓ (분석 단위)

같은 OA 라도 13자리 ≠ 14자리 — 코드 체계 자체가 바뀜
2016~2025 사이에 OA 50개 정도가 재구획됨
```

해결:
- `derived/oa2016_to_oa2025.parquet` = 면적가중 매핑 (`weight` 합 = 1 per 2016 OA)
- LP (2016 단위) × weight → 2025 단위로 disaggregate"""),

CODE("""# 2016 → 2025 매핑표 살펴보기
mapping = pd.read_parquet(os.path.join(DRV, 'oa2016_to_oa2025.parquet'))
print(f'매핑 행 수 : {len(mapping):,}')
print(f'컬럼       : {list(mapping.columns)}')
print(mapping.head(8))

# 한 2016 OA 가 여러 2025 OA 로 쪼개진 사례
multi = mapping.groupby('TOT_REG_CD').size().sort_values(ascending=False)
print(f'\\n2016 OA 1개 → 2025 OA 1개 매칭 : {(multi == 1).sum()} ({(multi == 1).mean()*100:.1f}%)')
print(f'2016 OA 1개 → 2025 OA 여러개 (재구획): {(multi > 1).sum()}')
print(f'최대 분할 : {multi.max()} 개')"""),

MD("""## 4. 통합 산출 — oa_master.parquet

위의 모든 데이터를 합친 결과. 직접 만들 땐 8분 정도 걸리므로 **이미 만들어진 것을 로드**.

```
oa_master.parquet 구성
─────────────────────────────────────────────────
19,097 OA × 150 cols
  ├ 키        : TOT_OA_CD, ADM_CD, block_id
  ├ 기하      : geometry, area_m2
  ├ 인구·가구·주택 : pop_total, hh_count, ho_total, ...
  ├ 성연령 (81) : in_age_M00_04, ..., in_age_F75p
  └ LP 시간풀 (6) : lp_pool_resident_02_05,
                   lp_pool_morning_07_10,
                   lp_pool_midday_11_15,
                   lp_pool_evening_18_21,
                   lp_pool_late_22_01,
                   lp_pool_24h
```"""),

CODE("""oa_master = gpd.read_parquet(os.path.join(DRV, 'oa_master.parquet'))
print(f'oa_master shape : {oa_master.shape}  (19,097 OA × 150 cols)')
print()
print('주요 컬럼 그룹:')
for prefix, label in [
    ('pop_', '인구 통계'), ('hh_', '가구'), ('ho_', '주택'),
    ('in_age_', '성연령 81종'), ('lp_pool_', 'LP 시간 풀'),
    ('lp_demo_', 'LP 성연령 28종'),
]:
    cols = [c for c in oa_master.columns if c.startswith(prefix)]
    print(f'  {label:<12} ({prefix}*) : {len(cols)}개')

print(f'\\n결측 (pop_total 기준) : {oa_master["pop_total"].isna().sum()} OA')"""),

CODE("""# 인구 분포 시각화
fig, ax = plt.subplots(figsize=(13, 11))
oa_master.plot(column='pop_total', cmap='YlOrRd', ax=ax,
               vmin=0, vmax=oa_master['pop_total'].quantile(0.95),
               linewidth=0, legend=True,
               legend_kwds={'label': 'pop_total (명)', 'shrink': 0.6},
               missing_kwds={'color': 'lightgray'})
ax.set_title('서울 19,097 OA — 거주 인구 분포 (2024 SGIS)')
ax.set_axis_off(); plt.show()"""),

CODE("""# LP 시간 풀 — 새벽 vs 정오 비교
fig, axes = plt.subplots(1, 2, figsize=(18, 9))
vmax = oa_master['lp_pool_24h'].quantile(0.95)

oa_master.plot(column='lp_pool_resident_02_05', cmap='Blues', ax=axes[0],
               vmin=0, vmax=vmax, linewidth=0, legend=True,
               legend_kwds={'shrink': 0.6},
               missing_kwds={'color': 'lightgray'})
axes[0].set_title('새벽 (02-05시) 거주 인구 — 베드타운 패턴')
axes[0].set_axis_off()

oa_master.plot(column='lp_pool_midday_11_15', cmap='Reds', ax=axes[1],
               vmin=0, vmax=vmax, linewidth=0, legend=True,
               legend_kwds={'shrink': 0.6},
               missing_kwds={'color': 'lightgray'})
axes[1].set_title('정오 (11-15시) 활동 인구 — CBD 패턴')
axes[1].set_axis_off()
plt.show()

print('→ 강남·종로·여의도 = 정오에 인구 ↑ (workplace)')
print('→ 외곽 = 새벽에 인구 ↑ (residential)')"""),

MD("""## 5. 자치구별 인구 집계 — 코드 위계 활용

OA 코드 (14자리) 앞 5자리 = 자치구 코드. groupby 한 줄로 자치구 인구.

```
TOT_OA_CD = '11010530010001'
            └┬┘└┬┘ └┬┘ └─┬──┘
            시도 시군구 동  일련번호
            └─sgg─┘
```"""),

CODE("""oa_master['sgg_cd'] = oa_master['TOT_OA_CD'].astype(str).str[:5]
oa_master['sgg_nm']  = oa_master['ADM_NM'] if 'ADM_NM' in oa_master.columns else 'N/A'

sgg_pop = (oa_master.groupby('sgg_cd')['pop_total']
                    .agg(['sum', 'count'])
                    .rename(columns={'sum': 'pop_total', 'count': 'oa_count'})
                    .sort_values('pop_total', ascending=False))
print('자치구별 인구·OA 수 (top 10):')
print(sgg_pop.head(10))
print(f'\\n서울 총인구 (SGIS) : {sgg_pop["pop_total"].sum()/1e6:.2f}M')"""),

MD("""## 6. 정리

- **SGIS 통계** = OA 단위 long-format CSV → wide pivot
- **LOCAL_PEOPLE** = KT 시그널링 시간대 생활인구 (zip 안 31일 × 24시간)
- **2016 vs 2025 OA** = 코드 체계 다름, `oa2016_to_oa2025.parquet` 면적가중 매핑이 매개
- **`oa_master.parquet`** = 모든 OA 변수 한 파일 (19,097 × 150)
- 자치구·행정동 집계는 `TOT_OA_CD[:5]` 또는 `[:8]` groupby 한 줄

→ **다음 Lecture 3** — admdong 단위 통행 발생 (Trip Generation, 통행 수요 메인 시작)."""),

CODE("""print('OK')
print(f'oa_master : {oa_master.shape}')
print(f'서울 자치구 : {oa_master["sgg_cd"].nunique()}')
print(f'유효 OA (pop_total 있는) : {oa_master["pop_total"].notna().sum()}')"""),
]

if __name__ == '__main__':
    HERE = os.path.dirname(__file__)
    write_both(cells,
               os.path.join(HERE, '..', 'notebooks', '02_oa_master.ipynb'),
               os.path.join(HERE, '..', 'slides', '02_oa_master.md'))
