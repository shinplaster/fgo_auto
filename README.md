# FGO AUTO
This is an experimental Python script to automate quest iteration of Fate Grand Order(FGO) on Mac OS.
This script assumes that the target iOS device is connected to the Mac via "iPhone Mirroring".

## Usage
```
% python fgo_auto.py -h
usage: fgo_auto.py [-h] [-i ITERATION] [--debug] order_sheet

FGO AUTO: an automation script for FGO quest iteration

positional arguments:
  order_sheet           a file of FGO Auto order sheet

options:
  -h, --help            show this help message and exit
  -i ITERATION, --iteration ITERATION
                        Number of loop for the target quest
  --debug               DEBUG mode for development
```

## Dependent modules
```
pip install pyautoguit
pip install pywinctl
pip install opencv-python
pip install pyocr
pip install pyyaml

brew install tesseract
```
