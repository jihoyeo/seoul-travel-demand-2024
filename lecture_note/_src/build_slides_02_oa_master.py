"""02_oa_master.pptx — Lecture 2 deck (16:9, Uber design system + Pretendard).

Same theme/primitives as Lecture 1:
  - black/white duet, pill 999 px on every interactive shape
  - editorial illustrations absent; rhythm carried by polarity flips
  - Pretendard ExtraBold / Bold / Medium / ExtraLight only
  - code rendered as light code cells (canvas-softer + Cascadia Code), tight line-spacing
"""
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


DECK_LABEL = "TAZ · Lecture 2 · OA 마스터 구축"


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
             [("LECTURE 02  ·  OA 마스터",
               {"style": "eyebrow", "color": C.ink})])

    add_text(s, MARGIN_X, title_y, Inches(7.4), Inches(2.6),
             [("OA 마스터 구축\n+ SGIS · LOCAL_PEOPLE",
               {"style": "display_xxl", "color": C.ink,
                "line_spacing": 1.08})])

    add_text(s, MARGIN_X, sub_y, Inches(7.4), Inches(1.1),
             [("흩어진 SGIS 통계 · LOCAL_PEOPLE 을 한 파일로 묶어\n"
               "이후 모든 OA 분석의 출발점 (oa_master.parquet) 을 만든다.",
               {"style": "lead", "color": C.body})])

    add_pill(s, MARGIN_X,            cta_y, Inches(1.85), Inches(0.5),
             "Open notebook",  variant="primary")
    add_pill(s, MARGIN_X + Inches(2.00), cta_y, Inches(1.85), Inches(0.5),
             "View parquet",   variant="secondary")

    # right column: overview card
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
        ("왜",            "raw 가 여러 파일에 흩어져 있어\n매번 join 하면 비효율"),
        ("4단계 위치",     "1단계 (Trip Generation)\n입력 변수 정비"),
        ("사전지식",      "pandas pivot · GeoPandas\n공간 join (Lec1)"),
        ("이번 시간 산출", "oa_master.parquet\n19,097 OA × 150 cols"),
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

    # footer block
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
# slide 02 — raw → derived flow
# ============================================================================

def slide_raw_to_derived(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="DATA  ·  PIPELINE",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("raw 데이터 → oa_master 한 파일",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("3 종 raw 를 한 키 (TOT_OA_CD) 로 합쳐, 이후 회귀·OD·superblock 의 공통 입력",
               {"style": "lead", "color": C.body})])

    # raw source cards (3 stacked on left)
    src_x = MARGIN_X
    src_y0 = Inches(2.75)
    src_w = Inches(3.5)
    src_h = Inches(1.20)
    src_gap = Inches(0.16)
    sources = [
        ("공간 데이터",     "sgis_oa  ·  sgis_oa_2016",
         "2025 / 2016 OA 폴리곤"),
        ("SGIS 통계",      "sgis_census  ·  10 CSV",
         "인구 · 가구 · 주택"),
        ("LOCAL_PEOPLE",   "seoul_living_pop  ·  zip",
         "KT 시그널링 시간대 인구"),
    ]
    for i, (eb, name, sub) in enumerate(sources):
        y = src_y0 + (src_h + src_gap) * i
        add_rounded(s, src_x, y, src_w, src_h, fill=C.canvas_soft, line=None,
                    radius_ratio=radius_for(src_w, src_h, 0.21))
        pad = Inches(0.26)
        add_text(s, src_x + pad, y + pad, src_w - pad * 2, Inches(0.3),
                 [(eb, {"style": "eyebrow", "color": C.body})])
        add_text(s, src_x + pad, y + pad + Inches(0.30),
                 src_w - pad * 2, Inches(0.35),
                 [(name, {"style": "display_sm", "color": C.ink, "code": True})])
        add_text(s, src_x + pad, y + pad + Inches(0.60),
                 src_w - pad * 2, Inches(0.35),
                 [(sub, {"style": "body_sm", "color": C.body})])

    # hub: oa_master.parquet (centered, dark)
    hub_w = Inches(2.8)
    hub_h = Inches(2.1)
    hub_x = src_x + src_w + Inches(0.95)
    hub_y = src_y0 + (src_h * 3 + src_gap * 2 - hub_h) // 2
    add_rounded(s, hub_x, hub_y, hub_w, hub_h, fill=C.primary, line=None,
                radius_ratio=radius_for(hub_w, hub_h, 0.21))
    pad = Inches(0.32)
    add_text(s, hub_x + pad, hub_y + pad, hub_w - pad * 2, Inches(0.32),
             [("DERIVED  ·  MASTER", {"style": "eyebrow", "color": C.mute})])
    add_text(s, hub_x + pad, hub_y + pad + Inches(0.38),
             hub_w - pad * 2, Inches(0.7),
             [("oa_master\n.parquet",
               {"style": "display_md", "color": C.on_dark,
                "code": True, "line_spacing": 1.15})])
    add_text(s, hub_x + pad, hub_y + hub_h - pad - Inches(0.55),
             hub_w - pad * 2, Inches(0.55),
             [("19,097 OA  ·  150 cols",
               {"style": "body_sm_b", "color": C.mute})])

    # arrows
    for i in range(3):
        y = src_y0 + (src_h + src_gap) * i + src_h // 2
        add_arrow(s, src_x + src_w + Inches(0.03), y,
                  hub_x - Inches(0.03), hub_y + hub_h // 2,
                  color=C.hairline_mid, weight_pt=1.0)

    # right column: 'what's inside' card
    rx = hub_x + hub_w + Inches(0.50)
    rw = SLIDE_W - MARGIN_X - rx
    rh_card = src_h * 3 + src_gap * 2
    add_card_content(s, rx, src_y0, rw, rh_card, radius_in=0.21)
    pad = Inches(0.32)
    add_text(s, rx + pad, src_y0 + pad, rw - pad * 2, Inches(0.32),
             [("WHAT'S INSIDE  ·  150 COLS",
               {"style": "eyebrow", "color": C.body})])

    groups = [
        ("키 · 기하",    "TOT_OA_CD, ADM_CD, block_id\n+ geometry, area_m2"),
        ("인구·가구·주택", "pop_total, hh_count, ho_total ..."),
        ("성연령 81종",   "in_age_M00_04  ...  in_age_F75p"),
        ("LP 시간 풀 6",  "resident_02_05 · morning_07_10\nmidday_11_15 · evening_18_21 ..."),
    ]
    gy = src_y0 + pad + Inches(0.45)
    for k, v in groups:
        add_text(s, rx + pad, gy, rw - pad * 2, Inches(0.30),
                 [(k, {"style": "body_md_b", "color": C.ink})])
        add_text(s, rx + pad, gy + Inches(0.26),
                 rw - pad * 2, Inches(0.55),
                 [(v, {"style": "body_sm", "color": C.body, "code": True})])
        gy += Inches(0.80)


# ============================================================================
# slide 03 — imports & paths
# ============================================================================

