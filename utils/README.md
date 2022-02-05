## Utils

`python render_png_from_json.py` renders the tracings, freehand drawings, and registered freehand drawings in svg and png from the raw JSON data `../data/tracings.json`, `../data/drawings.json`, and `../data/drawings_registered.json`. Output will be stored in `../data/svg/` and `../data/png/`. If you downloaded the renderings already, this script will be skipped.

`python generate_subsets.py` splits each drawing into partial drawings based on temporal order, i.e., 2 minutes split into 5 equal segments. You can provide two more optional command line arguments `tracings|drawings_registered` and `IMAGE_FILENAME.png` to run this script for a specific image. Output will be stored in `subsets/`.

`python visualize_progression.py` visualize progression of tracing and freehand drawing by accumulating and superimposing partial drawings in `subsets/`. You can provide two more optional command line arguments `tracings|drawings_registered` and `IMAGE_FILENAME.png` to run this script for a specific image. Output will be stored in `progression/`.
