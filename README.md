# zooniverse-pipeline

# Prerequisites

```
pip3 install panoptes-client
pip3 install Pillow
pip3 install opencv-python
pip3 install matplotlib
pip3 install piexif
```

#

# Run

```
python3 fluke_analysis_opencv.py <image_dir> [-z <zooniverse_dir>]
```

... where <zooniverse_dir> should have the "whales-as-individuals-classifications.csv" file. Default is "/opt/zooniverse/wai".