def slide_imports(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="SETUP  ·  IMPORTS",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("환경 설정 + Imports",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("Lecture 1 과 동일.  RAW / DRV 경로 한 번 정의해 이후 셀에서 재사용",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "import os, sys, zipfile, warnings",
        "import numpy as np",
        "import pandas as pd",
        "import geopandas as gpd",
        "import matplotlib.pyplot as plt",
        "",
        "warnings.filterwarnings('ignore')",
        "%matplotlib inline",
        "plt.rcParams['figure.figsize']     = (10, 6)",
        "plt.rcParams['font.family']        = 'Malgun Gothic'",
        "plt.rcParams['axes.unicode_minus'] = False",
        "",
        "ROOT = r'F:\\research\\TAZ'",
        "RAW  = os.path.join(ROOT, 'data', 'raw')",
        "DRV  = os.path.join(ROOT, 'data', 'derived')",
        "print('OK')",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(8.8), Inches(4.3),
                  code_lines, label="cell · setup",
                  font_pt=12, line_spacing=1.20)

    # right side: notes
    notes_x = MARGIN_X + Inches(9.1)
    notes_w = SLIDE_W - MARGIN_X - notes_x
    add_card_content(s, notes_x, Inches(2.55), notes_w, Inches(4.3),
                     radius_in=0.21)
    pad = Inches(0.30)
    add_text(s, notes_x + pad, Inches(2.55) + pad,
             notes_w - pad * 2, Inches(0.32),
             [("NOTES", {"style": "eyebrow", "color": C.body})])

    notes = [
        ("zipfile",     "LP 데이터는 zip 안 31일 CSV — 스트리밍 read"),
        ("RAW",         "원본 SGIS / LP / 경계 데이터"),
        ("DRV",         "파생 파일 (oa2016_to_oa2025, oa_master)"),
        ("CP949",       "SGIS · LP CSV 의 한글 인코딩"),
    ]
    ny = Inches(2.55) + pad + Inches(0.5)
    for k, v in notes:
        add_text(s, notes_x + pad, ny,
                 Inches(1.4), Inches(0.32),
                 [(k, {"style": "body_md_b", "color": C.ink, "code": True})])
        add_text(s, notes_x + pad, ny + Inches(0.28),
                 notes_w - pad * 2, Inches(0.55),
                 [(v, {"style": "body_sm", "color": C.body})])
        ny += Inches(0.90)


# ============================================================================
# slide 04 — SGIS 데이터 구조 (long → wide)
# ============================================================================

def slide_sgis_structure(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="SGIS  ·  LONG → WIDE",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("SGIS 인구·가구·주택 — long format",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("한 OA 가 여러 행 (long) — 분석엔 wide 가 편함.  pivot 한 줄로 변환",
               {"style": "lead", "color": C.body})])

    # left: SGIS CSV table
    tab_x = MARGIN_X
    tab_y = Inches(2.55)
    tab_w = Inches(7.6)
    tab_h = Inches(4.7)
    add_card_content(s, tab_x, tab_y, tab_w, tab_h, radius_in=0.21)

    pad = Inches(0.35)
    add_text(s, tab_x + pad, tab_y + pad, tab_w - pad * 2, Inches(0.32),
             [("SGIS_CENSUS  ·  10 CSV 구조",
               {"style": "eyebrow", "color": C.body})])

    rows = [
        ("FILE", "ROW FORMAT"),
        ("11_2024년_인구총괄(총인구).csv",      "long: OA × 항목"),
        ("11_2024년_성연령별인구.csv",          "long: OA × 81 성연령"),
        ("11_2024년_가구총괄.csv",              "long: OA × 항목"),
        ("11_2024년_세대구성별가구.csv",         "long: OA × 세대구성"),
        ("11_2024년_주택총괄.csv",              "long: OA × 항목"),
        ("...  (총 10개 CSV)",                  ""),
    ]
    rh = Inches(0.42)
    head_y = tab_y + pad + Inches(0.45)
    for ri, (a, b) in enumerate(rows):
        y = head_y + rh * ri
        if ri == 0:
            add_text(s, tab_x + pad, y, Inches(4.4), Inches(0.3),
                     [(a, {"style": "eyebrow", "color": C.body})])
            add_text(s, tab_x + pad + Inches(4.4), y, Inches(2.6), Inches(0.3),
                     [(b, {"style": "eyebrow", "color": C.body})])
        else:
            add_hairline(s, tab_x + pad, y - Inches(0.04),
                         tab_w - pad * 2, color=C.hairline_soft)
            add_text(s, tab_x + pad, y, Inches(4.4), Inches(0.35),
                     [(a, {"style": "body_sm_b", "color": C.ink, "code": True})])
            add_text(s, tab_x + pad + Inches(4.4), y, Inches(2.6), Inches(0.35),
                     [(b, {"style": "body_sm", "color": C.body, "code": True})])

    # right column: 2 cards (long vs wide)
    rx = tab_x + tab_w + Inches(0.30)
    rw = SLIDE_W - MARGIN_X - rx
    # top card — long
    lh = Inches(2.25)
    add_rounded(s, rx, tab_y, rw, lh, fill=C.canvas_soft, line=None,
                radius_ratio=radius_for(rw, lh, 0.21))
    pad2 = Inches(0.26)
    add_text(s, rx + pad2, tab_y + pad2, rw - pad2 * 2, Inches(0.3),
             [("LONG  ·  raw format", {"style": "eyebrow", "color": C.body})])
    add_text(s, rx + pad2, tab_y + pad2 + Inches(0.30),
             rw - pad2 * 2, Inches(0.45),
             [("한 OA = 여러 행",
               {"style": "display_sm", "color": C.ink})])
    add_text(s, rx + pad2, tab_y + pad2 + Inches(0.72),
             rw - pad2 * 2, Inches(1.2),
             [("연도 · OA · 항목코드 · 값\n각 항목마다 한 row.\n→ 항목별 비교가 불편",
               {"style": "body_sm", "color": C.body})])

    # bottom card — wide (emphasis)
    wh = Inches(2.25)
    wy = tab_y + lh + Inches(0.20)
    add_rounded(s, rx, wy, rw, wh, fill=C.primary, line=None,
                radius_ratio=radius_for(rw, wh, 0.21))
    add_text(s, rx + pad2, wy + pad2, rw - pad2 * 2, Inches(0.3),
             [("WIDE  ·  분석 표준", {"style": "eyebrow", "color": C.mute})])
    add_text(s, rx + pad2, wy + pad2 + Inches(0.30),
             rw - pad2 * 2, Inches(0.45),
             [("한 OA = 한 행",
               {"style": "display_sm", "color": C.on_dark})])
    add_text(s, rx + pad2, wy + pad2 + Inches(0.72),
             rw - pad2 * 2, Inches(1.4),
             [("pivot(index=oa_cd,\n     columns=item_cd,\n     values=value)",
               {"style": "body_sm", "color": C.mute, "code": True,
                "line_spacing": 1.25})])


# ============================================================================
# slide 05 — SGIS load + pivot (code)
# ============================================================================

def slide_sgis_pivot(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="SGIS  ·  PIVOT",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("SGIS 인구총괄 — 헤더 없는 CSV 로 시작",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("read_csv (cp949, header=None) → to_numeric → pivot_table 한 줄",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "# 헤더 없는 CSV — 컬럼: 연도, OA 코드, 항목 코드, 값",
        "pop = pd.read_csv(",
        "    os.path.join(RAW, 'sgis_census',",
        "                 '11_2024년_인구총괄(총인구).csv'),",
        "    encoding='cp949', header=None,",
        "    names=['year', 'oa_cd', 'item_cd', 'value'])",
        "print(f'shape : {pop.shape}')",
        "",
        "# 'N/A' (통계 보호) → NaN (0 으로 채우면 안 됨)",
        "pop['value'] = pd.to_numeric(pop['value'], errors='coerce')",
        "",
        "# long → wide",
        "wide = pop.pivot_table(index='oa_cd', columns='item_cd',",
        "                       values='value', aggfunc='first')",
        "print(f'wide shape : {wide.shape}')",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(8.8), Inches(4.7),
                  code_lines, label="cell · sgis pivot",
                  font_pt=11, line_spacing=1.18)

    # right: pattern card
    nx = MARGIN_X + Inches(9.1)
    nw = SLIDE_W - MARGIN_X - nx
    add_card_content(s, nx, Inches(2.55), nw, Inches(4.7),
                     radius_in=0.21)
    pad = Inches(0.30)
    add_text(s, nx + pad, Inches(2.55) + pad,
             nw - pad * 2, Inches(0.32),
             [("WHY 'N/A' ≠ 0", {"style": "eyebrow", "color": C.body})])
    add_text(s, nx + pad, Inches(2.55) + pad + Inches(0.40),
             nw - pad * 2, Inches(0.8),
             [("통계 보호로\n인구 작은 OA",
               {"style": "display_sm", "color": C.ink,
                "line_spacing": 1.25})])
    add_text(s, nx + pad, Inches(2.55) + pad + Inches(1.55),
             nw - pad * 2, Inches(2.5),
             [("SGIS 는 인구가 너무 적은 OA 의\n"
               "수치를 'N/A' 로 마스킹 (노출 위험).\n\n"
               "fillna(0) 으로 채우면\n"
               "→ '비어있음' 과 '0명' 을 혼동.\n\n"
               "errors='coerce' 로 안전하게\n"
               "NaN 유지 — pivot 후에도 보존.",
               {"style": "body_sm", "color": C.body})])


# ============================================================================
# slide 06 — LOCAL_PEOPLE 데이터 개요
# ============================================================================

def slide_lp_intro(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="LOCAL_PEOPLE  ·  INTRO",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("LOCAL_PEOPLE — 시간대별 생활인구",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("KT 휴대전화 시그널링 → OA 단위 시간대별 추정 인구  ·  서울 열린데이터 광장",
               {"style": "lead", "color": C.body})])

    # 4 stats cards
    stat_y = Inches(2.6)
    stat_h = Inches(1.5)
    sw = Inches(2.85)
    sgap = Inches(0.20)
    sx0 = MARGIN_X
    stats = [
        ("출처",       "data.seoul.go.kr",  "서울 열린데이터 광장"),
        ("방법",       "KT 시그널링",        "휴대전화 → OA 시간 인구"),
        ("형식",       "zip · 31 CSV",      "12월 한달, 일별 분할"),
        ("크기",       "3.7 GB",            "CSV 한 개 ≈ 126 MB"),
    ]
    for i, (k, v, sub) in enumerate(stats):
        x = sx0 + (sw + sgap) * i
        add_rounded(s, x, stat_y, sw, stat_h, fill=C.canvas_soft, line=None,
                    radius_ratio=radius_for(sw, stat_h, 0.21))
        pad = Inches(0.25)
        add_text(s, x + pad, stat_y + pad, sw - pad * 2, Inches(0.3),
                 [(k, {"style": "eyebrow", "color": C.body})])
        add_text(s, x + pad, stat_y + pad + Inches(0.30),
                 sw - pad * 2, Inches(0.55),
                 [(v, {"style": "display_md", "color": C.ink,
                       "code": True})])
        add_text(s, x + pad, stat_y + pad + Inches(0.85),
                 sw - pad * 2, Inches(0.45),
                 [(sub, {"style": "body_sm", "color": C.body})])

    # below: 2 cards (wide format + scale)
    bot_y = stat_y + stat_h + Inches(0.30)
    bot_h = Inches(2.4)
    bot_w = (CONTENT_W - sgap) // 2

    # left — wide format
    add_rounded(s, sx0, bot_y, bot_w, bot_h, fill=C.canvas, line=C.hairline,
                line_w_pt=0.75,
                radius_ratio=radius_for(bot_w, bot_h, 0.21))
    pad = Inches(0.30)
    add_text(s, sx0 + pad, bot_y + pad, bot_w - pad * 2, Inches(0.32),
             [("WIDE FORMAT  ·  28 COLS",
               {"style": "eyebrow", "color": C.body})])
    add_text(s, sx0 + pad, bot_y + pad + Inches(0.36),
             bot_w - pad * 2, Inches(0.5),
             [("한 행 = 한 OA × 한 시간대",
               {"style": "display_sm", "color": C.ink})])

    cols_txt = [
        "기준일ID · 시간대구분",
        "집계구코드(13) · 행정동코드(8)",
        "총생활인구수",
        "남자 0-9세인구 ... 여자 70+세인구",
        "  (성연령 14 × 2 = 28 컬럼)",
    ]
    cy = bot_y + pad + Inches(0.85)
    for c in cols_txt:
        add_text(s, sx0 + pad, cy, bot_w - pad * 2, Inches(0.28),
                 [(c, {"style": "body_sm", "color": C.body, "code": True})])
        cy += Inches(0.28)

    # right — scale (emphasis dark)
    rx = sx0 + bot_w + sgap
    add_rounded(s, rx, bot_y, bot_w, bot_h, fill=C.primary, line=None,
                radius_ratio=radius_for(bot_w, bot_h, 0.21))
    add_text(s, rx + pad, bot_y + pad, bot_w - pad * 2, Inches(0.32),
             [("SCALE  ·  14 M 행/월",
               {"style": "eyebrow", "color": C.mute})])
    add_text(s, rx + pad, bot_y + pad + Inches(0.36),
             bot_w - pad * 2, Inches(0.7),
             [("31일 × 24시간 × 19,000 OA",
               {"style": "display_md", "color": C.on_dark,
                "code": True})])
    add_text(s, rx + pad, bot_y + pad + Inches(1.10),
             bot_w - pad * 2, Inches(1.0),
             [("→ 약 14 M 행 / 월\n"
               "→ 일 단위 스트리밍 read 가\n"
               "   메모리 안전",
               {"style": "body_sm", "color": C.mute})])


# ============================================================================
# slide 07 — LOCAL_PEOPLE 로드 (zip 스트리밍)
# ============================================================================

def slide_lp_load(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="LOCAL_PEOPLE  ·  LOAD",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("LP zip 스트리밍 — 12월 1일 한 파일만",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("zip 전체 풀지 말고 zipfile.open 으로 일별 CSV 만 read — 126 MB 만 메모리",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "lp_zip = os.path.join(RAW, 'seoul_living_pop',",
        "                      'LOCAL_PEOPLE_202412.zip')",
        "",
        "with zipfile.ZipFile(lp_zip) as z:",
        "    names = sorted(n for n in z.namelist() if n.endswith('.csv'))",
        "    print(f'zip 내 파일 : {len(names)}개 (일별)')",
        "",
        "    # 하나만 읽기 (12월 1일)",
        "    with z.open(names[0]) as f:",
        "        lp = pd.read_csv(f, encoding='cp949')",
        "",
        "print(f'한 파일 shape : {lp.shape}')",
        "print(f'  = 24h × 19,152 OA = {24 * 19152}')",
        "print(f'컬럼 (앞 5)   : {list(lp.columns[:5])}')",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(8.8), Inches(3.6),
                  code_lines, label="cell · zip stream",
                  font_pt=11, line_spacing=1.18)

    # output
    out_lines = [
        "zip 내 파일 : 31개 (일별)",
        "한 파일 shape : (459,648, 32)",
        "  = 24h × 19,152 OA = 459,648",
        "컬럼 (앞 5) : ['기준일ID', '시간대구분',",
        "             '집계구코드', '행정동코드', '총생활인구수']",
    ]
    add_code_cell(s, MARGIN_X, Inches(6.30),
                  Inches(8.8), Inches(0.95),
                  out_lines,
                  label="output", font_pt=10, line_spacing=1.18)

    # right: flow card
    nx = MARGIN_X + Inches(9.1)
    nw = SLIDE_W - MARGIN_X - nx
    add_card_content(s, nx, Inches(2.55), nw, Inches(4.7),
                     radius_in=0.21)
    pad = Inches(0.28)
    add_text(s, nx + pad, Inches(2.55) + pad,
             nw - pad * 2, Inches(0.32),
             [("FLOW", {"style": "eyebrow", "color": C.body})])

    flow_steps = [
        ("1", "ZipFile open",  "3.7 GB zip 을 풀지 않고 read"),
        ("2", "namelist()",    "31 일별 CSV 이름만 추출"),
        ("3", "z.open(name)",  "한 파일만 file-object 로 stream"),
        ("4", "read_csv(f, cp949)", "126 MB 만 메모리 — 한글 인코딩"),
    ]
    fy = Inches(2.55) + pad + Inches(0.45)
    for num, head, body in flow_steps:
        add_text(s, nx + pad, fy, Inches(0.35), Inches(0.6),
                 [(num, {"style": "display_md", "color": C.ink})])
        add_text(s, nx + pad + Inches(0.4), fy,
                 nw - pad * 2 - Inches(0.4), Inches(0.28),
                 [(head, {"style": "body_md_b", "color": C.ink,
                          "code": True})])
        add_text(s, nx + pad + Inches(0.4), fy + Inches(0.27),
                 nw - pad * 2 - Inches(0.4), Inches(0.7),
                 [(body, {"style": "body_sm", "color": C.body})])
        fy += Inches(0.95)


# ============================================================================
# slide 08 — LP 시간대 패턴 시각화
# ============================================================================

def slide_lp_pattern(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="LOCAL_PEOPLE  ·  HOURLY",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("LP 시간대 패턴 — 한 OA 24시간",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("종로구 OA 하나의 24시간 추이 — 새벽 vs 정오 vs 야간 비교",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "# 한 OA 의 24시간 총생활인구",
        "sample_cd = lp['집계구코드'].iloc[0]",
        "one_oa = lp[lp['집계구코드'] == sample_cd] \\",
        "           .sort_values('시간대구분')",
        "",
        "fig, ax = plt.subplots(figsize=(10, 4))",
        "ax.plot(one_oa['시간대구분'],",
        "        one_oa['총생활인구수'],",
        "        marker='o', color='steelblue')",
        "ax.set_xlabel('시간대 (0-23h)')",
        "ax.set_ylabel('생활인구 (명)')",
        "ax.set_title(f'OA {sample_cd} — 시간대별 생활인구')",
        "ax.grid(alpha=0.3); plt.show()",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(8.4), Inches(3.6),
                  code_lines, label="cell · hourly profile",
                  font_pt=11, line_spacing=1.18)

    out_lines = [
        "새벽 (3시)  :  812",
        "정오 (12시) : 1,540",
        "야간 (20시) : 1,205",
    ]
    add_code_cell(s, MARGIN_X, Inches(6.30),
                  Inches(8.4), Inches(0.95),
                  out_lines,
                  label="output", font_pt=10, line_spacing=1.20)

    # right: tip card (pattern semantics)
    nx = MARGIN_X + Inches(8.7)
    nw = SLIDE_W - MARGIN_X - nx
    add_card_content(s, nx, Inches(2.55), nw, Inches(4.7),
                     radius_in=0.21)
    pad = Inches(0.30)
    add_text(s, nx + pad, Inches(2.55) + pad,
             nw - pad * 2, Inches(0.32),
             [("PATTERN", {"style": "eyebrow", "color": C.body})])
    add_text(s, nx + pad, Inches(2.55) + pad + Inches(0.36),
             nw - pad * 2, Inches(0.7),
             [("시간대 패턴이\nOA 의 정체",
               {"style": "display_sm", "color": C.ink,
                "line_spacing": 1.25})])

    pat = [
        ("residential",  "새벽 ↑  ·  정오 ↓\n외곽 베드타운"),
        ("workplace",    "새벽 ↓  ·  정오 ↑\n강남·종로·여의도"),
        ("retail",       "정오/저녁 peak\n명동 · 홍대"),
    ]
    py = Inches(2.55) + pad + Inches(1.35)
    for k, v in pat:
        add_text(s, nx + pad, py, nw - pad * 2, Inches(0.30),
                 [(k, {"style": "body_md_b", "color": C.ink,
                       "code": True})])
        add_text(s, nx + pad, py + Inches(0.27),
                 nw - pad * 2, Inches(0.65),
                 [(v, {"style": "body_sm", "color": C.body})])
        py += Inches(0.95)


# ============================================================================
# slide 09 — 2016 vs 2025 OA 코드 체계 (concept)
# ============================================================================

def slide_oa_code_systems(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="OA CODE  ·  2016 vs 2025",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("두 OA 코드 체계 — 2016 vs 2025",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("LOCAL_PEOPLE 는 2016 (13자리)  ·  SGIS 통계는 2025 (14자리) — 공간 교차로 매핑",
               {"style": "lead", "color": C.body})])

    # left: 2 code-system cards
    lx = MARGIN_X
    ly = Inches(2.55)
    lw = Inches(7.4)

    # card A — 2016
    ah = Inches(2.05)
    add_rounded(s, lx, ly, lw, ah, fill=C.canvas_soft, line=None,
                radius_ratio=radius_for(lw, ah, 0.21))
    pad = Inches(0.32)
    add_text(s, lx + pad, ly + pad, lw - pad * 2, Inches(0.32),
             [("2016  ·  LOCAL_PEOPLE", {"style": "eyebrow", "color": C.body})])
    add_text(s, lx + pad, ly + pad + Inches(0.36),
             lw - pad * 2, Inches(0.7),
             [("TOT_REG_CD  ·  13 자리",
               {"style": "display_md", "color": C.ink, "code": True})])
    add_text(s, lx + pad, ly + pad + Inches(1.15),
             lw - pad * 2, Inches(0.5),
             [("LP 의 '집계구코드' 와 완전 일치  ·  sgis_oa_2016/ 폴리곤",
               {"style": "body_sm", "color": C.body})])

    # card B — 2025
    by = ly + ah + Inches(0.25)
    bh = Inches(2.05)
    add_rounded(s, lx, by, lw, bh, fill=C.primary, line=None,
                radius_ratio=radius_for(lw, bh, 0.21))
    add_text(s, lx + pad, by + pad, lw - pad * 2, Inches(0.32),
             [("2025  ·  SGIS 통계 표준", {"style": "eyebrow", "color": C.mute})])
    add_text(s, lx + pad, by + pad + Inches(0.36),
             lw - pad * 2, Inches(0.7),
             [("TOT_OA_CD  ·  14 자리",
               {"style": "display_md", "color": C.on_dark, "code": True})])
    add_text(s, lx + pad, by + pad + Inches(1.15),
             lw - pad * 2, Inches(0.6),
             [("oa_master 의 기본 키  ·  2016~2025 사이 ~50 OA 재구획",
               {"style": "body_sm", "color": C.mute})])

    # right: solution card (mapping)
    rx = lx + lw + Inches(0.30)
    rw = SLIDE_W - MARGIN_X - rx
    rh = ah + bh + Inches(0.25)
    add_card_content(s, rx, ly, rw, rh, radius_in=0.21)
    pad2 = Inches(0.30)
    add_text(s, rx + pad2, ly + pad2, rw - pad2 * 2, Inches(0.32),
             [("SOLUTION  ·  AREA-WEIGHT",
               {"style": "eyebrow", "color": C.body})])
    add_text(s, rx + pad2, ly + pad2 + Inches(0.36),
             rw - pad2 * 2, Inches(0.7),
             [("면적가중 매핑표\n+ disaggregate",
               {"style": "display_sm", "color": C.ink,
                "line_spacing": 1.25})])

    add_hairline(s, rx + pad2, ly + pad2 + Inches(1.45),
                 rw - pad2 * 2, color=C.hairline_soft)
    add_text(s, rx + pad2, ly + pad2 + Inches(1.55),
             rw - pad2 * 2, Inches(1.0),
             [("oa2016_to_oa2025\n.parquet",
               {"style": "body_md_b", "color": C.ink,
                "code": True, "line_spacing": 1.20})])
    add_text(s, rx + pad2, ly + pad2 + Inches(2.45),
             rw - pad2 * 2, Inches(1.2),
             [("· weight 합 = 1 per 2016 OA\n"
               "· LP × weight → 2025 단위로\n"
               "  disaggregate",
               {"style": "body_sm", "color": C.body})])


# ============================================================================
# slide 10 — 매핑표 미리보기 (code)
# ============================================================================

def slide_mapping_preview(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="OA CODE  ·  MAPPING",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("2016 → 2025 매핑표 — 면적가중",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("한 2016 OA 가 여러 2025 OA 로 쪼개진 사례 확인 — 재구획 진단",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "mapping = pd.read_parquet(",
        "    os.path.join(DRV, 'oa2016_to_oa2025.parquet'))",
        "print(f'매핑 행 수 : {len(mapping):,}')",
        "print(f'컬럼       : {list(mapping.columns)}')",
        "print(mapping.head(5))",
        "",
        "# 한 2016 OA 가 여러 2025 OA 로 쪼개진 사례",
        "multi = (mapping.groupby('TOT_REG_CD').size()",
        "                .sort_values(ascending=False))",
        "n_one  = (multi == 1).sum()",
        "n_many = (multi > 1).sum()",
        "print(f'2016 → 2025 단일 매칭 : {n_one}'",
        "      f'  ({n_one/len(multi)*100:.1f}%)')",
        "print(f'재구획 (1→여러)       : {n_many}')",
        "print(f'최대 분할             : {multi.max()} 개')",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(8.8), Inches(4.7),
                  code_lines, label="cell · mapping preview",
                  font_pt=11, line_spacing=1.18)

    # right: schema card
    nx = MARGIN_X + Inches(9.1)
    nw = SLIDE_W - MARGIN_X - nx
    add_card_content(s, nx, Inches(2.55), nw, Inches(4.7),
                     radius_in=0.21)
    pad = Inches(0.30)
    add_text(s, nx + pad, Inches(2.55) + pad,
             nw - pad * 2, Inches(0.32),
             [("MAPPING SCHEMA", {"style": "eyebrow", "color": C.body})])

    cols = [
        ("TOT_REG_CD",  "13",  "2016 OA 코드"),
        ("TOT_OA_CD",   "14",  "2025 OA 코드"),
        ("weight",      "f",   "면적 비율 (0~1)"),
    ]
    sy = Inches(2.55) + pad + Inches(0.40)
    for name, typ, desc in cols:
        add_text(s, nx + pad, sy, Inches(1.5), Inches(0.32),
                 [(name, {"style": "body_md_b", "color": C.ink,
                          "code": True})])
        add_text(s, nx + pad + Inches(1.50), sy,
                 Inches(0.5), Inches(0.32),
                 [(typ, {"style": "body_sm", "color": C.body,
                         "code": True})])
        add_text(s, nx + pad, sy + Inches(0.28),
                 nw - pad * 2, Inches(0.5),
                 [(desc, {"style": "body_sm", "color": C.body})])
        sy += Inches(0.78)

    # invariant pill
    inv_y = Inches(5.55)
    inv_h = Inches(0.46)
    add_rounded(s, nx + pad, inv_y, nw - pad * 2, inv_h,
                fill=C.primary, line=None, radius_ratio=0.5)
    add_text(s, nx + pad, inv_y, nw - pad * 2, inv_h,
             [("INVARIANT  ·  Σ weight = 1",
               {"style": "caption_b", "color": C.on_dark,
                "letter_spacing_pt": 0.8})],
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, nx + pad, inv_y + inv_h + Inches(0.18),
             nw - pad * 2, Inches(0.55),
             [("→ 한 2016 OA 의 인구 합이\n   2025 OA 들로 정확히 분배",
               {"style": "body_sm", "color": C.body})])


# ============================================================================
# slide 11 — oa_master 구성
# ============================================================================

def slide_oa_master_layout(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="OA MASTER  ·  LAYOUT",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("oa_master.parquet — 19,097 × 150",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("위의 모든 raw 를 합친 결과.  직접 만들면 ~8분 → 이미 만들어진 것을 로드",
               {"style": "lead", "color": C.body})])

    # 5 group cards across
    row_y = Inches(2.6)
    card_h = Inches(2.5)
    gap = Inches(0.18)
    card_w = (CONTENT_W - gap * 4) // 5
    groups = [
        ("KEY · GEOM",     "3 + 2",
         "TOT_OA_CD\nADM_CD\nblock_id\ngeometry\narea_m2"),
        ("인구·가구·주택",  "~ 20",
         "pop_total\nhh_count\nho_total\naging_idx\nhh_avg_size"),
        ("성연령 81종",    "81",
         "in_age_M00_04\nin_age_M05_09\n  ...\nin_age_F70_74\nin_age_F75p"),
        ("LP 시간 풀 6",   "6",
         "lp_pool_resident_02_05\nlp_pool_morning_07_10\nlp_pool_midday_11_15\nlp_pool_evening_18_21\nlp_pool_late_22_01\nlp_pool_24h"),
        ("LP 성연령 28",   "28",
         "lp_demo_M00_09\nlp_demo_M10_19\n  ...\nlp_demo_F70p"),
    ]
    for i, (head, n, body) in enumerate(groups):
        x = MARGIN_X + (card_w + gap) * i
        # third one (성연령 81종) gets emphasis as the biggest group
        if i == 2:
            add_rounded(s, x, row_y, card_w, card_h, fill=C.primary, line=None,
                        radius_ratio=radius_for(card_w, card_h, 0.21))
            head_c, body_c, num_c = C.on_dark, C.mute, C.on_dark
        else:
            add_rounded(s, x, row_y, card_w, card_h, fill=C.canvas_soft, line=None,
                        radius_ratio=radius_for(card_w, card_h, 0.21))
            head_c, body_c, num_c = C.ink, C.body, C.ink
        pad = Inches(0.22)
        add_text(s, x + pad, row_y + pad, card_w - pad * 2, Inches(0.32),
                 [(head, {"style": "eyebrow", "color": body_c})])
        add_text(s, x + pad, row_y + pad + Inches(0.32),
                 card_w - pad * 2, Inches(0.55),
                 [(n, {"style": "display_md", "color": num_c})])
        add_text(s, x + pad, row_y + pad + Inches(0.95),
                 card_w - pad * 2, card_h - pad * 2 - Inches(0.95),
                 [(body, {"style": "body_sm", "color": body_c,
                          "code": True, "line_spacing": 1.30})])

    # bottom: TOT_OA_CD anatomy (compact bar)
    ant_y = row_y + card_h + Inches(0.30)
    ant_h = Inches(1.45)
    add_rounded(s, MARGIN_X, ant_y, CONTENT_W, ant_h, fill=C.canvas, line=C.hairline,
                line_w_pt=0.75,
                radius_ratio=radius_for(CONTENT_W, ant_h, 0.21))
    pad = Inches(0.32)
    add_text(s, MARGIN_X + pad, ant_y + pad,
             Inches(4), Inches(0.32),
             [("TOT_OA_CD  ·  14 DIGITS",
               {"style": "eyebrow", "color": C.body})])
    add_text(s, MARGIN_X + pad, ant_y + pad + Inches(0.32),
             Inches(5), Inches(0.4),
             [("11010530010001",
               {"style": "display_md", "color": C.ink, "code": True})])
    # right side: slicing examples
    add_text(s, MARGIN_X + Inches(6.6), ant_y + pad,
             Inches(6), Inches(0.32),
             [("SLICING  ·  groupby key",
               {"style": "eyebrow", "color": C.body})])

    slice_tab = [
        ("[:5]", "시군구  ·  자치구"),
        ("[:8]", "행정동 (SGIS 8자리)"),
    ]
    sy = ant_y + pad + Inches(0.32)
    for sl, label in slice_tab:
        add_text(s, MARGIN_X + Inches(6.6), sy, Inches(1.0), Inches(0.30),
                 [(sl, {"style": "body_md_b", "color": C.ink, "code": True})])
        add_text(s, MARGIN_X + Inches(7.6), sy, Inches(5), Inches(0.30),
                 [(label, {"style": "body_sm", "color": C.body})])
        sy += Inches(0.34)


# ============================================================================
# slide 12 — oa_master 로드 + 컬럼 그룹 (code)
# ============================================================================

def slide_oa_master_load(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="OA MASTER  ·  LOAD",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("oa_master 로드 + 컬럼 그룹 확인",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("gpd.read_parquet 한 줄.  컬럼 prefix 로 5개 그룹 셀프 점검",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "oa_master = gpd.read_parquet(",
        "    os.path.join(DRV, 'oa_master.parquet'))",
        "print(f'oa_master shape : {oa_master.shape}')",
        "",
        "print('주요 컬럼 그룹:')",
        "for prefix, label in [",
        "    ('pop_',    '인구 통계'),",
        "    ('hh_',     '가구'),",
        "    ('ho_',     '주택'),",
        "    ('in_age_', '성연령 81종'),",
        "    ('lp_pool_','LP 시간 풀'),",
        "    ('lp_demo_','LP 성연령 28종'),",
        "]:",
        "    cols = [c for c in oa_master.columns",
        "                  if c.startswith(prefix)]",
        "    print(f'  {label:<12} ({prefix}*) : {len(cols)}개')",
        "",
        "print(f'결측 (pop_total) : '",
        "      f'{oa_master[\"pop_total\"].isna().sum()} OA')",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(8.8), Inches(4.7),
                  code_lines, label="cell · load + group check",
                  font_pt=11, line_spacing=1.18)

    # right: output card (mocked expected output)
    nx = MARGIN_X + Inches(9.1)
    nw = SLIDE_W - MARGIN_X - nx
    add_rounded(s, nx, Inches(2.55), nw, Inches(4.7),
                fill=C.canvas_soft, line=None,
                radius_ratio=radius_for(nw, Inches(4.7), 0.21))
    pad = Inches(0.30)
    add_text(s, nx + pad, Inches(2.55) + pad,
             nw - pad * 2, Inches(0.32),
             [("EXPECTED OUTPUT", {"style": "eyebrow", "color": C.body})])

    out_lines = [
        "oa_master shape : (19097, 150)",
        "",
        "주요 컬럼 그룹:",
        "  인구 통계    (pop_*)     :  6개",
        "  가구         (hh_*)      :  9개",
        "  주택         (ho_*)      :  7개",
        "  성연령 81종  (in_age_*)  : 81개",
        "  LP 시간 풀   (lp_pool_*) :  6개",
        "  LP 성연령 28 (lp_demo_*) : 28개",
        "",
        "결측 (pop_total) : 117 OA",
    ]
    oy = Inches(2.55) + pad + Inches(0.45)
    for line in out_lines:
        add_text(s, nx + pad, oy, nw - pad * 2, Inches(0.28),
                 [(line, {"style": "body_sm", "color": C.ink,
                          "code": True})])
        oy += Inches(0.30)


# ============================================================================
# slide 13 — 인구 분포 choropleth (code)
# ============================================================================

def slide_pop_choropleth(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="OA MASTER  ·  POP CHOROPLETH",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("OA 거주 인구 분포 — choropleth",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("19,097 OA × pop_total — vmax 는 q95 로 클리핑해 outlier 영향 줄임",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "fig, ax = plt.subplots(figsize=(13, 11))",
        "oa_master.plot(",
        "    column='pop_total', cmap='YlOrRd', ax=ax,",
        "    vmin=0, vmax=oa_master['pop_total'].quantile(0.95),",
        "    linewidth=0, legend=True,",
        "    legend_kwds={'label': 'pop_total (명)',",
        "                 'shrink': 0.6},",
        "    missing_kwds={'color': 'lightgray'})",
        "ax.set_title('서울 19,097 OA — 거주 인구 (2024 SGIS)')",
        "ax.set_axis_off(); plt.show()",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(8.8), Inches(3.4),
                  code_lines, label="cell · pop choropleth",
                  font_pt=11, line_spacing=1.18)

    # right: pattern notes
    nx = MARGIN_X + Inches(9.1)
    nw = SLIDE_W - MARGIN_X - nx
    add_card_content(s, nx, Inches(2.55), nw, Inches(4.7),
                     radius_in=0.21)
    pad = Inches(0.28)
    add_text(s, nx + pad, Inches(2.55) + pad,
             nw - pad * 2, Inches(0.32),
             [("PATTERN NOTES", {"style": "eyebrow", "color": C.body})])

    notes = [
        ("quantile(0.95)",
         "최대값이 outlier 면 대부분의 OA 색이 묻힘\n→ q95 로 vmax clip 해 contrast 살림"),
        ("linewidth=0",
         "19,097 폴리곤 — 외곽선 켜면 검정으로 묻힘"),
        ("missing_kwds",
         "pop_total NaN OA (~117개) 를 lightgray 로\n시각 구분 — 빈 곳 ≠ 0 명"),
        ("legend shrink",
         "기본 legend 가 너무 크면 본 지도가 좁아짐"),
    ]
    ny = Inches(2.55) + pad + Inches(0.45)
    for k, v in notes:
        add_text(s, nx + pad, ny, nw - pad * 2, Inches(0.30),
                 [(k, {"style": "body_md_b", "color": C.ink, "code": True})])
        add_text(s, nx + pad, ny + Inches(0.28),
                 nw - pad * 2, Inches(0.85),
                 [(v, {"style": "body_sm", "color": C.body})])
        ny += Inches(1.00)

    # below code: insight pill
    ins_y = Inches(6.10)
    ins_h = Inches(1.15)
    add_rounded(s, MARGIN_X, ins_y, Inches(8.8), ins_h, fill=C.primary,
                line=None, radius_ratio=radius_for(Inches(8.8), ins_h, 0.21))
    add_text(s, MARGIN_X + Inches(0.36), ins_y + Inches(0.22),
             Inches(8.0), Inches(0.32),
             [("INSIGHT", {"style": "eyebrow", "color": C.mute})])
    add_text(s, MARGIN_X + Inches(0.36), ins_y + Inches(0.50),
             Inches(8.0), Inches(0.65),
             [("외곽 (강동·강서·노원) 대형 단지 ↑  ·  도심 (종로·중구) 낮음 — workplace",
               {"style": "body_md", "color": C.on_dark})])


# ============================================================================
# slide 14 — LP 시간 풀 — 새벽 vs 정오 (code)
# ============================================================================

def slide_lp_pool_compare(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="OA MASTER  ·  LP POOL COMPARE",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("LP 시간 풀 — 새벽 vs 정오",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("같은 OA 라도 시간에 따라 인구 다름 — bed-town(02-05) vs CBD(11-15) 패턴 비교",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "fig, axes = plt.subplots(1, 2, figsize=(18, 9))",
        "vmax = oa_master['lp_pool_24h'].quantile(0.95)",
        "",
        "oa_master.plot(column='lp_pool_resident_02_05',",
        "    cmap='Blues', ax=axes[0],",
        "    vmin=0, vmax=vmax, linewidth=0, legend=True,",
        "    legend_kwds={'shrink': 0.6},",
        "    missing_kwds={'color': 'lightgray'})",
        "axes[0].set_title('새벽 (02-05시) — 베드타운 패턴')",
        "axes[0].set_axis_off()",
        "",
        "oa_master.plot(column='lp_pool_midday_11_15',",
        "    cmap='Reds', ax=axes[1],",
        "    vmin=0, vmax=vmax, linewidth=0, legend=True,",
        "    legend_kwds={'shrink': 0.6},",
        "    missing_kwds={'color': 'lightgray'})",
        "axes[1].set_title('정오 (11-15시) — CBD 패턴')",
        "axes[1].set_axis_off()",
        "plt.show()",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(8.8), Inches(4.7),
                  code_lines, label="cell · resident vs midday",
                  font_pt=10, line_spacing=1.18)

    # right: 2 contrast cards
    nx = MARGIN_X + Inches(9.1)
    nw = SLIDE_W - MARGIN_X - nx
    ch = Inches(2.25)

    # residential card
    add_rounded(s, nx, Inches(2.55), nw, ch, fill=C.canvas_soft, line=None,
                radius_ratio=radius_for(nw, ch, 0.21))
    pad = Inches(0.28)
    add_text(s, nx + pad, Inches(2.55) + pad, nw - pad * 2, Inches(0.32),
             [("새벽  ·  02-05", {"style": "eyebrow", "color": C.body})])
    add_text(s, nx + pad, Inches(2.55) + pad + Inches(0.32),
             nw - pad * 2, Inches(0.55),
             [("BED-TOWN",
               {"style": "display_md", "color": C.ink})])
    add_text(s, nx + pad, Inches(2.55) + pad + Inches(0.95),
             nw - pad * 2, Inches(1.0),
             [("강동 · 강서 · 노원 · 도봉\n"
               "거주지 인구가 가장 진하게 보임",
               {"style": "body_sm", "color": C.body})])

    # midday card (emphasis)
    my = Inches(2.55) + ch + Inches(0.20)
    add_rounded(s, nx, my, nw, ch, fill=C.primary, line=None,
                radius_ratio=radius_for(nw, ch, 0.21))
    add_text(s, nx + pad, my + pad, nw - pad * 2, Inches(0.32),
             [("정오  ·  11-15", {"style": "eyebrow", "color": C.mute})])
    add_text(s, nx + pad, my + pad + Inches(0.32),
             nw - pad * 2, Inches(0.55),
             [("CBD",
               {"style": "display_md", "color": C.on_dark})])
    add_text(s, nx + pad, my + pad + Inches(0.95),
             nw - pad * 2, Inches(1.0),
             [("강남 · 종로 · 여의도\n"
               "workplace 신호 — Lec3 회귀 feature",
               {"style": "body_sm", "color": C.mute})])


# ============================================================================
# slide 15 — 자치구별 인구 집계 (slicing)
# ============================================================================

def slide_sgg_aggregation(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="OA MASTER  ·  AGGREGATION",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("자치구별 인구 집계 — 코드 위계 활용",
               {"style": "display_xl", "color": C.ink})])
    add_text(s, MARGIN_X, Inches(1.75), Inches(12), Inches(0.5),
             [("TOT_OA_CD[:5] = 자치구 코드.  groupby 한 줄로 OA → 자치구 집계",
               {"style": "lead", "color": C.body})])

    code_lines = [
        "oa_master['sgg_cd'] = (oa_master['TOT_OA_CD']",
        "                          .astype(str).str[:5])",
        "",
        "sgg_pop = (oa_master",
        "           .groupby('sgg_cd')['pop_total']",
        "           .agg(['sum', 'count'])",
        "           .rename(columns={'sum':  'pop_total',",
        "                            'count':'oa_count'})",
        "           .sort_values('pop_total', ascending=False))",
        "",
        "print('자치구별 인구·OA 수 (top 10):')",
        "print(sgg_pop.head(10))",
        "print(f'서울 총인구 : '",
        "      f'{sgg_pop[\"pop_total\"].sum()/1e6:.2f}M')",
    ]
    add_code_cell(s, MARGIN_X, Inches(2.55),
                  Inches(8.0), Inches(3.7),
                  code_lines, label="cell · sgg aggregation",
                  font_pt=11, line_spacing=1.18)

    out_lines = [
        "sgg_cd        pop_total   oa_count",
        "11680 (강남)     545,210        882",
        "11650 (서초)     410,830        660",
        "11440 (마포)     370,210        612",
        "...",
        "서울 총인구 : 9.32M",
    ]
    add_code_cell(s, MARGIN_X, Inches(6.40),
                  Inches(8.0), Inches(1.10),
                  out_lines,
                  label="output", font_pt=10, line_spacing=1.20)

    # right: slicing reference
    nx = MARGIN_X + Inches(8.3)
    nw = SLIDE_W - MARGIN_X - nx
    add_card_content(s, nx, Inches(2.55), nw, Inches(4.7),
                     radius_in=0.21)
    pad = Inches(0.28)
    add_text(s, nx + pad, Inches(2.55) + pad,
             nw - pad * 2, Inches(0.32),
             [("TOT_OA_CD SLICING",
               {"style": "eyebrow", "color": C.body})])
    add_text(s, nx + pad, Inches(2.55) + pad + Inches(0.32),
             nw - pad * 2, Inches(0.55),
             [("11010530010001",
               {"style": "display_sm", "color": C.ink, "code": True})])

    slices = [
        ("[:2]",   "시도",      "11"),
        ("[:5]",   "시군구",     "11010"),
        ("[:8]",   "행정동(SGIS)", "11010530"),
        ("[:14]",  "OA 일련",    "11010530010001"),
    ]
    sy = Inches(2.55) + pad + Inches(1.10)
    for sl, label, ex in slices:
        add_text(s, nx + pad, sy, Inches(1.0), Inches(0.30),
                 [(sl, {"style": "body_md_b", "color": C.ink, "code": True})])
        add_text(s, nx + pad + Inches(1.05), sy, Inches(1.5), Inches(0.30),
                 [(label, {"style": "body_sm", "color": C.body})])
        add_text(s, nx + pad + Inches(2.55), sy,
                 nw - pad * 2 - Inches(2.55), Inches(0.30),
                 [(ex, {"style": "body_sm", "color": C.body, "code": True})])
        sy += Inches(0.42)

    add_hairline(s, nx + pad, sy + Inches(0.05),
                 nw - pad * 2, color=C.hairline_soft)
    add_text(s, nx + pad, sy + Inches(0.15),
             nw - pad * 2, Inches(0.9),
             [("→ 자치구 25 · 행정동 426 (SGIS) 까지\n   groupby 한 줄로 집계",
               {"style": "body_sm", "color": C.body})])


# ============================================================================
# slide 16 — summary + next
# ============================================================================

def slide_summary(prs, idx, total):
    s = new_blank_slide(prs)
    add_page_chrome(s, eyebrow="SUMMARY  ·  RECAP",
                    page_no=idx, total_pages=total, deck=DECK_LABEL)

    add_text(s, MARGIN_X, Inches(1.0), Inches(11), Inches(0.7),
             [("정리 — Lecture 2 에서 챙길 5가지",
               {"style": "display_xl", "color": C.ink})])

    row_y = Inches(2.2)
    card_w = (CONTENT_W - Inches(0.2) * 4) // 5
    card_h = Inches(2.6)
    cards = [
        ("1", "SGIS",          "long format · pivot 한 줄로 wide.\nN/A 는 NaN (≠ 0)"),
        ("2", "LOCAL_PEOPLE",  "KT 시그널링 시간대 인구.\nzip 안 일별 CSV stream"),
        ("3", "두 코드 체계",   "2016 (13) vs 2025 (14).\n면적가중 매핑이 매개"),
        ("4", "oa_master",     "19,097 OA × 150 cols\n키 + 인구 + LP + 성연령"),
        ("5", "코드 위계",     "TOT_OA_CD[:5/:8]\ngroupby 한 줄 = sgg / admdong"),
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

    # bottom: black promo card → Lec 3
    pr_y = Inches(5.20)
    pr_h = Inches(1.7)
    add_card_dark(s, MARGIN_X, pr_y, CONTENT_W, pr_h, radius_in=0.21)
    pad = Inches(0.5)
    add_text(s, MARGIN_X + pad, pr_y + pad, Inches(3), Inches(0.32),
             [("NEXT  ·  LECTURE 03",
               {"style": "eyebrow", "color": C.mute})])
    add_text(s, MARGIN_X + pad, pr_y + pad + Inches(0.3),
             Inches(9), Inches(0.7),
             [("통행 발생 (Trip Generation) — admdong P_i / A_j 회귀 추정",
               {"style": "display_md", "color": C.on_dark})])
    # pill button on right
    btn_w = Inches(2.4); btn_h = Inches(0.55)
    btn_x = MARGIN_X + CONTENT_W - pad - btn_w
    btn_y = pr_y + (pr_h - btn_h) // 2
    add_rounded(s, btn_x, btn_y, btn_w, btn_h, fill=C.canvas, line=None,
                radius_ratio=0.5)
    add_text(s, btn_x, btn_y, btn_w, btn_h,
             [("Open Lecture 03  →", {"style": "button", "color": C.ink})],
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)


# ============================================================================
# main
# ============================================================================

def build():
    prs = Presentation()
    setup_169(prs)

    slides = [
        slide_title,
        slide_raw_to_derived,
        slide_imports,
        slide_sgis_structure,
        slide_sgis_pivot,
        slide_lp_intro,
        slide_lp_load,
        slide_lp_pattern,
        slide_oa_code_systems,
        slide_mapping_preview,
        slide_oa_master_layout,
        slide_oa_master_load,
        slide_pop_choropleth,
        slide_lp_pool_compare,
        slide_sgg_aggregation,
        slide_summary,
    ]
    total = len(slides)

    for i, fn in enumerate(slides, start=1):
        fn(prs, i, total)

    out = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "slides", "02_oa_master.pptx",
    )
    prs.save(out)
    print(f"OK · {total} slides · {out}")
    return out


if __name__ == "__main__":
    build()
