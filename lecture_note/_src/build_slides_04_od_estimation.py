"""04_od_estimation.pptx — Lecture 4 deck (16:9, Uber design + Pretendard)."""
from __future__ import annotations

import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pptx import Presentation
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Emu, Inches, Pt

from slide_theme_uber import (
    C, SLIDE_W, SLIDE_H, MARGIN_X, MARGIN_Y, CONTENT_W, CONTENT_H, TYPE,
    add_text, add_rounded, add_card_content, add_card_soft, add_card_dark,
    add_pill, add_chip, add_code_cell, add_hairline, add_vline, add_arrow,
    add_page_chrome, new_blank_slide, new_dark_slide, setup_169, radius_for,
)


DECK_LABEL = "TAZ · Lecture 4 · OD 추정"


# ============================================================================
# slide 01 — title
# ============================================================================

def slide_title(prs, idx, total):
    s = new_blank_slide(prs)

    eyebrow_y = Inches(1.2)
    title_y   = Inches(1.7)
    sub_y     = Inches(4.3)
    cta_y     = Inches(5.6)

    add_text(s, MARGIN_X, eyebrow_y, Inches(7), Inches(0.4),
             [("LECTURE 04  ·  OD 추정",
               {"style": "eyebrow", "color": C.ink})])

    add_text(s, MARGIN_X, title_y, Inches(7.4), Inches(2.6),
             [("Trip Distribution\n— Poisson gravity GLM",
               {"style": "display_xxl", "color": C.ink,
                "line_spacing": 1.08})])

    add_text(s, MARGIN_X, sub_y, Inches(7.4), Inches(1.1),
             [("admdong i → j 통행량 T_ij 를 추정하고\n"
               "관측 OD 와 정량 비교 (RMSE · MAPE · R²).",
               {"style": "lead", "color": C.body})])

    add_pill(s, MARGIN_X,            cta_y, Inches(1.85), Inches(0.5),
             "Open notebook",  variant="primary")
    add_pill(s, MARGIN_X + Inches(2.00), cta_y, Inches(1.85), Inches(0.5),
             "od_matrix_v1",   variant="secondary")

    card_x = Inches(8.5)
    card_y = Inches(1.2)
    card_w = SLIDE_W - card_x - MARGIN_X
    card_h = Inches(5.0)
    add_card_content(s, card_x, card_y, card_w, card_h, radius_in=0.21)

    pad = Inches(0.42)
    add_text(s, card_x + pad, card_y + pad, card_w - pad * 2, Inches(0.32),
             [("OVERVIEW", {"style": "eyebrow", "color": C.body})])

    row_y = card_y + pad + Inches(0.55)
    rows = [
        ("왜",            "4단계 모형 2단계.\n공간 패턴을 첫 원리에서"),
        ("4단계 위치",     "2단계  ·  Trip Distribution"),
        ("사전지식",      "pi_aj_v1.parquet (Lec3)\nGLM · IPF 개념"),
        ("이번 시간 산출", "od_matrix_v1.parquet\nadmdong × admdong T_ij"),
    ]
    rh = Inches(0.95)
    for i, (k, v) in enumerate(rows):
        ry = row_y + rh * i
        if i > 0:
            add_hairline(s, card_x + pad, ry - Inches(0.05),
                         card_w - pad * 2, color=C.hairline_soft)
        add_text(s, card_x + pad, ry, Inches(1.3), Inches(0.4),
                 [(k, {"style": "body_md_b", "color": C.ink})])
        add_text(s, card_x + pad + Inches(1.30), ry,
                 card_w - pad * 2 - Inches(1.30), Inches(0.8),
                 [(v, {"style": "body_sm", "color": C.body})])

    add_hairline(s, MARGIN_X, SLIDE_H - Inches(0.85),
                 SLIDE_W - MARGIN_X * 2, color=C.hairline_soft)
    add_text(s, MARGIN_X, SLIDE_H - Inches(0.72), Inches(8), Inches(0.3),
             [("TAZ STUDIO  ·  서울 통행수요 강좌",
               {"style": "eyebrow", "color": C.body})])
    add_text(s, SLIDE_W - MARGIN_X - Inches(3), SLIDE_H - Inches(0.72),
             Inches(3), Inches(0.3),
             [(f"01 / {total:02d}", {"style": "eyebrow", "color": C.body,
                                     "letter_spacing_pt": 1.6})],
             align=PP_ALIGN.RIGHT)


# ============================================================================
# slide 02 — Gravity model 직관
# ============================================================================

