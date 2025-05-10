# BatchImageProcessor

A modular Python framework for batch processing images and videos.

## Installation

```bash
pip install -e .
```

## Content Engine with Aesthetic Score Tracking

The Content Engine processes videos to extract aesthetically pleasing segments and tracks the aesthetic scores for each output file.

### Usage

```bash
python examples/content_engine.py --input /path/to/input --output /path/to/output
```

Optional parameters:
- `--scores /path/to/scores.json`: Specify where to save the score mapping
- `--threshold 5.5`: Set minimum aesthetic score (0-10)
- `--sample-rate 1.0`: Set frames per second to analyze
- `--min-duration 2.0`: Set minimum segment duration in seconds
- `--no-combine`: Don't combine adjacent good segments

### Programmatic API

```python
from examples.content_engine import ContentEngine

engine = ContentEngine(
    input_dir="/path/to/videos",
    output_dir="/path/to/output",
    scores_output_path="/path/to/scores.json",
    threshold=5.5,
    sample_rate=1.0,
    min_segment_duration=2.0,
    combine_adjacent_segments=True
)

# Process videos and get the score mapping
scores_dict = engine.process_videos()
```

The resulting scores.json file contains a dictionary mapping output filepaths to their aesthetic scores:

```json
{
  "/path/to/output/video1.mp4": 6.78,
  "/path/to/output/video2.mp4": 7.23,
  "/path/to/output/video3.mp4": 5.91
}
```
