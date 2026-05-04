"""Render the 3 new Phase 6 figures (Wave 4 Plan 05)."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location('mf', 'scripts/make_figures.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

logs_dir = Path('logs')
output_dir = Path('figures')
output_dir.mkdir(parents=True, exist_ok=True)

m.render_d12_cross_model_heatmap_v6(logs_dir, output_dir)
print('OK: rendered figures/d12_cross_model_heatmap_v6.png')

m.render_d12_undefended_v6(logs_dir, output_dir)
print('OK: rendered figures/d12_undefended_v6.png')

m.render_d03_arms_race_v6(logs_dir, output_dir)
print('OK: rendered figures/d03_arms_race_v6.png')

print('OK: 3 new figures rendered to figures/')
