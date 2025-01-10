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
fgo_auto.py depends on the following modules. please install these modules before use.
```
pip install pyautoguit
pip install pywinctl
pip install opencv-python
pip install pyocr
pip install pyyaml
```

## Install tesseract
fgo_auto.py is using tesseract OCR tool via pyocr. Please install tesseract and Japanese language file as follows:
```
brew install tesseract
cd /opt/homebrew/share/tessdata
curl -LO https://github.com/tesseract-ocr/tessdata_best/raw/main/jpn.traineddata
```
make sure the available languages are as follows:
```
% tesseract --list-langs
List of available languages in "/opt/homebrew/share/tessdata/" (4):
eng
jpn
osd
snum
```