def slide_gravity_intuition(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="GRAVITY  ·  INTUITION",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("Gravity model — 직관",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("Newton 중력의 통행 모델 — ‘사람 많은 곳 → 사람 많은 곳’ 으로 가깝게",
               {"style": "lead", "color": C.body})])

    # left: formula card (emphasis)
    fx = MARGIN_X
    fy = Inches(2.55)
    fw = Inches(6.8)
    fh = Inches(4.7)
    add_rounded(s, fx, fy, fw, fh, fill=C.primary, line=None,
                radius_ratio=radius_for(fw, fh, 0.21))
    pad = Inches(0.36)
    add_text(s, fx + pad, fy + pad, fw - pad * 2, Inches(0.32),
             [("FORMULA  ·  PRODUCTION-ATTRACTION",
               {"style": "eyebrow", "color": C.mute})])

    # main formula
    add_text(s, fx + pad, fy + pad + Inches(0.50),
             fw - pad * 2, Inches(1.2),
             [("T_ij  =  K · P_i^α · A_j^β · f(c_ij)",
               {"style": "display_lg", "color": C.on_dark, "code": True,
                "line_spacing": 1.30})])

    # variable definitions
    defs = [
        ("T_ij",    "i → j 통행량"),
        ("K",       "정규화 상수"),
        ("P_i, A_j","발생·유인량"),
        ("α, β",    "elasticity (≈ 1)"),
        ("f(c_ij)", "거리 임피던스"),
    ]
    dy = fy + pad + Inches(1.95)
    for k, v in defs:
        add_text(s, fx + pad, dy, Inches(1.6), Inches(0.30),
                 [(k, {"style": "body_md_b", "color": C.on_dark, "code": True})])
        add_text(s, fx + pad + Inches(1.7), dy,
                 fw - pad * 2 - Inches(1.7), Inches(0.30),
                 [(v, {"style": "body_sm", "color": C.mute})])
        dy += Inches(0.42)

    # right: distance form table
    rx = fx + fw + Inches(0.30)
    rw = SLIDE_W - MARGIN_X - rx
    add_card_content(s, rx, fy, rw, fh, radius_in=0.21)
    pad2 = Inches(0.30)
    add_text(s, rx + pad2, fy + pad2, rw - pad2 * 2, Inches(0.32),
             [("DETERRENCE  ·  3 FORMS",
               {"style": "eyebrow", "color": C.body})])

    forms = [
        ("Power",       "c^{-β}",          "단거리 dominate",  False),
        ("Exponential", "exp(-β_d · c)",   "본 강좌 채택",     True),
        ("Tanner",      "c^a · exp(-bc)",  "hybrid",          False),
    ]
    ty = fy + pad2 + Inches(0.50)
    for name, eq, note, sel in forms:
        # row card
        row_h = Inches(1.05)
        if sel:
            add_rounded(s, rx + pad2, ty, rw - pad2 * 2, row_h,
                        fill=C.primary, line=None,
                        radius_ratio=radius_for(rw - pad2 * 2, row_h, 0.21))
            n_c, e_c, no_c = C.on_dark, C.mute, C.mute
        else:
            add_rounded(s, rx + pad2, ty, rw - pad2 * 2, row_h,
                        fill=C.canvas_soft, line=None,
                        radius_ratio=radius_for(rw - pad2 * 2, row_h, 0.21))
            n_c, e_c, no_c = C.ink, C.body, C.body
        rpad = Inches(0.22)
        add_text(s, rx + pad2 + rpad, ty + rpad,
                 (rw - pad2 * 2) - rpad * 2, Inches(0.32),
                 [(name, {"style": "body_md_b", "color": n_c})])
        add_text(s, rx + pad2 + rpad, ty + rpad + Inches(0.30),
                 (rw - pad2 * 2) - rpad * 2, Inches(0.30),
                 [(eq, {"style": "body_sm_b", "color": n_c, "code": True})])
        add_text(s, rx + pad2 + rpad, ty + rpad + Inches(0.60),
                 (rw - pad2 * 2) - rpad * 2, Inches(0.30),
                 [(note, {"style": "body_sm", "color": no_c})])
        ty += row_h + Inches(0.16)


# ============================================================================
# slide 03 — 왜 Poisson GLM
# ============================================================================

def slide_why_poisson(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="MODEL  ·  POISSON GLM",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("왜 Poisson GLM 인가",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("count 데이터에 자연 적합  +  Poisson MLE = entropy maximization",
               {"style": "lead", "color": C.body})])

    # left: log-linear form box
    fx = MARGIN_X
    fy = Inches(2.55)
    fw = Inches(7.0)
    fh = Inches(2.4)
    add_rounded(s, fx, fy, fw, fh, fill=C.canvas_soft, line=None,
                radius_ratio=radius_for(fw, fh, 0.21))
    pad = Inches(0.32)
    add_text(s, fx + pad, fy + pad, fw - pad * 2, Inches(0.32),
             [("LOG-LINEAR  ·  GLM form", {"style": "eyebrow", "color": C.body})])
    add_text(s, fx + pad, fy + pad + Inches(0.40),
             fw - pad * 2, Inches(0.7),
             [("log E[T_ij] = log K + α log P_i + β log A_j − β_d · c_ij",
               {"style": "body_md_b", "color": C.ink, "code": True})])
    add_text(s, fx + pad, fy + pad + Inches(1.20),
             fw - pad * 2, Inches(0.7),
             [("→  statsmodels.GLM(family=Poisson()).fit()  ·  한 줄",
               {"style": "body_sm", "color": C.body, "code": True})])

    # below: comparison table (left)
    cmp_y = fy + fh + Inches(0.25)
    cmp_h = Inches(2.05)
    add_card_content(s, fx, cmp_y, fw, cmp_h, radius_in=0.21)
    pad = Inches(0.32)
    add_text(s, fx + pad, cmp_y + pad, fw - pad * 2, Inches(0.32),
             [("COMPARE  ·  log-OLS vs Poisson",
               {"style": "eyebrow", "color": C.body})])

    rows = [
        ("log-OLS",  "log(T + ε) hack  ·  작은 flow bias"),
        ("Poisson",  "log link 자연  ·  count 데이터 right likelihood"),
    ]
    ry = cmp_y + pad + Inches(0.40)
    for k, v in rows:
        add_text(s, fx + pad, ry, Inches(1.6), Inches(0.32),
                 [(k, {"style": "body_md_b", "color": C.ink, "code": True})])
        add_text(s, fx + pad + Inches(1.7), ry,
                 fw - pad * 2 - Inches(1.7), Inches(0.32),
                 [(v, {"style": "body_sm", "color": C.body})])
        ry += Inches(0.50)

    # right: 3 reason cards
    rx = fx + fw + Inches(0.30)
    rw = SLIDE_W - MARGIN_X - rx
    add_card_dark(s, rx, fy, rw, fh + cmp_h + Inches(0.25), radius_in=0.21)
    pad2 = Inches(0.30)
    add_text(s, rx + pad2, fy + pad2, rw - pad2 * 2, Inches(0.32),
             [("WHY POISSON", {"style": "eyebrow", "color": C.mute})])
    add_text(s, rx + pad2, fy + pad2 + Inches(0.32),
             rw - pad2 * 2, Inches(0.7),
             [("count 데이터의\n자연스러운 likelihood",
               {"style": "display_sm", "color": C.on_dark,
                "line_spacing": 1.20})])

    reasons = [
        ("non-negative",    "T_ij ≥ 0 자연 보장"),
        ("variance ∝ mean", "큰 flow 가 큰 분산 — 현실적"),
        ("entropy maximum", "Flowerdew & Aitkin 82"),
        ("one-liner",       "GLM(family=Poisson())"),
    ]
    ny = fy + pad2 + Inches(1.45)
    for k, v in reasons:
        add_text(s, rx + pad2, ny, rw - pad2 * 2, Inches(0.30),
                 [(k, {"style": "body_md_b", "color": C.on_dark,
                       "code": True})])
        add_text(s, rx + pad2, ny + Inches(0.28),
                 rw - pad2 * 2, Inches(0.60),
                 [(v, {"style": "body_sm", "color": C.mute})])
        ny += Inches(0.85)


