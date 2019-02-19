# zooniverse-pipeline

# Prerequisites

```
pip3 install panoptes-client
pip3 install Pillow
pip3 install opencv-python
pip3 install matplotlib
pip3 install piexif
```

# Run

## Crop Images Using Zooniverse Data

```
python3 fluke_analysis_opencv.py -f <zooniverse_csv_file> <image_dir>
```

The first time you run this it will take a little longer as it will create a file named "<zooniverse_csv_file_minus_ext>\_preprocessed.csv". Subsequent runs will use this file instead if it exists.

## Upload Images to Zooniverse Subject

```
python3 subject_uploader_fixed_resize.py -s <subject_name> <image_dir>
```

If subject already exists you will be prompted to make sure you want to upload more to this subject or not.
