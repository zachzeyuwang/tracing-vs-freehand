# Tracing Versus Freehand for Evaluating Computer-Generated Drawings (SIGGRAPH 2021)

Zeyu Wang, Sherry Qiu, Nicole Feng, Holly Rushmeier, Leonard McMillan, Julie Dorsey

[[Paper]](https://graphics.cs.yale.edu/sites/default/files/tracing-vs-freehand_0.pdf)
[[Project]](https://zachzeyuwang.github.io/tracing-vs-freehand)

![teaser](teaser.jpg)

## Drawing Dataset

The dataset consists of 1,498 tracings and freehand drawings by 110 participants for 100 image prompts. Our drawings are registered to the prompts and include vector-based timestamped strokes collected via stylus input.

Instructions for data preparation can be found in the `data` folder. All code in this repository takes input from the `data` folder.

*Please right click the links below and "Save link as..." if it doesn't download automatically.*

[Image prompts](http://tracer.cs.yale.edu/tracing-vs-freehand/data/images.zip).

All rendered tracings and freehand drawings in [SVG](http://tracer.cs.yale.edu/tracing-vs-freehand/data/svg.zip) and [PNG](http://tracer.cs.yale.edu/tracing-vs-freehand/data/png.zip).

Raw JSON data: [tracings](http://tracer.cs.yale.edu/tracing-vs-freehand/data/tracings.json), [freehand drawings](http://tracer.cs.yale.edu/tracing-vs-freehand/data/drawings.json), [registered freehand drawings](http://tracer.cs.yale.edu/tracing-vs-freehand/data/drawings_registered.json).

JSON data format:
```
{
  // each prompt
  "image": {
    // each drawing
    "participant": [
      // each stroke
      {
        "path": string (Unix timestamp, x, y coordinates at each vertex separated by comma)
        "pressure": string (pressure value at each vertex separated by comma)
        "color": string (hex code, e.g., "#000000")
        "width": integer (stroke width on a 800x800 canvas)
        "opacity": float (alpha value from 0 to 1)
      }
      ...
    ]
    ...
  }
  ...
}
```

## Analysis Code

`utils/render_png_from_json.py` renders the drawings in png format from the raw JSON data.

More analysis code, including drawing registration, will be released once I finish tidying them up and writing documentation. If you need anything in particular, please feel free to reach out to me directly via email.

## Citation

The dataset and code are released for academic research use only under CC BY-NC-SA 4.0.

If you use the dataset or code for your research, please cite this paper:
```
@article{Wang:2021:Tracing,
  author = {Wang, Zeyu and Qiu, Sherry and Feng, Nicole and Rushmeier,  Holly and McMillan, Leonard and Dorsey, Julie},
  title = {Tracing Versus Freehand for Evaluating Computer-Generated Drawings},
  year = {2021},
  issue_date = {August 2021},
  publisher = {Association for Computing Machinery},
  address = {New York, NY, USA},
  volume = {40},
  number = {4},
  issn = {0730-0301},
  url = {https://doi.org/10.1145/3450626.3459819},
  doi = {10.1145/3450626.3459819},
  journal = {ACM Trans. Graph.},
  month = aug,
  numpages = {12},
  keywords = {sketch dataset, drawing process, stroke analysis}
}
```