# ============================================================================
# slide 04 — imports & paths
# ============================================================================

def slide_imports(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="SETUP  ·  IMPORTS",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("환경 설정 + Imports",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("Lec3 와 동일 + shapely.LineString (flow line)  ·  statsmodels (GLM)",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "import os, warnings",
        "import numpy as np",
        "import pandas as pd",
        "import geopandas as gpd",
        "import matplotlib.pyplot as plt",
        "from shapely.geometry import Point, LineString",
        "import statsmodels.api as sm",
        "",
        "warnings.filterwarnings('ignore')",
        "%matplotlib inline",
        "plt.rcParams['figure.figsize']     = (10, 6)",
        "plt.rcParams['font.family']        = 'Malgun Gothic'",
        "plt.rcParams['axes.unicode_minus'] = False",
        "",
        "ROOT    = r'F:\\research\\TAZ'",
        "RAW     = os.path.join(ROOT, 'data', 'raw')",
        "DRV     = os.path.join(ROOT, 'data', 'derived')",
        "OUT_DIR = os.path.join(DRV, 'lecture_outputs')",
        "print('OK')",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(8.8), Inches(4.3),
                  code_lines, label="cell · setup",
                  font_pt=11, line_spacing=1.18)

    notes_x = MARGIN_X + Inches(9.1)
    notes_w = SLIDE_W - MARGIN_X - notes_x
    add_card_content(s, notes_x, Inches(2.55), notes_w, Inches(4.3),
                     radius_in=0.21)
    pad = Inches(0.28)
    add_text(s, notes_x + pad, Inches(2.55) + pad,
             notes_w - pad * 2, Inches(0.32),
             [("NOTES", {"style": "eyebrow", "color": C.body})])

    notes = [
        ("LineString",  "top-N flow lines\nflow visualization"),
        ("GLM",         "statsmodels.GLM\n+ family=Poisson()"),
        ("OUT_DIR",     "pi_aj_v1.parquet load\n+ od_matrix_v1.parquet save"),
    ]
    ny = Inches(2.55) + pad + Inches(0.5)
    for k, v in notes:
        add_text(s, notes_x + pad, ny,
                 Inches(1.4), Inches(0.32),
                 [(k, {"style": "body_md_b", "color": C.ink, "code": True})])
        add_text(s, notes_x + pad, ny + Inches(0.28),
                 notes_w - pad * 2, Inches(0.8),
                 [(v, {"style": "body_sm", "color": C.body})])
        ny += Inches(1.10)


# ============================================================================
# slide 05 — P_i, A_j 로드 + 인구가중 centroid
# ============================================================================

def slide_pa_centroid(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="CENTROID  ·  POP-WEIGHTED",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("P_i, A_j 로드 + 인구가중 centroid",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("OA centroid 를 OA 인구로 가중평균 — 단순 geometry centroid 보다 정확",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "pa = pd.read_parquet(os.path.join(OUT_DIR, 'pi_aj_v1.parquet'))",
        "boundary = gpd.read_file(os.path.join(",
        "    RAW, 'admdong_boundary', 'admdong_2023.geojson'))",
        "seoul = boundary[",
        "    boundary['sidonm'].str.contains('서울', na=False)].copy()",
        "seoul['adm_cd_haengan'] = (seoul['adm_cd2']",
        "                              .astype(str).str[:8].astype(int))",
        "seoul = seoul.to_crs(5179)",
        "",
        "g = seoul[['adm_cd_haengan','adm_nm','sgg','sggnm','geometry']] \\",
        "      .merge(pa, on='adm_cd_haengan', how='left')",
        "g = g[g['P_obs'].notna() & g['A_obs'].notna()].reset_index(drop=True)",
        "",
        "# 인구가중 centroid",
        "m = gpd.read_parquet(os.path.join(DRV, 'oa_master.parquet'))",
        "m = m[m['block_id'] != -1].copy()",
        "m['adm_cd_sgis'] = (m['TOT_OA_CD'].astype(str).str[:8].astype(int))",
        "m['cx'] = m.geometry.centroid.x",
        "m['cy'] = m.geometry.centroid.y",
        "m['w']  = m['pop_total'].fillna(0)",
        "",
        "def wmean(sub):",
        "    if sub['w'].sum() == 0:",
        "        return pd.Series({'cx': sub['cx'].mean(),",
        "                          'cy': sub['cy'].mean()})",
        "    return pd.Series({",
        "        'cx': (sub['cx']*sub['w']).sum()/sub['w'].sum(),",
        "        'cy': (sub['cy']*sub['w']).sum()/sub['w'].sum()})",
        "",
        "cent = m.groupby('adm_cd_sgis').apply(wmean).reset_index()",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(9.6), Inches(4.7),
                  code_lines, label="cell · load + centroid",
                  font_pt=10, line_spacing=1.16)

    # right note
    nx = MARGIN_X + Inches(9.9)
    nw = SLIDE_W - MARGIN_X - nx
    add_rounded(s, nx, Inches(2.55), nw, Inches(4.7),
                fill=C.canvas_soft, line=None,
                radius_ratio=radius_for(nw, Inches(4.7), 0.21))
    pad = Inches(0.26)
    add_text(s, nx + pad, Inches(2.55) + pad, nw - pad * 2, Inches(0.32),
             [("WHY POP-WEIGHTED",
               {"style": "eyebrow", "color": C.body})])
    add_text(s, nx + pad, Inches(2.55) + pad + Inches(0.32),
             nw - pad * 2, Inches(1.0),
             [("도시 활동의\n무게중심",
               {"style": "display_sm", "color": C.ink,
                "line_spacing": 1.25})])
    add_text(s, nx + pad, Inches(2.55) + pad + Inches(1.40),
             nw - pad * 2, Inches(2.5),
             [("admdong 의 단순 geometry\ncentroid 는 사람이 없는\n"
               "녹지·산까지 포함.\n\n인구가중 평균은\n"
               "거주·일자리의\n진짜 중심 — 더 정확한\n"
               "거리 행렬.",
               {"style": "body_sm", "color": C.body})])


# ============================================================================
# slide 06 — 426×426 거리 행렬
# ============================================================================

def slide_distance_matrix(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="DISTANCE  ·  426 × 426",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("거리 행렬 — broadcasting 한 줄",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("n × n × 2 차원 broadcasting 으로 모든 쌍 거리 계산  ·  대각선 = intrazonal 반경",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "coords = g[['cx','cy']].values",
        "n = len(coords)",
        "print(f'n = {n}, OD pairs = {n*n:,}')",
        "",
        "# n × n × 2 차원 broadcasting",
        "diff    = coords[:, None, :] - coords[None, :, :]",
        "dist_km = np.sqrt((diff ** 2).sum(axis=2)) / 1000",
        "",
        "# 대각선 = intrazonal — 자기 admdong 반경 근사",
        "np.fill_diagonal(",
        "    dist_km,",
        "    np.sqrt(g.geometry.area.values / np.pi) / 1000)",
        "",
        "print(f'거리 mean   {dist_km.mean():.2f} km')",
        "print(f'거리 median {np.median(dist_km):.2f} km')",
        "print(f'거리 max    {dist_km.max():.2f} km')",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(8.4), Inches(4.7),
                  code_lines, label="cell · distance matrix",
                  font_pt=11, line_spacing=1.18)

    # right: 2 cards
    nx = MARGIN_X + Inches(8.7)
    nw = SLIDE_W - MARGIN_X - nx

    # top — broadcasting trick
    add_card_content(s, nx, Inches(2.55), nw, Inches(2.25), radius_in=0.21)
    pad = Inches(0.28)
    add_text(s, nx + pad, Inches(2.55) + pad, nw - pad * 2, Inches(0.32),
             [("BROADCASTING TRICK",
               {"style": "eyebrow", "color": C.body})])
    add_text(s, nx + pad, Inches(2.55) + pad + Inches(0.36),
             nw - pad * 2, Inches(1.7),
             [("coords[:, None, :]\n"
               "  - coords[None, :, :]\n\n"
               "→ shape (n, n, 2)\n"
               "  명시적 for-loop 불필요",
               {"style": "body_sm", "color": C.body, "code": True,
                "line_spacing": 1.35})])

    # bottom — intrazonal radius (emphasis)
    iy = Inches(5.00)
    add_rounded(s, nx, iy, nw, Inches(2.25), fill=C.primary, line=None,
                radius_ratio=radius_for(nw, Inches(2.25), 0.21))
    add_text(s, nx + pad, iy + pad, nw - pad * 2, Inches(0.32),
             [("DIAGONAL  ·  INTRAZONAL",
               {"style": "eyebrow", "color": C.mute})])
    add_text(s, nx + pad, iy + pad + Inches(0.34),
             nw - pad * 2, Inches(1.7),
             [("√(area / π)\n\n"
               "자기 admdong 의 평균\n"
               "이동 거리 ≈ 반경.\n"
               "self-distance = 0 이면\n"
               "intrazonal 폭주.",
               {"style": "body_sm", "color": C.mute, "code": True,
                "line_spacing": 1.30})])


# ============================================================================
# slide 07 — 관측 OD 행렬 T_obs
# ============================================================================

def slide_t_obs(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="OBS MATRIX  ·  T_obs",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("관측 OD 행렬 T_obs — long → wide",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("groupby (O, D) → np.zeros 채우기.  row/col sum 으로 P_obs / A_obs 검증",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "od = pd.read_parquet(os.path.join(",
        "    RAW, 'seoul_living_movement',",
        "    'admdong_od_20240327.parquet'))",
        "o_seoul = od['O_ADMDONG_CD'].astype(str).str.startswith('11')",
        "d_seoul = od['D_ADMDONG_CD'].astype(str).str.startswith('11')",
        "od = od[o_seoul & d_seoul",
        "        & (od['IN_FORN_DIV_NM'] == 1)].copy()",
        "",
        "od_agg = (od.groupby(['O_ADMDONG_CD','D_ADMDONG_CD'],",
        "                      as_index=False)['CNT'].sum())",
        "",
        "# admdong → index 매핑",
        "adm_idx = {c: i for i, c in enumerate(g['adm_cd_haengan'])}",
        "od_agg['i'] = od_agg['O_ADMDONG_CD'].map(adm_idx)",
        "od_agg['j'] = od_agg['D_ADMDONG_CD'].map(adm_idx)",
        "od_agg = od_agg.dropna(subset=['i','j'])",
        "",
        "T_obs = np.zeros((n, n), dtype=float)",
        "T_obs[od_agg['i'].astype(int).values,",
        "      od_agg['j'].astype(int).values] = od_agg['CNT'].values",
        "",
        "P_arr = g['P_obs'].values; A_arr = g['A_obs'].values",
        "print(f'row_sum vs P_obs max diff : '",
        "      f'{np.abs(T_obs.sum(axis=1) - P_arr).max():.4f}')",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(8.8), Inches(4.7),
                  code_lines, label="cell · T_obs build",
                  font_pt=10, line_spacing=1.16)

    # right: stat card
    nx = MARGIN_X + Inches(9.1)
    nw = SLIDE_W - MARGIN_X - nx
    add_card_content(s, nx, Inches(2.55), nw, Inches(4.7),
                     radius_in=0.21)
    pad = Inches(0.28)
    add_text(s, nx + pad, Inches(2.55) + pad,
             nw - pad * 2, Inches(0.32),
             [("EXPECTED STATS", {"style": "eyebrow", "color": C.body})])

    stats = [
        ("T_obs shape",   "(426, 426)"),
        ("T_obs sum",     "~ 8.5 M"),
        ("0 비율",         "~ 76 %"),
        ("row=P, col=A",  "max diff < 1e-3"),
    ]
    sy = Inches(2.55) + pad + Inches(0.40)
    for k, v in stats:
        add_text(s, nx + pad, sy, Inches(1.8), Inches(0.30),
                 [(k, {"style": "body_sm_b", "color": C.ink, "code": True})])
        add_text(s, nx + pad + Inches(1.8), sy,
                 nw - pad * 2 - Inches(1.8), Inches(0.30),
                 [(v, {"style": "body_sm", "color": C.body, "code": True})])
        sy += Inches(0.40)

    # sparsity callout
    add_hairline(s, nx + pad, sy + Inches(0.05),
                 nw - pad * 2, color=C.hairline_soft)
    add_text(s, nx + pad, sy + Inches(0.20),
             nw - pad * 2, Inches(0.30),
             [("SPARSITY", {"style": "eyebrow", "color": C.body})])
    add_text(s, nx + pad, sy + Inches(0.50),
             nw - pad * 2, Inches(2.0),
             [("76% cell 이 0\n→ Poisson 이 자연.\n"
               "log-OLS 면 log(0) hack\n필요.",
               {"style": "body_sm", "color": C.body})])


# ============================================================================
# slide 08 — Poisson GLM fit (code)
# ============================================================================

def slide_glm_fit(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="GLM  ·  FIT",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("Poisson GLM fit — 한 줄로 추정",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("181,050 행 (425 × 426)  ·  α, β, β_d 추정",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "i_idx, j_idx = np.indices((n, n))",
        "mask = i_idx != j_idx   # 대각선 제외",
        "",
        "flat = pd.DataFrame({",
        "    'T':     T_obs[mask],",
        "    'log_P': np.log(P_arr[i_idx[mask]] + 1),",
        "    'log_A': np.log(A_arr[j_idx[mask]] + 1),",
        "    'd':     dist_km[mask],",
        "})",
        "print(f'fit rows : {len(flat):,}')",
        "",
        "X_glm = sm.add_constant(flat[['log_P','log_A','d']])",
        "glm = sm.GLM(flat['T'], X_glm,",
        "             family=sm.families.Poisson()).fit()",
        "",
        "print(f'log K  = {glm.params[\"const\"]:>7.3f}')",
        "print(f'α (P)  = {glm.params[\"log_P\"]:>7.3f}')",
        "print(f'β (A)  = {glm.params[\"log_A\"]:>7.3f}')",
        "print(f'β_d    = {glm.params[\"d\"]:>7.3f}'",
        "      f'  → 1km ↑ → ×{np.exp(glm.params[\"d\"]):.3f}')",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(8.8), Inches(4.7),
                  code_lines, label="cell · GLM fit",
                  font_pt=10, line_spacing=1.16)

    # right: typical results
    nx = MARGIN_X + Inches(9.1)
    nw = SLIDE_W - MARGIN_X - nx
    add_card_dark(s, nx, Inches(2.55), nw, Inches(4.7), radius_in=0.21)
    pad = Inches(0.28)
    add_text(s, nx + pad, Inches(2.55) + pad,
             nw - pad * 2, Inches(0.32),
             [("TYPICAL FIT", {"style": "eyebrow", "color": C.mute})])

    rows = [
        ("log K", "≈ −12.5"),
        ("α (P)", "≈ +0.95"),
        ("β (A)", "≈ +0.95"),
        ("β_d",   "≈ −0.20"),
    ]
    ry = Inches(2.55) + pad + Inches(0.40)
    for k, v in rows:
        add_text(s, nx + pad, ry, Inches(1.4), Inches(0.30),
                 [(k, {"style": "body_md_b", "color": C.on_dark, "code": True})])
        add_text(s, nx + pad + Inches(1.4), ry,
                 nw - pad * 2 - Inches(1.4), Inches(0.30),
                 [(v, {"style": "body_md_b", "color": C.on_dark, "code": True})],
                 align=PP_ALIGN.RIGHT)
        ry += Inches(0.42)

    add_text(s, nx + pad, ry + Inches(0.10),
             nw - pad * 2, Inches(1.5),
             [("→ α, β ≈ 1\n  자연적 elasticity\n\n"
               "→ exp(−0.20)\n  = 0.82\n  1km 늘면 통행 18% ↓",
               {"style": "body_sm", "color": C.mute,
                "line_spacing": 1.30})])


# ============================================================================
# slide 09 — IPF / Furness
# ============================================================================

def slide_ipf(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="IPF  ·  FURNESS",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("IPF / Furness — marginal 보존",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("GLM 만으론 row/col marginal 정확 보존 X — 반복 row · col 정규화",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "# GLM 예측치를 seed 로",
        "K = np.exp(glm.params['const'])",
        "T_seed = (K",
        "  * (P_arr[:, None] + 1) ** glm.params['log_P']",
        "  * (A_arr[None, :] + 1) ** glm.params['log_A']",
        "  * np.exp(glm.params['d'] * dist_km))",
        "",
        "def ipf(T, P, A, max_iter=50, tol=1e-3):",
        "    T = T.copy(); history = []",
        "    for it in range(max_iter):",
        "        rs = T.sum(axis=1)",
        "        T = T * np.where(rs > 0, P/rs, 1)[:, None]",
        "        cs = T.sum(axis=0)",
        "        T = T * np.where(cs > 0, A/cs, 1)[None, :]",
        "        err = max(",
        "            np.abs(T.sum(axis=1)-P).max() / max(P.max(),1),",
        "            np.abs(T.sum(axis=0)-A).max() / max(A.max(),1))",
        "        history.append(err)",
        "        if err < tol: break",
        "    return T, history",
        "",
        "T_pred, hist = ipf(T_seed, P_arr, A_arr)",
        "print(f'IPF iter : {len(hist)}, final err : {hist[-1]:.5f}')",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(8.4), Inches(4.7),
                  code_lines, label="cell · IPF",
                  font_pt=10, line_spacing=1.16)

    # right: algorithm card
    nx = MARGIN_X + Inches(8.7)
    nw = SLIDE_W - MARGIN_X - nx
    add_card_content(s, nx, Inches(2.55), nw, Inches(4.7),
                     radius_in=0.21)
    pad = Inches(0.28)
    add_text(s, nx + pad, Inches(2.55) + pad,
             nw - pad * 2, Inches(0.32),
             [("ALGORITHM", {"style": "eyebrow", "color": C.body})])

    steps = [
        ("1", "row 보정",  "T = T × (P_i / Σ_j T_ij)"),
        ("2", "col 보정",  "T = T × (A_j / Σ_i T_ij)"),
        ("3", "수렴 체크",  "err < tol → break"),
        ("4", "반복",       "보통 6–10 iter, 1% 이내"),
    ]
    sy = Inches(2.55) + pad + Inches(0.45)
    for n_, h, b in steps:
        add_text(s, nx + pad, sy, Inches(0.35), Inches(0.6),
                 [(n_, {"style": "display_md", "color": C.ink})])
        add_text(s, nx + pad + Inches(0.40), sy,
                 nw - pad * 2 - Inches(0.40), Inches(0.30),
                 [(h, {"style": "body_md_b", "color": C.ink})])
        add_text(s, nx + pad + Inches(0.40), sy + Inches(0.28),
                 nw - pad * 2 - Inches(0.40), Inches(0.55),
                 [(b, {"style": "body_sm", "color": C.body, "code": True})])
        sy += Inches(0.95)


# ============================================================================
# slide 10 — 검증 4종 overview
# ============================================================================

def slide_validation_overview(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="VALIDATION  ·  4 PASSES",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("검증 4종 — 정량 + 정성",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("RMSE·R² 만으론 부족.  4가지 각도로 모델 진단",
               {"style": "lead", "color": C.body})])

    # 4 cards
    row_y = Inches(2.6)
    card_w = (CONTENT_W - Inches(0.25) * 3) // 4
    card_h = Inches(3.6)
    items = [
        ("9", "정량",       "RMSE · MAPE · R²",
         "log-log scatter\n작은 flow 까지 확인",
         "outline"),
        ("10", "TLD",       "Trip Length\nDistribution",
         "관측 vs 예측 거리 분포\n일치하면 β_d 적합",
         "emphasis"),
        ("11", "Flow lines", "Top-100 flow",
         "강남·종로 attractor?\n외곽 producer?\nface validity",
         "outline"),
        ("12", "Intrazonal", "T_ii / row sum",
         "자기 admdong 내 통행\n비율 — 면적과 관계",
         "outline"),
    ]
    for i, (num, head, sub, body, tone) in enumerate(items):
        x = MARGIN_X + (card_w + Inches(0.25)) * i
        if tone == "emphasis":
            add_rounded(s, x, row_y, card_w, card_h, fill=C.primary, line=None,
                        radius_ratio=radius_for(card_w, card_h, 0.21))
            n_c, h_c, b_c = C.mute, C.on_dark, C.mute
        else:
            add_rounded(s, x, row_y, card_w, card_h, fill=C.canvas_soft, line=None,
                        radius_ratio=radius_for(card_w, card_h, 0.21))
            n_c, h_c, b_c = C.mute, C.ink, C.body
        pad = Inches(0.26)
        add_text(s, x + pad, row_y + pad, card_w - pad * 2, Inches(0.5),
                 [(num, {"style": "display_lg", "color": n_c})])
        add_text(s, x + pad, row_y + pad + Inches(0.55),
                 card_w - pad * 2, Inches(0.4),
                 [(head, {"style": "display_sm", "color": h_c})])
        add_text(s, x + pad, row_y + pad + Inches(0.95),
                 card_w - pad * 2, Inches(0.7),
                 [(sub, {"style": "body_sm_b", "color": h_c, "code": True,
                         "line_spacing": 1.25})])
        add_text(s, x + pad, row_y + pad + Inches(1.85),
                 card_w - pad * 2, card_h - pad * 2 - Inches(1.85),
                 [(body, {"style": "body_sm", "color": b_c,
                          "line_spacing": 1.35})])

    # bottom: pill summary
    pl_y = row_y + card_h + Inches(0.30)
    add_rounded(s, MARGIN_X, pl_y, CONTENT_W, Inches(0.6),
                fill=C.primary, line=None, radius_ratio=0.5)
    add_text(s, MARGIN_X, pl_y, CONTENT_W, Inches(0.6),
             [("정량  ·  정성 — 각각 모자란 부분을 다른 각도가 잡아준다",
               {"style": "body_md_b", "color": C.on_dark})],
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)


# ============================================================================
# slide 11 — 검증 1·2 — 정량 + TLD (code)
# ============================================================================

def slide_validation_quant(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="VALIDATION  ·  QUANT + TLD",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("검증 1·2 — RMSE / R²  +  Trip Length",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("정량 + 거리 분포 — 평균 통행거리 매칭 확인",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "flat_obs  = T_obs[mask]",
        "flat_pred = T_pred[mask]",
        "",
        "rmse = np.sqrt(((flat_obs - flat_pred)**2).mean())",
        "mape = (np.abs(flat_obs - flat_pred)",
        "         / (flat_obs + 1)).mean()",
        "ss_res = ((flat_obs - flat_pred)**2).sum()",
        "ss_tot = ((flat_obs - flat_obs.mean())**2).sum()",
        "r2 = 1 - ss_res / ss_tot",
        "print(f'RMSE : {rmse:.2f}')",
        "print(f'MAPE : {mape*100:.1f}%')",
        "print(f'R²   : {r2:.3f}')",
        "",
        "# Trip Length Distribution",
        "flat_d = dist_km[mask]",
        "bins = np.arange(0, 31, 1)",
        "tld_obs,  _ = np.histogram(flat_d, bins=bins, weights=flat_obs)",
        "tld_pred, _ = np.histogram(flat_d, bins=bins, weights=flat_pred)",
        "",
        "mean_obs  = (flat_d * flat_obs ).sum() / flat_obs.sum()",
        "mean_pred = (flat_d * flat_pred).sum() / flat_pred.sum()",
        "print(f'평균 통행거리 — 관측 {mean_obs:.2f} km'",
        "      f'  ·  예측 {mean_pred:.2f} km')",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(8.4), Inches(4.7),
                  code_lines, label="cell · quant + tld",
                  font_pt=10, line_spacing=1.16)

    # right: metrics card
    nx = MARGIN_X + Inches(8.7)
    nw = SLIDE_W - MARGIN_X - nx
    add_card_content(s, nx, Inches(2.55), nw, Inches(2.25),
                     radius_in=0.21)
    pad = Inches(0.28)
    add_text(s, nx + pad, Inches(2.55) + pad,
             nw - pad * 2, Inches(0.32),
             [("METRICS  ·  TYPICAL",
               {"style": "eyebrow", "color": C.body})])
    stats = [
        ("RMSE", "~ 25"),
        ("MAPE", "~ 60%"),
        ("R²",   "~ 0.55"),
    ]
    sy = Inches(2.55) + pad + Inches(0.40)
    for k, v in stats:
        add_text(s, nx + pad, sy, Inches(1.4), Inches(0.30),
                 [(k, {"style": "body_md_b", "color": C.ink, "code": True})])
        add_text(s, nx + pad + Inches(1.4), sy,
                 nw - pad * 2 - Inches(1.4), Inches(0.30),
                 [(v, {"style": "body_md_b", "color": C.ink, "code": True})],
                 align=PP_ALIGN.RIGHT)
        sy += Inches(0.40)

    # bottom — TLD card (emphasis)
    iy = Inches(5.00)
    add_rounded(s, nx, iy, nw, Inches(2.25), fill=C.primary, line=None,
                radius_ratio=radius_for(nw, Inches(2.25), 0.21))
    add_text(s, nx + pad, iy + pad,
             nw - pad * 2, Inches(0.32),
             [("TLD  ·  mean 통행거리",
               {"style": "eyebrow", "color": C.mute})])
    add_text(s, nx + pad, iy + pad + Inches(0.34),
             nw - pad * 2, Inches(1.6),
             [("관측 ~ 5.0 km\n예측 ~ 5.4 km\n\n→ 거의 일치하면\n  β_d 적합한 신호",
               {"style": "body_sm", "color": C.mute, "code": True,
                "line_spacing": 1.30})])


# ============================================================================
# slide 12 — 시간대별 β_d 변화
# ============================================================================

def slide_band_beta(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="BANDS  ·  β_d BY HOUR",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("시간대별 β_d — 출근 vs 야간",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("출근시간 = 장거리 통근 ↑ → β_d 절대값 ↓ (덜 가파름)",
               {"style": "lead", "color": C.body})])

    # bands table
    tab_x = MARGIN_X
    tab_y = Inches(2.55)
    tab_w = Inches(7.2)
    tab_h = Inches(4.7)
    add_card_content(s, tab_x, tab_y, tab_w, tab_h, radius_in=0.21)

    pad = Inches(0.32)
    add_text(s, tab_x + pad, tab_y + pad, tab_w - pad * 2, Inches(0.32),
             [("BANDS  ·  TYPICAL β_d",
               {"style": "eyebrow", "color": C.body})])

    head = ("BAND", "HOURS", "β_d", "INTERPRETATION")
    rows = [
        ("전체",     "0–23",     "−0.20",  "baseline"),
        ("출근",     "7–9",      "−0.15",  "장거리 통근 ↑"),
        ("주간",     "10–16",    "−0.22",  "general"),
        ("퇴근",     "17–19",    "−0.16",  "장거리 ↑"),
        ("야간",     "22–5",     "−0.30",  "단거리 dominate"),
    ]
    col_x = [tab_x + pad,
             tab_x + pad + Inches(1.4),
             tab_x + pad + Inches(2.6),
             tab_x + pad + Inches(4.0)]
    col_w = [Inches(1.4), Inches(1.2), Inches(1.4),
             tab_w - pad * 2 - Inches(4.0)]
    head_y = tab_y + pad + Inches(0.55)
    for ci, c in enumerate(head):
        add_text(s, col_x[ci], head_y, col_w[ci], Inches(0.3),
                 [(c, {"style": "eyebrow", "color": C.body})])

    ry = head_y + Inches(0.45)
    for band, hours, beta, interp in rows:
        emp = band == "야간"
        if emp:
            add_rounded(s, tab_x + pad, ry - Inches(0.08),
                        tab_w - pad * 2, Inches(0.62),
                        fill=C.primary, line=None,
                        radius_ratio=radius_for(tab_w - pad * 2, Inches(0.62), 0.18))
            tc = C.on_dark; bc = C.mute
        else:
            add_hairline(s, tab_x + pad, ry - Inches(0.06),
                         tab_w - pad * 2, color=C.hairline_soft)
            tc = C.ink; bc = C.body
        add_text(s, col_x[0], ry, col_w[0], Inches(0.5),
                 [(band, {"style": "body_md_b", "color": tc})])
        add_text(s, col_x[1], ry, col_w[1], Inches(0.5),
                 [(hours, {"style": "body_md", "color": bc, "code": True})])
        add_text(s, col_x[2], ry, col_w[2], Inches(0.5),
                 [(beta, {"style": "body_md_b", "color": tc, "code": True})])
        add_text(s, col_x[3], ry, col_w[3], Inches(0.5),
                 [(interp, {"style": "body_sm", "color": bc})])
        ry += Inches(0.65)

    # right column: code snippet
    rx = tab_x + tab_w + Inches(0.30)
    rw = SLIDE_W - MARGIN_X - rx
    code_lines = [
        "def fit_band(od_sub):",
        "    od_a = (od_sub.groupby(",
        "        ['O_ADMDONG_CD','D_ADMDONG_CD'],",
        "        as_index=False)['CNT'].sum())",
        "    od_a['i'] = od_a['O_ADMDONG_CD'].map(adm_idx)",
        "    od_a['j'] = od_a['D_ADMDONG_CD'].map(adm_idx)",
        "    od_a = od_a.dropna(subset=['i','j'])",
        "    T = np.zeros((n, n))",
        "    T[od_a['i'].astype(int).values,",
        "      od_a['j'].astype(int).values] = od_a['CNT'].values",
        "    P_t = T.sum(1); A_t = T.sum(0)",
        "    fl = pd.DataFrame({",
        "       'T':     T[mask],",
        "       'log_P': np.log(P_t[i_idx[mask]]+1),",
        "       'log_A': np.log(A_t[j_idx[mask]]+1),",
        "       'd':     dist_km[mask]})",
        "    glm_t = sm.GLM(fl['T'],",
        "        sm.add_constant(fl[['log_P','log_A','d']]),",
        "        family=sm.families.Poisson()).fit()",
        "    return glm_t.params['d']",
    ]
    add_code_cell(s, rx, tab_y, rw, tab_h, code_lines,
                  label="cell · fit_band",
                  font_pt=9, line_spacing=1.15)


# ============================================================================
# slide 13 — od_matrix_v1 저장
# ============================================================================

def slide_save_output(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="OUTPUT  ·  od_matrix_v1",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("od_matrix_v1.parquet 저장",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("long format 으로 변환  ·  T_obs=0 & 작은 T_pred 는 제외해 파일 크기 절약",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "ii, jj = np.indices((n, n))",
        "flat_out = pd.DataFrame({",
        "    'adm_O_haengan': g['adm_cd_haengan'].values[ii.flatten()],",
        "    'adm_D_haengan': g['adm_cd_haengan'].values[jj.flatten()],",
        "    'adm_O_nm':      g['adm_nm'].values[ii.flatten()],",
        "    'adm_D_nm':      g['adm_nm'].values[jj.flatten()],",
        "    'T_obs':         T_obs.flatten(),",
        "    'T_pred':        T_pred.flatten(),",
        "    'distance_km':   dist_km.flatten(),",
        "})",
        "flat_out['residual'] = flat_out['T_obs'] - flat_out['T_pred']",
        "",
        "# 둘 다 작은 cell 은 drop — 파일 크기 절약",
        "flat_out = flat_out[",
        "    (flat_out['T_obs'] > 0) | (flat_out['T_pred'] > 0.5)",
        "].reset_index(drop=True)",
        "print(f'OD pairs : {len(flat_out):,}')",
        "",
        "od_path = os.path.join(OUT_DIR, 'od_matrix_v1.parquet')",
        "flat_out.to_parquet(od_path)",
        "print(f'saved : {od_path}')",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(8.8), Inches(4.7),
                  code_lines, label="cell · save od_matrix",
                  font_pt=10, line_spacing=1.16)

    # right: schema card
    nx = MARGIN_X + Inches(9.1)
    nw = SLIDE_W - MARGIN_X - nx
    add_card_content(s, nx, Inches(2.55), nw, Inches(4.7),
                     radius_in=0.21)
    pad = Inches(0.28)
    add_text(s, nx + pad, Inches(2.55) + pad,
             nw - pad * 2, Inches(0.32),
             [("od_matrix_v1.parquet", {"style": "eyebrow", "color": C.body})])
    add_text(s, nx + pad, Inches(2.55) + pad + Inches(0.32),
             nw - pad * 2, Inches(0.7),
             [("OD pairs\n(sparse, drop 0)",
               {"style": "display_sm", "color": C.ink,
                "line_spacing": 1.25})])

    schema = [
        ("adm_O_haengan", "출발 admdong"),
        ("adm_D_haengan", "도착 admdong"),
        ("T_obs",         "관측"),
        ("T_pred",        "예측"),
        ("distance_km",   "거리"),
        ("residual",      "obs − pred"),
    ]
    sy = Inches(2.55) + pad + Inches(1.35)
    for k, v in schema:
        add_text(s, nx + pad, sy, Inches(2.4), Inches(0.28),
                 [(k, {"style": "body_sm_b", "color": C.ink, "code": True})])
        add_text(s, nx + pad + Inches(2.4), sy,
                 nw - pad * 2 - Inches(2.4), Inches(0.28),
                 [(v, {"style": "body_sm", "color": C.body})])
        sy += Inches(0.36)


# ============================================================================
# slide 14 — summary + next (강좌 마무리)
# ============================================================================

def slide_summary(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="SUMMARY  ·  COURSE WRAP",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("정리 — Lecture 4  +  강좌 마무리",
               {"style": "display_xl", "color": C.ink})])

    row_y = Inches(2.2)
    card_w = (CONTENT_W - Inches(0.2) * 4) // 5
    card_h = Inches(2.6)
    cards = [
        ("1", "Gravity",       "T ∝ P · A · f(c)\n사람·사람·거리"),
        ("2", "Poisson GLM",   "count likelihood\nlog link · 1줄"),
        ("3", "IPF / Furness", "row · col 반복\n6–10 iter 수렴"),
        ("4", "검증 4종",      "정량 + TLD\n+ flow + intrazonal"),
        ("5", "시간대 β_d",     "출근 ↓  ·  야간 ↑\n행동 일관성"),
    ]
    for i, (num, head, body) in enumerate(cards):
        x = MARGIN_X + (card_w + Inches(0.2)) * i
        add_rounded(s, x, row_y, card_w, card_h, fill=C.canvas_soft, line=None,
                    radius_ratio=radius_for(card_w, card_h, 0.21))
        pad = Inches(0.22)
        add_text(s, x + pad, row_y + pad, card_w - pad * 2, Inches(0.5),
                 [(num, {"style": "display_lg", "color": C.mute})])
        add_text(s, x + pad, row_y + pad + Inches(0.55),
                 card_w - pad * 2, Inches(0.5),
                 [(head, {"style": "display_sm", "color": C.ink})])
        add_text(s, x + pad, row_y + pad + Inches(1.10),
                 card_w - pad * 2, Inches(1.4),
                 [(body, {"style": "body_sm", "color": C.body})])

    # bottom: closing dark card
    pr_y = Inches(5.20)
    pr_h = Inches(1.7)
    add_card_dark(s, MARGIN_X, pr_y, CONTENT_W, pr_h, radius_in=0.21)
    pad = Inches(0.5)
    add_text(s, MARGIN_X + pad, pr_y + pad, Inches(4), Inches(0.32),
             [("DONE  ·  COURSE MAIN TRACK",
               {"style": "eyebrow", "color": C.mute})])
    add_text(s, MARGIN_X + pad, pr_y + pad + Inches(0.3),
             Inches(9), Inches(0.7),
             [("stock + 도로·토지이용 + 관측 OD 로 4단계 1·2 baseline 을 fit 하고 검증",
               {"style": "display_md", "color": C.on_dark})])
    # next pill (A1 appendix or end)
    btn_w = Inches(2.4); btn_h = Inches(0.55)
    btn_x = MARGIN_X + CONTENT_W - pad - btn_w
    btn_y = pr_y + (pr_h - btn_h) // 2
    add_rounded(s, btn_x, btn_y, btn_w, btn_h, fill=C.canvas, line=None,
                radius_ratio=0.5)
    add_text(s, btn_x, btn_y, btn_w, btn_h,
             [("A1 부록 → 뷰어", {"style": "button", "color": C.ink})],
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)


# ============================================================================
# main
# ============================================================================

def build():
    prs = Presentation()
    setup_169(prs)

    slides = [
        slide_title,
        slide_gravity_intuition,
        slide_why_poisson,
        slide_imports,
        slide_pa_centroid,
        slide_distance_matrix,
        slide_t_obs,
        slide_glm_fit,
        slide_ipf,
        slide_validation_overview,
        slide_validation_quant,
        slide_band_beta,
        slide_save_output,
        slide_summary,
    ]
    total = len(slides)

    for i, fn in enumerate(slides, start=1):
        fn(prs, i, total)

    out = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "slides", "04_od_estimation.pptx",
    )
    prs.save(out)
    print(f"OK · {total} slides · {out}")
    return out


if __name__ == "__main__":
    build()
