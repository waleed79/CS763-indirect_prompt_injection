"""Re-render the 6 figures that go into figures/final/ and copy them there."""
import shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import make_figures as mf

logs = Path("logs")
out  = Path("figures")
final = Path("figures/final")

targets = ["fig2", "fig3", "fig4", "fig5_v6", "fig5_und", "fig1_v6"]
name_map = {
    "fig2":     "fig2_utility_security.png",
    "fig3":     "fig3_loo_causal.png",
    "fig4":     "fig4_ratio_sweep.png",
    "fig5_v6":  "d12_cross_model_heatmap_v6.png",
    "fig5_und": "d12_undefended_v6.png",
    "fig1_v6":  "d03_arms_race_v6.png",
}

for key in targets:
    renderer = mf.ALL_RENDERERS[key]
    renderer(logs, out)
    fname = name_map[key]
    shutil.copy2(out / fname, final / fname)
    print(f"[OK] {key} -> figures/final/{fname}")
