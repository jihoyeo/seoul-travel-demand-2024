"""Run all build_*.py scripts to regenerate every notebook."""
import os, runpy, glob

BASE = os.path.dirname(os.path.abspath(__file__))

scripts = sorted(glob.glob(os.path.join(BASE, 'build_*.py')))
scripts = [s for s in scripts if os.path.basename(s) != 'build_all.py']

for s in scripts:
    print(f'\\n=== {os.path.basename(s)} ===')
    runpy.run_path(s, run_name='__main__')
print('\\nAll notebooks rebuilt.')
