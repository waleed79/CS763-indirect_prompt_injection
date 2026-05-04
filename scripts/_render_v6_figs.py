import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location('mf', 'scripts/make_figures.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
logs_dir = Path('logs')
output_dir = Path('figures')
m.render_d12_cross_model_heatmap_v6(logs_dir, output_dir)
m.render_d12_undefended_v6(logs_dir, output_dir)
m.render_d03_arms_race_v6(logs_dir, output_dir)
print('OK: 3 figures re-rendered')
