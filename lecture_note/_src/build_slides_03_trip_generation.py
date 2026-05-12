"""03_trip_generation.pptx — Lecture 3 deck (16:9, Uber design + Pretendard)."""
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


DECK_LABEL = "TAZ · Lecture 3 · 통행 발생"


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
             [("LECTURE 03  ·  통행 발생",
               {"style": "eyebrow", "color": C.ink})])

    add_text(s, MARGIN_X, title_y, Inches(7.4), Inches(2.6),
             [("Trip Generation\n— P_i, A_j 회귀 추정",
               {"style": "display_xxl", "color": C.ink,
                "line_spacing": 1.08})])

    add_text(s, MARGIN_X, sub_y, Inches(7.4), Inches(1.1),
             [("admdong 의 출발/도착 통행수를 oa_master 변수에서 회귀로 추정.\n"
               "관측 OD 의 row/col sum 이 진짜 P_obs / A_obs.",
               {"style": "lead", "color": C.body})])

    add_pill(s, MARGIN_X,            cta_y, Inches(1.85), Inches(0.5),
             "Open notebook",  variant="primary")
    add_pill(s, MARGIN_X + Inches(2.00), cta_y, Inches(1.85), Inches(0.5),
             "pi_aj_v1",       variant="secondary")

    # right card
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
        ("왜",            "P_i, A_j 가 Lec 4 gravity\nmodel 의 row/col marginal"),
        ("4단계 위치",     "1단계  ·  Trip Generation"),
        ("사전지식",      "oa_master.parquet (Lec2)\nOLS · LightGBM 기초"),
        ("이번 시간 산출", "pi_aj_v1.parquet\nadmdong × (P/A + 예측)"),
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

    # footer
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
# slide 02 — 왜 admdong 분석 단위
# ============================================================================

def slide_unit_choice(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="UNIT  ·  ADMDONG",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("분석 단위는 왜 admdong 인가",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("분석 단위는 ‘데이터의 입도’ 가 결정 — 관측 OD 가 admdong 으로 공개됨",
               {"style": "lead", "color": C.body})])

    # 3 unit cards
    row_y = Inches(2.7)
    card_w = Inches(3.95)
    card_h = Inches(3.4)
    gap = Inches(0.30)
    units = [
        ("superblock",  "907",  "도로 자연 경계",
         "관측 OD 없음", "outline", "—"),
        ("admdong",     "426",  "통행 수요 단위",
         "admdong_od_20240327",   "emphasis", "본 강좌"),
        ("자치구",       "25",   "정책 단위",
         "gu_hourly_od_202310",   "outline", "검증용"),
    ]
    for i, (name, cnt, role, od, tone, scope) in enumerate(units):
        x = MARGIN_X + (card_w + gap) * i
        if tone == "emphasis":
            add_rounded(s, x, row_y, card_w, card_h, fill=C.primary, line=None,
                        radius_ratio=radius_for(card_w, card_h, 0.21))
            head_c, body_c, eb_c = C.on_dark, C.mute, C.mute
        else:
            add_rounded(s, x, row_y, card_w, card_h, fill=C.canvas, line=C.hairline,
                        line_w_pt=0.75,
                        radius_ratio=radius_for(card_w, card_h, 0.21))
            head_c, body_c, eb_c = C.ink, C.body, C.body

        pad = Inches(0.30)
        add_text(s, x + pad, row_y + pad, card_w - pad * 2, Inches(0.32),
                 [(scope, {"style": "eyebrow", "color": eb_c})])
        add_text(s, x + pad, row_y + pad + Inches(0.36),
                 card_w - pad * 2, Inches(0.5),
                 [(name, {"style": "display_md", "color": head_c, "code": True})])
        add_text(s, x + pad, row_y + pad + Inches(0.95),
                 card_w - pad * 2, Inches(0.8),
                 [(cnt, {"style": "display_xl", "color": head_c, "line_spacing": 1.0})])
        add_text(s, x + pad, row_y + pad + Inches(1.85),
                 card_w - pad * 2, Inches(0.4),
                 [(role, {"style": "body_md_b", "color": head_c})])
        add_text(s, x + pad, row_y + pad + Inches(2.25),
                 card_w - pad * 2, Inches(0.4),
                 [("관측 OD",  {"style": "caption_b", "color": eb_c,
                              "letter_spacing_pt": 1.2})])
        add_text(s, x + pad, row_y + pad + Inches(2.50),
                 card_w - pad * 2, Inches(0.4),
                 [(od, {"style": "body_sm", "color": body_c, "code": True})])


# ============================================================================
# slide 03 — 코드 체계 두 종류 (행안부 vs SGIS)
# ============================================================================

