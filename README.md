# Tracing Versus Freehand for Evaluating Computer-Generated Drawings

Zeyu Wang, Sherry Qiu, Nicole Feng, Holly Rushmeier, Leonard McMillan, Julie Dorsey

SIGGRAPH 2021

[[Paper]](https://graphics.cs.yale.edu/sites/default/files/tracing-vs-freehand_0.pdf)
[[Browser]](http://tracer.cs.yale.edu:8000/tracing-vs-freehand/)

![teaser](teaser.jpg)

We will release our drawing dataset and analysis code in this repository.

The dataset consists of 1,498 tracings and freehand drawings by 110 participants for 100 image prompts. Our drawings are registered to the prompts and include vector-based timestamped strokes collected via stylus input.

More to come. Stay tuned!

## Data

Raw JSON data: [tracings](http://tracer.cs.yale.edu:8000/tracing-vs-freehand/data/tracings.json), [freehand drawings](http://tracer.cs.yale.edu:8000/tracing-vs-freehand/data/drawings.json), [registered freehand drawings](http://tracer.cs.yale.edu:8000/tracing-vs-freehand/data/drawings_registered.json).

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
