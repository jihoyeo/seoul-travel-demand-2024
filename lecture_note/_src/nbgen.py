"""
nbgen.py — 강좌 노트북 빌더.

각 노트북 소스 (`_src/build_*.py`) 는 다음 패턴으로 작성한다:

    from nbgen import MD, CODE, write_notebook

    cells = [
        MD('# Title\n학습 목표 …'),
        CODE('import pandas as pd'),
        ...
    ]
    write_notebook(cells, '../notebooks/01_xxx.ipynb')

`MD`, `CODE` 는 단순히 (type, src) 튜플. 빌더는 `nbformat 4.5` 형식의
유효한 ipynb JSON 을 생성한다 (kernel: python3, no outputs).

사용 (lecture_note 디렉터리에서):
    python _src/build_01_spatial_data.py
    python _src/build_all.py        # 전부 한꺼번에
"""
import json, os, uuid

def MD(src):  return ('markdown', src)
def CODE(src): return ('code', src)

def _src_lines(text):
    """nbformat 은 source 를 줄 단위 리스트로 받음. 마지막 줄 제외 모든 줄에 \n 부착."""
    if not text:
        return []
    lines = text.split('\n')
    return [l + '\n' for l in lines[:-1]] + [lines[-1]]

def _cell(kind, src):
    base = {
        'cell_type': kind,
        'id': uuid.uuid4().hex[:12],
        'metadata': {},
        'source': _src_lines(src),
    }
    if kind == 'code':
        base['execution_count'] = None
        base['outputs'] = []
    return base

def write_notebook(cells, out_path):
    nb = {
        'cells': [_cell(k, s) for (k, s) in cells],
        'metadata': {
            'kernelspec': {
                'display_name': 'Python 3',
                'language': 'python',
                'name': 'python3',
            },
            'language_info': {
                'codemirror_mode': {'name': 'ipython', 'version': 3},
                'file_extension': '.py',
                'mimetype': 'text/x-python',
                'name': 'python',
                'nbconvert_exporter': 'python',
                'pygments_lexer': 'ipython3',
                'version': '3.11',
            },
        },
        'nbformat': 4,
        'nbformat_minor': 5,
    }
    out_path = os.path.abspath(out_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    print(f'  wrote {out_path}  ({len(cells)} cells)')


def write_slide(cells, out_path):
    """슬라이드 markdown 출력 — MD 셀은 그대로, CODE 셀은 ```python``` fence.

    노트북과 동일 cells 에서 파생되므로 코드·서술 동기화 자동.
    슬라이드 끝의 마지막 CODE 셀 (보통 검증용 print) 은 슬라이드 가독성을 위해 생략.
    """
    out = []
    for i, (kind, src) in enumerate(cells):
        if kind == 'markdown':
            out.append(src.rstrip())
        else:  # code
            # 슬라이드 마지막의 검증용 print 셀은 생략
            is_last_verification = (i == len(cells) - 1) and src.strip().startswith('print(')
            if is_last_verification:
                continue
            out.append('```python\n' + src.rstrip() + '\n```')
        out.append('')   # 빈 줄
    text = '\n'.join(out).rstrip() + '\n'

    out_path = os.path.abspath(out_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f'  wrote {out_path}  ({len(cells)} cells → slide)')


def write_both(cells, notebook_path, slide_path):
    """노트북 + 슬라이드 한 번에. build_*.py 의 __main__ 에서 호출."""
    write_notebook(cells, notebook_path)
    write_slide(cells, slide_path)
