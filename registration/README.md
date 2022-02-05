## Registering freehand drawings to tracing density

In our paper, we registered freehand drawings to their image prompt before we conduct our analysis. This is achieved by maximizing the pixel correlation of drawing patches between a freehand drawing and the tracing density using ITK.

Some freehand drawings are easy to register without any supervision using our coarse-to-fine registration framework. Running `bash register_unlabeled.sh` will register all these freehand drawings.

Other freehand drawings are harder to register due to bad initializations. We manually labeled fiducials in freehand drawings and their image prompt to establish initial correspondences, stored in `fiducials.json`. Running `bash register_labeled.sh` will register all these freehand drawings.

Input:
- Image density maps are stored in `../data/density/`.
- Freehand drawings are stored in `../data/png/drawings/`.

Output:
- Generated visuals are stored in `visual_unlabeled/` and `visual_labeled/`.
- Final transforms are stored in `transform_unlabeled/` and `transform_labeled/`.
