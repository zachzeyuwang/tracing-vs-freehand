# Data Preparation for Analysis

Run the following commands in the terminal to prepare the dataset:

```
cd data
wget http://tracer.cs.yale.edu/tracing-vs-freehand/data/tracings.json
wget http://tracer.cs.yale.edu/tracing-vs-freehand/data/drawings.json
wget http://tracer.cs.yale.edu/tracing-vs-freehand/data/drawings_registered.json
wget http://tracer.cs.yale.edu/tracing-vs-freehand/data/images.zip
wget http://tracer.cs.yale.edu/tracing-vs-freehand/data/density.zip
wget http://tracer.cs.yale.edu/tracing-vs-freehand/data/png.zip
wget http://tracer.cs.yale.edu/tracing-vs-freehand/data/svg.zip
unzip '*.zip'
rm *.zip
```

This `data` folder should look like this:

```
data
├── README.md
├── drawings.json
├── drawings_registered.json
├── tracings.json
├── images
│   ├── *.png (100 items)
├── density
│   ├── *.png (100 items)
├── png
│   ├── drawings
│   │   ├── *.png (288 items)
│   ├── drawings_registered
│   │   ├── *.png (288 items)
│   └── tracings
│       ├── *.png (1,210 items)
├── svg
│   ├── drawings
│   │   ├── *.svg (288 items)
│   ├── drawings_registered
│   │   ├── *.svg (288 items)
│   └── tracings
│       ├── *.svg (1,210 items)
```