def slide_code_systems(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="ADMDONG  ·  TWO CODES",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("admdong 코드 체계 — 행안부 vs SGIS",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("같은 동, 다른 코드 — 시군구 segment 가 다름.  boundary geojson 이 매개",
               {"style": "lead", "color": C.body})])

    # left: example card — 청운효자동
    ex_x = MARGIN_X
    ex_y = Inches(2.55)
    ex_w = Inches(7.2)
    ex_h = Inches(4.7)
    add_card_content(s, ex_x, ex_y, ex_w, ex_h, radius_in=0.21)

    pad = Inches(0.32)
    add_text(s, ex_x + pad, ex_y + pad, ex_w - pad * 2, Inches(0.32),
             [("EXAMPLE  ·  청운효자동",
               {"style": "eyebrow", "color": C.body})])
    add_text(s, ex_x + pad, ex_y + pad + Inches(0.36),
             ex_w - pad * 2, Inches(0.5),
             [("종로구 청운효자동",
               {"style": "display_md", "color": C.ink})])

    # two boxes side by side: 행안부 / SGIS
    bx_y = ex_y + pad + Inches(1.05)
    bx_w = (ex_w - pad * 2 - Inches(0.25)) // 2
    bx_h = Inches(2.5)

    # 행안부
    add_rounded(s, ex_x + pad, bx_y, bx_w, bx_h, fill=C.canvas_soft, line=None,
                radius_ratio=radius_for(bx_w, bx_h, 0.21))
    add_text(s, ex_x + pad + Inches(0.20), bx_y + Inches(0.20),
             bx_w - Inches(0.4), Inches(0.32),
             [("행안부  ·  admdong_od", {"style": "eyebrow", "color": C.body})])
    add_text(s, ex_x + pad + Inches(0.20), bx_y + Inches(0.55),
             bx_w - Inches(0.4), Inches(0.7),
             [("11110515",
               {"style": "display_lg", "color": C.ink, "code": True,
                "letter_spacing_pt": 1.0})])
    add_text(s, ex_x + pad + Inches(0.20), bx_y + Inches(1.40),
             bx_w - Inches(0.4), Inches(1.0),
             [("종로  ·  11110 segment\nO_ADMDONG_CD / D_ADMDONG_CD",
               {"style": "body_sm", "color": C.body, "code": True})])

    # SGIS
    sx = ex_x + pad + bx_w + Inches(0.25)
    add_rounded(s, sx, bx_y, bx_w, bx_h, fill=C.primary, line=None,
                radius_ratio=radius_for(bx_w, bx_h, 0.21))
    add_text(s, sx + Inches(0.20), bx_y + Inches(0.20),
             bx_w - Inches(0.4), Inches(0.32),
             [("SGIS  ·  oa_master",
               {"style": "eyebrow", "color": C.mute})])
    add_text(s, sx + Inches(0.20), bx_y + Inches(0.55),
             bx_w - Inches(0.4), Inches(0.7),
             [("11010515",
               {"style": "display_lg", "color": C.on_dark, "code": True,
                "letter_spacing_pt": 1.0})])
    add_text(s, sx + Inches(0.20), bx_y + Inches(1.40),
             bx_w - Inches(0.4), Inches(1.0),
             [("종로  ·  11010 segment\nADM_CD / TOT_OA_CD[:8]",
               {"style": "body_sm", "color": C.mute, "code": True})])

    # right: bridge card (boundary geojson)
    rx = ex_x + ex_w + Inches(0.30)
    rw = SLIDE_W - MARGIN_X - rx
    add_card_soft(s, rx, ex_y, rw, ex_h, radius_in=0.21)
    pad2 = Inches(0.28)
    add_text(s, rx + pad2, ex_y + pad2, rw - pad2 * 2, Inches(0.32),
             [("BRIDGE  ·  GEOJSON",
               {"style": "eyebrow", "color": C.body})])
    add_text(s, rx + pad2, ex_y + pad2 + Inches(0.32),
             rw - pad2 * 2, Inches(0.85),
             [("admdong_2023\n.geojson",
               {"style": "display_sm", "color": C.ink,
                "code": True, "line_spacing": 1.20})])
    add_text(s, rx + pad2, ex_y + pad2 + Inches(1.30),
             rw - pad2 * 2, Inches(0.32),
             [("한 행에 두 코드 동시 보관",
               {"style": "body_sm_b", "color": C.ink})])

    fields = [
        ("adm_cd2[:8]", "8", "행안부"),
        ("adm_cd8",     "8", "SGIS 8자리"),
        ("adm_cd",      "7", "SGIS 단축"),
        ("adm_nm",      "str", "동 이름"),
    ]
    fy = ex_y + pad2 + Inches(1.80)
    for f, n, d in fields:
        add_text(s, rx + pad2, fy, Inches(1.4), Inches(0.28),
                 [(f, {"style": "body_sm_b", "color": C.ink, "code": True})])
        add_text(s, rx + pad2 + Inches(1.4), fy, Inches(0.4), Inches(0.28),
                 [(n, {"style": "body_sm", "color": C.body, "code": True})])
        add_text(s, rx + pad2 + Inches(1.85), fy,
                 rw - pad2 * 2 - Inches(1.85), Inches(0.28),
                 [(d, {"style": "body_sm", "color": C.body})])
        fy += Inches(0.34)


# ============================================================================
# slide 04 — Imports & paths
# ============================================================================

