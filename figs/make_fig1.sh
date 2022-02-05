cd ../utils/
python generate_subsets.py tracings REN_SketchFab_fossil2_000_RGBND.png
python generate_subsets.py drawings_registered REN_SketchFab_fossil2_000_RGBND.png
python visualize_progression.py tracings REN_SketchFab_fossil2_000_RGBND.png
python visualize_progression.py drawings_registered REN_SketchFab_fossil2_000_RGBND.png
cd ../figs/
python make_fig1.py
