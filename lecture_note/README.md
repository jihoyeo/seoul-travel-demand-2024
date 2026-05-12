# 서울 통행수요 모델링 실습 강좌

서울시 집계구·필지·도로·생활인구·관측 OD 데이터를 가공해 **admdong 단위 통행 발생(P_i, A_j)·통행 분포(O-D)** 까지 처음부터 끝까지 따라가는 실습형 강좌. 본 워크스페이스(`F:\research\TAZ`) 의 데이터 파이프라인을 그대로 활용한다.

대상: **교통공학 대학원생** 수준. Python·pandas 익숙, GeoPandas/공간분석 처음, 4단계 통행수요모형 이론은 아는 가정.

---

## 디렉터리

```
lecture_note/
├─ slides/       발표용 Markdown (강의 슬라이드, 모듈별 1개)
├─ notebooks/    실습 Jupyter 노트북 (슬라이드와 1:1 매칭)
├─ reproduce/    부록 — 파이프라인 재현 (raw → derived) 노트북
├─ references/   참고 노트북 (gravity model, OD 시각화)
└─ _src/         노트북 빌더 + 셀 정의 소스 (학생 사용 X, 유지보수 용)
```

슬라이드 형식: 순수 Markdown. 페이지 구분은 `---`. GitHub/VSCode/Obsidian 에서 그대로 읽거나, [Marp](https://marp.app/) 로 PPT/PDF export 가능.

---

## 모듈 인덱스

```
강좌 전체 흐름
─────────────────────────────────────────────────────────────
Lec1 ──→ Lec2 ──→ Lec3 ──→ Lec4         메인 (통행 수요)
공간     OA       P/A      OD
데이터   마스터    발생     추정 + 검증

             └─→ Lec5 (부록 트랙, 도시 형태)
                 superblock + 토지이용
```

| # | 모듈 | 슬라이드 | 노트북 | 핵심 |
|---|---|---|---|---|
| Lecture 1 | 공간 데이터 둘러보기 | [01_spatial_data.md](slides/01_spatial_data.md) | [01_spatial_data.ipynb](notebooks/01_spatial_data.ipynb) | 강좌 개요, 4단계 모형, admdong·OA·필지, CRS 3종 |
| Lecture 2 | OA 마스터 구축 | [02_oa_master.md](slides/02_oa_master.md) | [02_oa_master.ipynb](notebooks/02_oa_master.ipynb) | SGIS 통계 long→wide, LOCAL_PEOPLE, 2016/2025 OA 매핑, `oa_master.parquet` |
| Lecture 3 | 통행 발생 (Trip Generation) | [03_trip_generation.md](slides/03_trip_generation.md) | [03_trip_generation.ipynb](notebooks/03_trip_generation.ipynb) | 관측 P/A, LP-차이 proxy, OLS+LightGBM, spatial CV |
| Lecture 4 | OD 추정 (Trip Distribution) | [04_od_estimation.md](slides/04_od_estimation.md) | [04_od_estimation.ipynb](notebooks/04_od_estimation.ipynb) | Poisson gravity GLM, IPF/Furness, RMSE/MAPE/R² 정량 검증, 시간대별 β_d |
| Lecture 5 | Superblock + 토지이용 (부록) | [05_superblock_landuse.md](slides/05_superblock_landuse.md) | [05_superblock_landuse.ipynb](notebooks/05_superblock_landuse.ipynb) | 907 도시 superblock, LU share, Shannon entropy |

부록 — 재현 노트북 (raw → derived 파이프라인, 학생은 결과물만 사용해도 됨):

| # | 노트북 | 풀이 대상 | 소요 |
|---|---|---|---|
| R1 | [R1_oa2016_to_oa2025.ipynb](reproduce/R1_oa2016_to_oa2025.ipynb) | `blocks/oa2016_to_oa2025.py` | ~30s |
| R2 | [R2_build_oa_master.ipynb](reproduce/R2_build_oa_master.ipynb) | `blocks/build_oa_master.py` | ~6분 |
| R3 | [R3_build_blocks_oa.ipynb](reproduce/R3_build_blocks_oa.ipynb) | `blocks/build_blocks_oa.py` | ~60s |
| R4 | [R4_aggregate_landuse.ipynb](reproduce/R4_aggregate_landuse.ipynb) | `blocks/aggregate_landuse.py` | ~30s |

부록 — 시각화 도구 만들기 (강의 외 트랙, AI 코딩 도구 사용):

| # | 슬라이드 | 핵심 |
|---|---|---|
| A1 | [A1_vibe_coding_viewer.md](slides/A1_vibe_coding_viewer.md) | deck.gl 인터랙티브 지도를 AI 에게 단계별로 요청하기, perf 트릭 7가지, `data/viewer/` reference 재현 |

---

## 데이터 카탈로그

각 데이터는 처음 등장하는 모듈에서 출처·스키마·전처리 방법을 다룬다.

| 데이터 | 위치 | 도입 강의 | 단위 / 규모 |
|---|---|---|---|
| `admdong_boundary/admdong_2023.geojson` | raw | Lecture 1 | 행정동 426 (서울) — 행안부·SGIS 두 코드 동시 보관 |
| `sgis_oa/bnd_oa_11_2025_2Q.*` | raw | Lecture 1 | 2025 SGIS 집계구 19,097개 |
| `sgis_oa_2016/집계구.*` | raw | Lecture 2 (R1) | 2016 SGIS 집계구 (LOCAL_PEOPLE 권위 경계) |
| `sgis_census/11_2024년_*.csv` | raw | Lecture 2 | 10개 통계 CSV (인구·가구·주택, long format) |
| `seoul_living_pop/LOCAL_PEOPLE_202412.zip` | raw | Lecture 2 | KT 시그널링 시간대 생활인구 (일별 CSV 31개) |
| `seoul_living_movement/admdong_od_20240327.parquet` | raw | Lecture 3 | 관측 admdong OD (6.7M 행, 시간대·목적·거리·통행수) |
| `seoul_living_movement/gu_hourly_od_202310.parquet` | raw | (참고) | 자치구 시간대 OD — 본 강좌에서 사용 X |
| `lsmd_zoning/AL_D154_*` | raw | Lecture 5 | 필지 (지목·용도지역) |
| `roads/centerline/*`, `roads/segment/*` | raw | Lecture 5 | 도로 중심선·세그먼트 (superblock 경계용) |
| `oa2016_to_oa2025.parquet` | derived | Lecture 2 | 2016 → 2025 OA 면적가중 매핑 (R1 산출) |
| `oa_master.parquet` | derived | Lecture 2 | 통합 OA 마스터 (19,097 × 150) — R2 산출 |
| `seoul_blocks.fgb`, `oa_to_block.parquet` | derived | Lecture 5 | superblock 907 + OA→block 매핑 (R3 산출) |

---

## 환경 설정

```bash
# Python 3.11 권장
conda create -n taz python=3.11
conda activate taz

pip install "geopandas>=1.0" "shapely>=2.0.6" pandas pyarrow \
            matplotlib statsmodels lightgbm scikit-learn \
            jupyterlab contextily mapclassify
```

데이터 경로: 강좌 노트북은 `F:\research\TAZ\data\raw\*` (원본) 과 `F:\research\TAZ\data\derived\*` (R1~R4 산출) 를 입력으로 한다. raw 에서 derived 를 만드는 과정은 `reproduce/` 의 R1~R4 노트북에 분리.

```python
# 노트북 상단 공통 패턴
import os
ROOT = r'F:\research\TAZ'
RAW  = os.path.join(ROOT, 'data', 'raw')
DRV  = os.path.join(ROOT, 'data', 'derived')
OUT_DIR = os.path.join(DRV, 'lecture_outputs')
```

---

## 강좌 운영 안내

- 한 학기 ≈ 5~6 주차. 매주 1 강의 (Lecture 5 는 시간 여유 시 부록).
- 강의 진행: 슬라이드(md) 로 개념·이론 30분 → 노트북 함께 실행 60분 → 학생 자율 변형 30분.
- 평가: Lecture 2 까지의 데이터 이해 + Lecture 3·4 모델링 결과의 face validity·정량 검증 토론.
- 본 강좌의 핵심 학습 목표 — **실데이터 적용의 어려움** 을 솔직히 보이는 것:
  - 공간 단위 통합 (OA → admdong → sgg)
  - 코드 체계 변환 (행안부 vs SGIS, 2016 vs 2025)
  - proxy vs 관측 비교 (LP-차이 proxy 의 한계)
  - 정량 검증 (RMSE, MAPE, R², TLD)

---

## 산출물

각 노트북은 `data/derived/lecture_outputs/` 에 다음을 저장:

| 산출물 | 강의 | 스키마 |
|---|---|---|
| `pi_aj_v1.parquet` | Lecture 3 | `adm_cd_haengan, P_obs, A_obs, P_pred_gbm, A_pred_gbm, residuals, proxy_cols` |
| `od_matrix_v1.parquet` | Lecture 4 | `adm_O_haengan, adm_D_haengan, T_obs, T_pred, distance_km, residual` |
| `block_master.parquet` | Lecture 5 (부록) | `block_id, P_i, A_j, geometry, LU features...` |

이 산출물은 본 프로젝트의 향후 모델링 단계 baseline 으로 재활용된다.