def slide_imports(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="SETUP  ·  IMPORTS",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("환경 설정 + Imports",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("Lec1·2 의 ROOT/RAW/DRV + lecture_outputs (산출 파일 폴더)",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "import os, warnings",
        "import numpy as np",
        "import pandas as pd",
        "import geopandas as gpd",
        "import matplotlib.pyplot as plt",
        "from shapely.geometry import Point",
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
        "os.makedirs(OUT_DIR, exist_ok=True)",
        "print('OK')",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(8.8), Inches(4.3),
                  code_lines, label="cell · setup",
                  font_pt=11, line_spacing=1.18)

    # right notes
    notes_x = MARGIN_X + Inches(9.1)
    notes_w = SLIDE_W - MARGIN_X - notes_x
    add_card_content(s, notes_x, Inches(2.55), notes_w, Inches(4.3),
                     radius_in=0.21)
    pad = Inches(0.28)
    add_text(s, notes_x + pad, Inches(2.55) + pad,
             notes_w - pad * 2, Inches(0.32),
             [("NOTES", {"style": "eyebrow", "color": C.body})])

    notes = [
        ("Point",      "CBD 좌표 한 점 — geometry.distance"),
        ("OUT_DIR",    "lecture_outputs 폴더에\nLec3·4 산출물 저장"),
        ("statsmodels","OLS  ·  GLM(Poisson) — Lec4 에서도"),
        ("lightgbm",   "비선형 예측 — feature importance"),
    ]
    ny = Inches(2.55) + pad + Inches(0.5)
    for k, v in notes:
        add_text(s, notes_x + pad, ny,
                 Inches(1.4), Inches(0.32),
                 [(k, {"style": "body_md_b", "color": C.ink, "code": True})])
        add_text(s, notes_x + pad, ny + Inches(0.28),
                 notes_w - pad * 2, Inches(0.7),
                 [(v, {"style": "body_sm", "color": C.body})])
        ny += Inches(0.92)


# ============================================================================
# slide 05 — admdong boundary 로드 + 변환표 만들기 (code)
# ============================================================================

def slide_boundary_load(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="ADMDONG  ·  BOUNDARY",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("admdong 경계 로드 + 두 코드 동시 보관",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("adm_cd2 [:8] (행안부)  +  adm_cd8 (SGIS) 를 int 로 변환해 join 편하게",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "boundary = gpd.read_file(",
        "    os.path.join(RAW, 'admdong_boundary',",
        "                 'admdong_2023.geojson'))",
        "seoul = boundary[",
        "    boundary['sidonm'].str.contains('서울', na=False)",
        "].copy()",
        "print(f'서울 admdong : {len(seoul)}')",
        "",
        "# 두 체계 키 동시 보관 (int 로 변환)",
        "seoul['adm_cd_haengan'] = (seoul['adm_cd2']",
        "                              .astype(str).str[:8].astype(int))",
        "seoul['adm_cd_sgis']    = seoul['adm_cd8'].astype(int)",
        "",
        "seoul = seoul.to_crs(5179)",
        "seoul['area_m2'] = seoul.geometry.area",
        "",
        "print(seoul[['adm_nm','adm_cd_haengan',",
        "             'adm_cd_sgis','area_m2']].head())",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(8.8), Inches(4.7),
                  code_lines, label="cell · load + dual keys",
                  font_pt=11, line_spacing=1.18)

    # right: flow / why
    nx = MARGIN_X + Inches(9.1)
    nw = SLIDE_W - MARGIN_X - nx
    add_card_content(s, nx, Inches(2.55), nw, Inches(4.7),
                     radius_in=0.21)
    pad = Inches(0.28)
    add_text(s, nx + pad, Inches(2.55) + pad,
             nw - pad * 2, Inches(0.32),
             [("STEPS", {"style": "eyebrow", "color": C.body})])
    steps = [
        ("1", "filter 서울",  "sidonm contains '서울'"),
        ("2", "두 코드 추출", "adm_cd2[:8]  +  adm_cd8"),
        ("3", "int 변환",     "join key 는 int 로 통일"),
        ("4", "to_crs(5179)", "면적 계산 m² 표준"),
    ]
    sy = Inches(2.55) + pad + Inches(0.45)
    for n, h, b in steps:
        add_text(s, nx + pad, sy, Inches(0.35), Inches(0.6),
                 [(n, {"style": "display_md", "color": C.ink})])
        add_text(s, nx + pad + Inches(0.40), sy,
                 nw - pad * 2 - Inches(0.40), Inches(0.30),
                 [(h, {"style": "body_md_b", "color": C.ink})])
        add_text(s, nx + pad + Inches(0.40), sy + Inches(0.28),
                 nw - pad * 2 - Inches(0.40), Inches(0.55),
                 [(b, {"style": "body_sm", "color": C.body, "code": True})])
        sy += Inches(0.95)


# ============================================================================
# slide 06 — OA → admdong 변수 집계 (concept)
# ============================================================================

def slide_oa_to_admdong(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="OA → ADMDONG  ·  CONCEPT",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("OA → admdong 변수 집계",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("adm_cd_sgis = TOT_OA_CD[:8]  →  groupby + sum / 인구가중 wmean",
               {"style": "lead", "color": C.body})])

    # left flow diagram (3 stacked steps)
    fx = MARGIN_X
    fy = Inches(2.6)
    fw = Inches(6.4)
    fh = Inches(1.45)
    fgap = Inches(0.25)

    steps = [
        ("oa_master",      "19,097 OA",       "outline",
         "adm_cd_sgis = TOT_OA_CD[:8]"),
        ("groupby + agg",  "sum / wmean",     "emphasis",
         "sum : pop_total, hh_count, lp_pool_*\nwmean : aging_idx, hh_avg_size"),
        ("admdong row",    "426 admdong",     "outline",
         "merge with boundary  ·  adm_g (geo + 변수)"),
    ]
    for i, (head, sub, tone, body) in enumerate(steps):
        y = fy + (fh + fgap) * i
        if tone == "emphasis":
            add_rounded(s, fx, y, fw, fh, fill=C.primary, line=None,
                        radius_ratio=radius_for(fw, fh, 0.21))
            h_c, b_c, eb_c = C.on_dark, C.mute, C.mute
        else:
            add_rounded(s, fx, y, fw, fh, fill=C.canvas, line=C.hairline,
                        line_w_pt=0.75,
                        radius_ratio=radius_for(fw, fh, 0.21))
            h_c, b_c, eb_c = C.ink, C.body, C.body
        pad = Inches(0.28)
        add_text(s, fx + pad, y + pad, Inches(3), Inches(0.32),
                 [(head, {"style": "display_sm", "color": h_c})])
        add_text(s, fx + pad, y + pad + Inches(0.34),
                 Inches(3), Inches(0.32),
                 [(sub, {"style": "body_sm", "color": b_c})])
        add_text(s, fx + Inches(3.1), y + pad,
                 fw - Inches(3.1) - pad, fh - pad * 2,
                 [(body, {"style": "body_sm", "color": b_c, "code": True,
                          "line_spacing": 1.30})])
        # arrow to next
        if i < 2:
            ax = fx + fw // 2
            add_arrow(s, ax, y + fh + Inches(0.02),
                      ax, y + fh + fgap - Inches(0.02),
                      color=C.hairline_mid, weight_pt=1.0)

    # right: 컬럼 분류 카드
    rx = fx + fw + Inches(0.40)
    rw = SLIDE_W - MARGIN_X - rx
    add_card_content(s, rx, fy, rw, fh * 3 + fgap * 2, radius_in=0.21)
    pad = Inches(0.30)
    add_text(s, rx + pad, fy + pad, rw - pad * 2, Inches(0.32),
             [("AGG STRATEGY",
               {"style": "eyebrow", "color": C.body})])

    items = [
        ("sum  (선형 합산)",
         "pop_total, hh_count, ho_total\nlp_pool_resident_02_05\nlp_pool_morning_07_10\nlp_pool_midday_11_15\nlp_pool_evening_18_21\nlp_pool_24h"),
        ("wmean  (인구가중)",
         "aging_idx, hh_avg_size\n→ 작은 OA 의 비율 변수가\n   큰 OA 에 묻히지 않게"),
    ]
    iy = fy + pad + Inches(0.45)
    for k, v in items:
        add_text(s, rx + pad, iy, rw - pad * 2, Inches(0.30),
                 [(k, {"style": "body_md_b", "color": C.ink})])
        add_text(s, rx + pad, iy + Inches(0.30),
                 rw - pad * 2, Inches(1.6),
                 [(v, {"style": "body_sm", "color": C.body, "code": True,
                       "line_spacing": 1.30})])
        iy += Inches(2.1)


# ============================================================================
# slide 07 — 집계 코드 + wmean 정의
# ============================================================================

def slide_aggregation_code(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="AGGREGATION  ·  CODE",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("groupby sum  +  인구가중 wmean",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("두 종류 — sum 한 줄 vs wmean 함수 정의 후 apply",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "m = pd.read_parquet(os.path.join(DRV, 'oa_master.parquet'))",
        "m['adm_cd_sgis'] = (m['TOT_OA_CD']",
        "                       .astype(str).str[:8].astype(int))",
        "",
        "sum_cols = ['pop_total','hh_count','ho_total',",
        "            'lp_pool_resident_02_05','lp_pool_morning_07_10',",
        "            'lp_pool_midday_11_15','lp_pool_evening_18_21',",
        "            'lp_pool_24h']",
        "adm = m.groupby('adm_cd_sgis')[sum_cols].sum().reset_index()",
        "",
        "def wmean(g, val, w='pop_total'):",
        "    ww = g[w].fillna(0); v = g[val]",
        "    return float((v*ww).sum() / ww.sum()) if ww.sum() > 0 \\",
        "           else v.mean()",
        "",
        "for c in ['aging_idx','hh_avg_size']:",
        "    s_ = (m.groupby('adm_cd_sgis')",
        "            .apply(lambda g: wmean(g, c)).rename(f'{c}_w'))",
        "    adm = adm.merge(s_.reset_index(), on='adm_cd_sgis')",
        "",
        "# 경계 + 변환표와 join",
        "adm_g = seoul[['adm_cd_haengan','adm_cd_sgis','adm_nm',",
        "               'sgg','sggnm','area_m2','geometry']] \\",
        "          .merge(adm, on='adm_cd_sgis', how='left')",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(9.6), Inches(4.7),
                  code_lines, label="cell · oa→admdong aggregation",
                  font_pt=10, line_spacing=1.18)

    # right: small reminder pill
    nx = MARGIN_X + Inches(9.9)
    nw = SLIDE_W - MARGIN_X - nx
    add_rounded(s, nx, Inches(2.55), nw, Inches(4.7),
                fill=C.canvas_soft, line=None,
                radius_ratio=radius_for(nw, Inches(4.7), 0.21))
    pad = Inches(0.26)
    add_text(s, nx + pad, Inches(2.55) + pad, nw - pad * 2, Inches(0.32),
             [("WHY wmean?", {"style": "eyebrow", "color": C.body})])
    add_text(s, nx + pad, Inches(2.55) + pad + Inches(0.32),
             nw - pad * 2, Inches(1.0),
             [("비율 변수는\n단순 평균 X",
               {"style": "display_sm", "color": C.ink,
                "line_spacing": 1.25})])
    add_text(s, nx + pad, Inches(2.55) + pad + Inches(1.30),
             nw - pad * 2, Inches(2.5),
             [("aging_idx 가 0.6 인 OA(10명) 와\n0.1 인 OA(5,000명) 의 평균은\n"
               "단순 mean = 0.35 이 아니라,\n인구가중 ≈ 0.10.\n\n"
               "wmean 으로 큰 OA 의 비중을\n반영해 admdong 대표값 산출.",
               {"style": "body_sm", "color": C.body})])


# ============================================================================
# slide 08 — 관측 OD 데이터 개요
# ============================================================================

def slide_obs_od_intro(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="OBS OD  ·  INTRO",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("관측 OD — admdong_od_20240327",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("KT 시그널링 기반 admdong O × D 통행 행렬.  row sum = P_obs, col sum = A_obs",
               {"style": "lead", "color": C.body})])

    # 3 stats cards
    stat_y = Inches(2.6)
    stat_h = Inches(1.55)
    sw = (CONTENT_W - Inches(0.2) * 2) // 3
    sx0 = MARGIN_X
    stats = [
        ("행 수",      "6.7 M",          "전국 admdong × admdong"),
        ("필터",       "서울 + 내국인",   "코드 11 + IN_FORN_DIV_NM=1"),
        ("산출",       "P_obs · A_obs",  "row / col sum 시간대별"),
    ]
    for i, (k, v, sub) in enumerate(stats):
        x = sx0 + (sw + Inches(0.2)) * i
        add_rounded(s, x, stat_y, sw, stat_h, fill=C.canvas_soft, line=None,
                    radius_ratio=radius_for(sw, stat_h, 0.21))
        pad = Inches(0.26)
        add_text(s, x + pad, stat_y + pad, sw - pad * 2, Inches(0.3),
                 [(k, {"style": "eyebrow", "color": C.body})])
        add_text(s, x + pad, stat_y + pad + Inches(0.30),
                 sw - pad * 2, Inches(0.55),
                 [(v, {"style": "display_md", "color": C.ink})])
        add_text(s, x + pad, stat_y + pad + Inches(0.90),
                 sw - pad * 2, Inches(0.45),
                 [(sub, {"style": "body_sm", "color": C.body})])

    # below: schema + filter card
    bot_y = stat_y + stat_h + Inches(0.30)
    bot_h = Inches(2.5)
    bot_w = (CONTENT_W - Inches(0.25)) // 2

    # schema
    add_rounded(s, sx0, bot_y, bot_w, bot_h, fill=C.canvas, line=C.hairline,
                line_w_pt=0.75,
                radius_ratio=radius_for(bot_w, bot_h, 0.21))
    pad = Inches(0.30)
    add_text(s, sx0 + pad, bot_y + pad, bot_w - pad * 2, Inches(0.32),
             [("SCHEMA  ·  9 cols", {"style": "eyebrow", "color": C.body})])
    cols = [
        "O_ADMDONG_CD  ·  D_ADMDONG_CD     (행안부 8자리)",
        "ST_TIME_CD    ·  FNS_TIME_CD       (출발 / 도착 시간)",
        "IN_FORN_DIV_NM                       (내국인=1)",
        "MOVE_PURPOSE                         (목적 코드)",
        "MOVE_DIST  ·  MOVE_TIME  ·  CNT     (거리·시간·통행수)",
    ]
    cy = bot_y + pad + Inches(0.40)
    for c in cols:
        add_text(s, sx0 + pad, cy, bot_w - pad * 2, Inches(0.30),
                 [(c, {"style": "body_sm", "color": C.body, "code": True})])
        cy += Inches(0.32)

    # P/A definition (emphasis dark)
    rx = sx0 + bot_w + Inches(0.25)
    add_rounded(s, rx, bot_y, bot_w, bot_h, fill=C.primary, line=None,
                radius_ratio=radius_for(bot_w, bot_h, 0.21))
    add_text(s, rx + pad, bot_y + pad, bot_w - pad * 2, Inches(0.32),
             [("P_obs  ·  A_obs", {"style": "eyebrow", "color": C.mute})])
    add_text(s, rx + pad, bot_y + pad + Inches(0.36),
             bot_w - pad * 2, Inches(0.55),
             [("관측 row/col sum",
               {"style": "display_sm", "color": C.on_dark})])

    lines = [
        ("P_obs(i)", "= Σ_j  CNT(i → j)   (출발 합)"),
        ("A_obs(j)", "= Σ_i  CNT(i → j)   (도착 합)"),
        ("",         ""),
        ("P/A ratio", "≈ 1.0  (동일 인구의 출발 = 도착)"),
    ]
    ly = bot_y + pad + Inches(1.10)
    for k, v in lines:
        add_text(s, rx + pad, ly, Inches(1.5), Inches(0.30),
                 [(k, {"style": "body_md_b", "color": C.on_dark, "code": True})])
        add_text(s, rx + pad + Inches(1.55), ly,
                 bot_w - pad * 2 - Inches(1.55), Inches(0.30),
                 [(v, {"style": "body_sm", "color": C.mute, "code": True})])
        ly += Inches(0.32)


# ============================================================================
# slide 09 — 관측 OD 필터 + 시간대별 P/A (code)
# ============================================================================

def slide_obs_od_filter(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="OBS OD  ·  FILTER + BANDS",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("OD 로드 → 서울 필터 → 시간대별 P/A 산출",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("4개 시간 band (total / morning / midday / evening) 동시 산출",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "od = pd.read_parquet(",
        "    os.path.join(RAW, 'seoul_living_movement',",
        "                 'admdong_od_20240327.parquet'))",
        "",
        "# 서울 O×D + 내국인",
        "o_seoul = od['O_ADMDONG_CD'].astype(str).str.startswith('11')",
        "d_seoul = od['D_ADMDONG_CD'].astype(str).str.startswith('11')",
        "od = od[o_seoul & d_seoul",
        "        & (od['IN_FORN_DIV_NM'] == 1)].copy()",
        "",
        "# 시간대별 P / A",
        "BANDS = [('total',0,23), ('morning',7,9),",
        "         ('midday',10,15), ('evening',17,19)]",
        "for lbl, lo, hi in BANDS:",
        "    sub = od[od['ST_TIME_CD'].between(lo, hi)]",
        "    p = (sub.groupby('O_ADMDONG_CD')['CNT']",
        "             .sum().rename(f'P_{lbl}'))",
        "    a = (sub.groupby('D_ADMDONG_CD')['CNT']",
        "             .sum().rename(f'A_{lbl}'))",
        "    adm_g = adm_g.merge(p.reset_index().rename(",
        "        columns={'O_ADMDONG_CD':'adm_cd_haengan'}),",
        "        on='adm_cd_haengan', how='left')",
        "    adm_g = adm_g.merge(a.reset_index().rename(",
        "        columns={'D_ADMDONG_CD':'adm_cd_haengan'}),",
        "        on='adm_cd_haengan', how='left')",
        "",
        "adm_g['P_obs'] = adm_g['P_total']",
        "adm_g['A_obs'] = adm_g['A_total']",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(9.6), Inches(4.7),
                  code_lines, label="cell · filter + bands",
                  font_pt=10, line_spacing=1.18)

    # right: insight pill stack
    nx = MARGIN_X + Inches(9.9)
    nw = SLIDE_W - MARGIN_X - nx
    add_rounded(s, nx, Inches(2.55), nw, Inches(4.7),
                fill=C.canvas_soft, line=None,
                radius_ratio=radius_for(nw, Inches(4.7), 0.21))
    pad = Inches(0.26)
    add_text(s, nx + pad, Inches(2.55) + pad, nw - pad * 2, Inches(0.32),
             [("4 BANDS", {"style": "eyebrow", "color": C.body})])

    bands = [
        ("total",   "0–23"),
        ("morning", "7–9"),
        ("midday",  "10–15"),
        ("evening", "17–19"),
    ]
    by = Inches(2.55) + pad + Inches(0.36)
    for k, v in bands:
        # pill
        add_rounded(s, nx + pad, by, Inches(1.2), Inches(0.40),
                    fill=C.primary, line=None, radius_ratio=0.5)
        add_text(s, nx + pad, by, Inches(1.2), Inches(0.40),
                 [(k, {"style": "caption_b", "color": C.on_dark})],
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        add_text(s, nx + pad + Inches(1.35), by + Inches(0.06),
                 nw - pad * 2 - Inches(1.35), Inches(0.30),
                 [(v, {"style": "body_md_b", "color": C.ink, "code": True})])
        by += Inches(0.58)

    add_hairline(s, nx + pad, by + Inches(0.05),
                 nw - pad * 2, color=C.hairline_soft)
    add_text(s, nx + pad, by + Inches(0.15),
             nw - pad * 2, Inches(1.0),
             [("P/A 비 ≈ 1.0\n→ 동일 인구의 출발=도착",
               {"style": "body_sm", "color": C.body})])


# ============================================================================
# slide 10 — LP-차이 proxy 정의 + 실제 결과
# ============================================================================

def slide_lp_proxy(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="LP-PROXY  ·  LESSON",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("LP-차이 proxy — 가설 vs 결과",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("‘출근 후 빠진 인구 = 출근 통행’ 가설 검증.  결과는 예상과 다름",
               {"style": "lead", "color": C.body})])

    # left: hypothesis card
    lx = MARGIN_X
    ly = Inches(2.55)
    lw = Inches(7.6)
    lh = Inches(4.7)
    add_rounded(s, lx, ly, lw, lh, fill=C.canvas, line=C.hairline,
                line_w_pt=0.75, radius_ratio=radius_for(lw, lh, 0.21))
    pad = Inches(0.32)
    add_text(s, lx + pad, ly + pad, lw - pad * 2, Inches(0.32),
             [("HYPOTHESIS", {"style": "eyebrow", "color": C.body})])
    add_text(s, lx + pad, ly + pad + Inches(0.32),
             lw - pad * 2, Inches(0.5),
             [("Stock 차이로 flow 가설",
               {"style": "display_sm", "color": C.ink})])

    formulas = [
        "out_A_signed  =  lp_resident  −  lp_morning      (signed)",
        "outflow_A     =  max(0, out_A_signed)            (clipped)",
        "inflow_A      =  max(0, − out_A_signed)          (workplace)",
    ]
    fy = ly + pad + Inches(1.0)
    for f in formulas:
        add_text(s, lx + pad, fy, lw - pad * 2, Inches(0.30),
                 [(f, {"style": "body_sm", "color": C.body, "code": True})])
        fy += Inches(0.34)

    add_hairline(s, lx + pad, fy + Inches(0.10),
                 lw - pad * 2, color=C.hairline_soft)
    add_text(s, lx + pad, fy + Inches(0.20),
             lw - pad * 2, Inches(0.6),
             [("→ outflow_A 가 P_morning 과 강하게 상관일 것",
               {"style": "body_md_b", "color": C.ink})])

    # 3 lesson lines
    ly2 = fy + Inches(0.90)
    lessons = [
        "stock 차이 ≠ flow 합   (차원 다름)",
        "clip(0) → workplace 신호 0 으로 뭉개짐",
        "단순 raw lp_pool_24h 가 r = +0.88  ·  복잡한 proxy 불필요",
    ]
    for s_ in lessons:
        add_text(s, lx + pad, ly2, lw - pad * 2, Inches(0.34),
                 [("·  " + s_, {"style": "body_sm", "color": C.body})])
        ly2 += Inches(0.34)

    # right: actual results (emphasis)
    rx = lx + lw + Inches(0.30)
    rw = SLIDE_W - MARGIN_X - rx
    add_rounded(s, rx, ly, rw, lh, fill=C.primary, line=None,
                radius_ratio=radius_for(rw, lh, 0.21))
    pad2 = Inches(0.28)
    add_text(s, rx + pad2, ly + pad2, rw - pad2 * 2, Inches(0.32),
             [("ACTUAL RESULTS", {"style": "eyebrow", "color": C.mute})])
    add_text(s, rx + pad2, ly + pad2 + Inches(0.32),
             rw - pad2 * 2, Inches(0.7),
             [("Pearson r",
               {"style": "display_md", "color": C.on_dark,
                "code": True})])

    rows = [
        ("outflow_A vs P_morning", "+0.30"),
        ("out_A_signed vs P_total","−0.78"),
        ("lp_resident vs P_total", "+0.62"),
        ("lp_pool_24h vs P_total", "+0.88"),
    ]
    ry = ly + pad2 + Inches(1.20)
    for k, v in rows:
        add_text(s, rx + pad2, ry, Inches(3.5), Inches(0.30),
                 [(k, {"style": "body_sm", "color": C.mute, "code": True})])
        add_text(s, rx + pad2 + Inches(3.5), ry,
                 rw - pad2 * 2 - Inches(3.5), Inches(0.30),
                 [(v, {"style": "body_md_b", "color": C.on_dark, "code": True})],
                 align=PP_ALIGN.RIGHT)
        ry += Inches(0.40)


# ============================================================================
# slide 11 — proxy 상관표 + 교훈 (code)
# ============================================================================

def slide_proxy_corr_code(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="LP-PROXY  ·  CORRELATION",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("proxy vs 관측 시간대 — Pearson r 표",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("baseline (raw LP) 와 proxy 를 같이 찍어, 복잡도 vs 단순함 비교",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "# signed proxy 정의",
        "r       = adm_g['lp_pool_resident_02_05']",
        "m_pool  = adm_g['lp_pool_morning_07_10']",
        "d_pool  = adm_g['lp_pool_midday_11_15']",
        "",
        "adm_g['out_A_signed'] = r - m_pool",
        "adm_g['outflow_A']    = adm_g['out_A_signed'].clip(lower=0)",
        "adm_g['inflow_A']     = (-adm_g['out_A_signed']).clip(lower=0)",
        "",
        "# proxy vs P_obs 상관",
        "print('=== outflow proxy vs P_obs ===')",
        "for proxy in ['out_A_signed','outflow_A']:",
        "    line = f'  {proxy:<14}'",
        "    for col in ['P_morning','P_midday','P_total']:",
        "        v = adm_g[[proxy, col]].dropna()",
        "        line += f'  {v[proxy].corr(v[col]):>+7.3f}'",
        "    print(line)",
        "",
        "print('--- baseline ---')",
        "for proxy in ['lp_pool_resident_02_05','lp_pool_24h']:",
        "    v = adm_g[[proxy, 'P_total']].dropna()",
        "    r_ = v[proxy].corr(v['P_total'])",
        "    print(f'  {proxy:<28}  r = {r_:+.3f}')",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(9.6), Inches(4.7),
                  code_lines, label="cell · corr matrix",
                  font_pt=10, line_spacing=1.18)

    # right: 3 lessons
    nx = MARGIN_X + Inches(9.9)
    nw = SLIDE_W - MARGIN_X - nx
    add_card_content(s, nx, Inches(2.55), nw, Inches(4.7),
                     radius_in=0.21)
    pad = Inches(0.28)
    add_text(s, nx + pad, Inches(2.55) + pad,
             nw - pad * 2, Inches(0.32),
             [("LESSONS", {"style": "eyebrow", "color": C.body})])

    lessons = [
        ("dimension",
         "Stock 차이 ≠ flow 합 — 차원이 달라\n근본적으로 약한 상관"),
        ("clip(0)",
         "workplace 신호가 0 으로 뭉개짐\n→ signed 가 더 정보 많음"),
        ("baseline first",
         "lp_pool_24h 단독 r = +0.88\n복잡한 proxy 만들기 전\nbaseline 확인 필수"),
    ]
    ly = Inches(2.55) + pad + Inches(0.40)
    for k, v in lessons:
        add_text(s, nx + pad, ly, nw - pad * 2, Inches(0.30),
                 [(k, {"style": "body_md_b", "color": C.ink, "code": True})])
        add_text(s, nx + pad, ly + Inches(0.28),
                 nw - pad * 2, Inches(0.85),
                 [(v, {"style": "body_sm", "color": C.body})])
        ly += Inches(1.20)


# ============================================================================
# slide 12 — 회귀 모델 — OLS + LightGBM
# ============================================================================

def slide_regression(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="REGRESSION  ·  OLS + LGBM",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("회귀 — P_obs ~ 인구·구조 변수",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("OLS (계수 해석)  +  LightGBM (비선형 예측).  log(target+1) 변환",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "# CBD 거리 feature 추가 (시청·광화문)",
        "cbd = gpd.GeoSeries([Point(126.9784, 37.5665)],",
        "                    crs=4326).to_crs(5179).iloc[0]",
        "adm_g['dist_cbd_km'] = (adm_g.geometry.centroid",
        "                              .distance(cbd) / 1000)",
        "",
        "FEATURES = ['pop_total','hh_count','hh_avg_size_w',",
        "            'aging_idx_w','ho_total','area_m2','dist_cbd_km']",
        "df_model = (adm_g[['adm_cd_haengan','adm_nm','sgg','sggnm',",
        "                   'P_obs','A_obs'] + FEATURES + ['geometry']]",
        "               .dropna())",
        "",
        "# OLS — log(target + 1) ~ log(features)",
        "import statsmodels.api as sm",
        "X = df_model[FEATURES].copy()",
        "for c in ['pop_total','hh_count','ho_total','area_m2','dist_cbd_km']:",
        "    X[f'log_{c}'] = np.log1p(X[c]); X = X.drop(columns=c)",
        "X = sm.add_constant(X)",
        "y_P = np.log1p(df_model['P_obs'])",
        "ols_P = sm.OLS(y_P, X).fit()",
        "print(f'OLS R² (log P_obs) : {ols_P.rsquared:.3f}')",
        "",
        "# LightGBM — 비선형",
        "import lightgbm as lgb",
        "gbm_P = lgb.LGBMRegressor(n_estimators=300, learning_rate=0.05,",
        "                          num_leaves=31, random_state=0, verbose=-1)",
        "gbm_P.fit(df_model[FEATURES], y_P)",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(8.8), Inches(4.7),
                  code_lines, label="cell · OLS + LGBM",
                  font_pt=10, line_spacing=1.16)

    # right: target/feature card
    nx = MARGIN_X + Inches(9.1)
    nw = SLIDE_W - MARGIN_X - nx
    add_card_content(s, nx, Inches(2.55), nw, Inches(4.7),
                     radius_in=0.21)
    pad = Inches(0.28)
    add_text(s, nx + pad, Inches(2.55) + pad,
             nw - pad * 2, Inches(0.32),
             [("FEATURES → TARGET", {"style": "eyebrow", "color": C.body})])

    feats = [
        "pop_total",
        "hh_count",
        "hh_avg_size_w",
        "aging_idx_w",
        "ho_total",
        "area_m2",
        "dist_cbd_km",
    ]
    fy = Inches(2.55) + pad + Inches(0.40)
    for f in feats:
        add_text(s, nx + pad, fy, nw - pad * 2, Inches(0.30),
                 [(f, {"style": "body_sm_b", "color": C.ink, "code": True})])
        fy += Inches(0.32)

    # arrow + target pill
    fy += Inches(0.10)
    add_rounded(s, nx + pad, fy, nw - pad * 2, Inches(0.55),
                fill=C.primary, line=None, radius_ratio=0.5)
    add_text(s, nx + pad, fy, nw - pad * 2, Inches(0.55),
             [("log(P_obs + 1)  ·  log(A_obs + 1)",
               {"style": "body_sm_b", "color": C.on_dark, "code": True})],
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)


# ============================================================================
# slide 13 — Spatial CV (random vs sgg)
# ============================================================================

def slide_spatial_cv(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="VALIDATION  ·  SPATIAL CV",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("Spatial CV — 옆 admdong 누수 차단",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("random 5-fold vs GroupKFold(sgg) — R² 정직히 측정",
               {"style": "lead", "color": C.body})])

    # 2 contrast cards
    row_y = Inches(2.55)
    card_w = (CONTENT_W - Inches(0.30)) // 2
    card_h = Inches(3.2)

    # random — outline
    add_rounded(s, MARGIN_X, row_y, card_w, card_h, fill=C.canvas, line=C.hairline,
                line_w_pt=0.75,
                radius_ratio=radius_for(card_w, card_h, 0.21))
    pad = Inches(0.32)
    add_text(s, MARGIN_X + pad, row_y + pad, card_w - pad * 2, Inches(0.32),
             [("RANDOM 5-FOLD", {"style": "eyebrow", "color": C.body})])
    add_text(s, MARGIN_X + pad, row_y + pad + Inches(0.36),
             card_w - pad * 2, Inches(0.55),
             [("낙관적", {"style": "display_md", "color": C.ink})])
    add_text(s, MARGIN_X + pad, row_y + pad + Inches(1.0),
             card_w - pad * 2, Inches(2.0),
             [("같은 자치구 옆 admdong 이\n"
               "train / test 에 섞여 들어감.\n\n"
               "공간 자기상관 (spatial\nautocorrelation) 으로\n"
               "R² 가 과대평가.",
               {"style": "body_sm", "color": C.body})])

    # spatial — emphasis
    rx = MARGIN_X + card_w + Inches(0.30)
    add_rounded(s, rx, row_y, card_w, card_h, fill=C.primary, line=None,
                radius_ratio=radius_for(card_w, card_h, 0.21))
    add_text(s, rx + pad, row_y + pad, card_w - pad * 2, Inches(0.32),
             [("SPATIAL (sgg)", {"style": "eyebrow", "color": C.mute})])
    add_text(s, rx + pad, row_y + pad + Inches(0.36),
             card_w - pad * 2, Inches(0.55),
             [("정직", {"style": "display_md", "color": C.on_dark})])
    add_text(s, rx + pad, row_y + pad + Inches(1.0),
             card_w - pad * 2, Inches(2.0),
             [("GroupKFold(n_splits=5)\nwith groups = sgg.\n\n"
               "모르는 자치구 예측 능력\n측정 — 실제 일반화 성능.",
               {"style": "body_sm", "color": C.mute})])

    # code below
    code_lines = [
        "def cv_score(X, y, splitter, groups=None, label=''):",
        "    rs = []",
        "    for tr, te in splitter.split(X, y, groups=groups):",
        "        m = lgb.LGBMRegressor(n_estimators=300, learning_rate=0.05,",
        "                              num_leaves=31, random_state=0, verbose=-1)",
        "        m.fit(X.iloc[tr], y.iloc[tr])",
        "        rs.append(r2_score(y.iloc[te], m.predict(X.iloc[te])))",
        "    print(f'  {label:<25} R² mean={np.mean(rs):.3f}')",
        "    return rs",
        "",
        "groups = df_model['sgg'].values",
        "_ = cv_score(X_gbm, y_P, KFold(5, shuffle=True, random_state=0), label='random')",
        "_ = cv_score(X_gbm, y_P, GroupKFold(5), groups=groups,         label='spatial')",
    ]
    add_code_cell(s, MARGIN_X, Inches(6.0),
                  CONTENT_W, Inches(1.25),
                  code_lines, label="cell · CV", font_pt=9, line_spacing=1.12)


# ============================================================================
# slide 14 — 잔차 choropleth + 출력 파일
# ============================================================================

def slide_residuals_output(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="RESIDUALS  +  OUTPUT",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("잔차 진단 + pi_aj_v1.parquet 저장",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("잔차가 큰 자치구 = 다음 feature 후보  ·  결과를 Lec 4 입력으로 저장",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "# 잔차 추출",
        "df_model['P_pred_ols'] = ols_P.predict(X)",
        "df_model['resid_P']    = y_P - df_model['P_pred_ols']",
        "df_model['resid_A']    = y_A - ols_A.predict(X)",
        "",
        "# 자치구별 잔차 평균 (절대값 큰 = FE 후보)",
        "sgg_resid = (df_model.groupby('sggnm')[['resid_P','resid_A']]",
        "                     .mean().round(3))",
        "top_resid = sgg_resid.reindex(",
        "    sgg_resid['resid_P'].abs().sort_values(ascending=False).index)",
        "print(top_resid.head(10))",
        "",
        "# pi_aj_v1.parquet 저장",
        "df_model['P_pred_gbm'] = np.expm1(gbm_P.predict(X_gbm))",
        "df_model['A_pred_gbm'] = np.expm1(gbm_A.predict(X_gbm))",
        "",
        "out_cols   = ['adm_cd_haengan','P_obs','A_obs',",
        "              'P_pred_gbm','A_pred_gbm','resid_P','resid_A']",
        "proxy_cols = ['outflow_A','outflow_B','outflow_C',",
        "              'out_A_signed','out_B_signed','out_C_signed']",
        "",
        "out = (adm_g[['adm_cd_haengan'] + proxy_cols]",
        "       .merge(df_model[out_cols], on='adm_cd_haengan', how='right'))",
        "out_path = os.path.join(OUT_DIR, 'pi_aj_v1.parquet')",
        "out.to_parquet(out_path)",
        "print(f'saved : {out_path}')",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(8.8), Inches(4.7),
                  code_lines, label="cell · residuals + save",
                  font_pt=10, line_spacing=1.16)

    # right: schema card
    nx = MARGIN_X + Inches(9.1)
    nw = SLIDE_W - MARGIN_X - nx
    add_card_content(s, nx, Inches(2.55), nw, Inches(4.7),
                     radius_in=0.21)
    pad = Inches(0.28)
    add_text(s, nx + pad, Inches(2.55) + pad,
             nw - pad * 2, Inches(0.32),
             [("pi_aj_v1.parquet", {"style": "eyebrow", "color": C.body})])
    add_text(s, nx + pad, Inches(2.55) + pad + Inches(0.32),
             nw - pad * 2, Inches(0.7),
             [("426 admdong\n× 16 cols",
               {"style": "display_sm", "color": C.ink,
                "line_spacing": 1.25})])

    schema = [
        ("adm_cd_haengan", "행안부 키 — Lec4 join"),
        ("P_obs · A_obs",  "관측 통행 (row/col sum)"),
        ("P_pred_gbm",     "LightGBM 예측"),
        ("A_pred_gbm",     "LightGBM 예측"),
        ("resid_*",        "OLS 잔차"),
        ("outflow_*",      "LP-proxy (비교 보존)"),
    ]
    sy = Inches(2.55) + pad + Inches(1.30)
    for k, v in schema:
        add_text(s, nx + pad, sy, Inches(2.4), Inches(0.28),
                 [(k, {"style": "body_sm_b", "color": C.ink, "code": True})])
        add_text(s, nx + pad + Inches(2.4), sy,
                 nw - pad * 2 - Inches(2.4), Inches(0.28),
                 [(v, {"style": "body_sm", "color": C.body})])
        sy += Inches(0.36)


# ============================================================================
# slide 15 — summary + next
# ============================================================================

def slide_summary(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="SUMMARY  ·  RECAP",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("정리 — Lecture 3 에서 챙길 5가지",
               {"style": "display_xl", "color": C.ink})])

    row_y = Inches(2.2)
    card_w = (CONTENT_W - Inches(0.2) * 4) // 5
    card_h = Inches(2.6)
    cards = [
        ("1", "단위",         "admdong (426)\n관측 OD 자연 단위"),
        ("2", "두 코드",       "행안부 vs SGIS\nboundary geojson 매개"),
        ("3", "P_obs / A_obs", "admdong_od 의\nrow / col sum"),
        ("4", "LP-proxy 교훈", "stock ≠ flow\nbaseline 먼저"),
        ("5", "Spatial CV",   "GroupKFold(sgg)\n옆 admdong 누수 차단"),
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

    # next promo
    pr_y = Inches(5.20)
    pr_h = Inches(1.7)
    add_card_dark(s, MARGIN_X, pr_y, CONTENT_W, pr_h, radius_in=0.21)
    pad = Inches(0.5)
    add_text(s, MARGIN_X + pad, pr_y + pad, Inches(3), Inches(0.32),
             [("NEXT  ·  LECTURE 04",
               {"style": "eyebrow", "color": C.mute})])
    add_text(s, MARGIN_X + pad, pr_y + pad + Inches(0.3),
             Inches(9), Inches(0.7),
             [("Trip Distribution — Poisson gravity GLM + IPF + 정량 검증",
               {"style": "display_md", "color": C.on_dark})])
    btn_w = Inches(2.4); btn_h = Inches(0.55)
    btn_x = MARGIN_X + CONTENT_W - pad - btn_w
    btn_y = pr_y + (pr_h - btn_h) // 2
    add_rounded(s, btn_x, btn_y, btn_w, btn_h, fill=C.canvas, line=None,
                radius_ratio=0.5)
    add_text(s, btn_x, btn_y, btn_w, btn_h,
             [("Open Lecture 04  →", {"style": "button", "color": C.ink})],
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)


# ============================================================================
# main
# ============================================================================

def build():
    prs = Presentation()
    setup_169(prs)

    slides = [
        slide_title,
        slide_unit_choice,
        slide_code_systems,
        slide_imports,
        slide_boundary_load,
        slide_oa_to_admdong,
        slide_aggregation_code,
        slide_obs_od_intro,
        slide_obs_od_filter,
        slide_lp_proxy,
        slide_proxy_corr_code,
        slide_regression,
        slide_spatial_cv,
        slide_residuals_output,
        slide_summary,
    ]
    total = len(slides)

    for i, fn in enumerate(slides, start=1):
        fn(prs, i, total)

    out = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "slides", "03_trip_generation.pptx",
    )
    prs.save(out)
    print(f"OK · {total} slides · {out}")
    return out


if __name__ == "__main__":
    build()
