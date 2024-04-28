# pifcap - A GUI for fast RAW image capture on Raspberry Pi
This software allows you to capture RAW images on Raspberry Pi in a fast way. Typical application is Lucky Imaging in astro photography.

***This software is still in development. It may not be functional. Please wait for the released version before you send issue reports.***

## Installation
The software is made for raspberry Pi with a recent OS (Bullseye or Bookworm). 

Some packages need to be installed with apt-get:
- `libcamera` and `libcamera-apps` (if not already installed). You can test libcamera and the support
for your camera with: 
  ```commandline
  libcamera-hello --list-cameras
  ```
  You must be able to make RAW pictures in all modes. For instance `libcamera-hello` shows for the HQ camera:
  ```
  0 : imx477 [4056x3040] (/base/soc/i2c0mux/i2c@1/imx477@1a)
    Modes: 'SRGGB10_CSI2P' : 1332x990 [120.05 fps - (696, 528)/2664x1980 crop]
           'SRGGB12_CSI2P' : 2028x1080 [50.03 fps - (0, 440)/4056x2160 crop]
                             2028x1520 [40.01 fps - (0, 0)/4056x3040 crop]
                             4056x3040 [10.00 fps - (0, 0)/4056x3040 crop]
  ```
  and you must be able to run these commands without errors:
  ```commandline
  libcamera-still -r --mode 1332:990 --shutter 100000 --gain 1 --awbgains 1,1 --immediate -o test.jpg
  libcamera-still -r --mode 2028:1080 --shutter 100000 --gain 1 --awbgains 1,1 --immediate -o test.jpg
  libcamera-still -r --mode 2028:1520 --shutter 100000 --gain 1 --awbgains 1,1 --immediate -o test.jpg
  libcamera-still -r --mode 4056:3040 --shutter 100000 --gain 1 --awbgains 1,1 --immediate -o test.jpg
  ```
  Something with your libcamera or kernel driver installation will be wrong if this does not work.
- The Python packages `PyQt5`, `picamera2` and `numpy` must be installed. Typically they are already installed. If not you can install them with:
```commandline
sudo apt-get install python3-picamera2 p
```

To install `pifcap`in your system run
```commandline
sudo pip3 install pifcap

## Uninstall
For uninstalling `pifcap` do:
```commandline
sudo pip3 uninstall pifcap
```

## Running
You can start graphical user interface of the capture program with:
```commandline
pifcap
```
Images are stored in a proprietary format to minimize CPU load during capture. Conversion of the collected images to FITS format can be done with the command line program `pifcap2fits`. Run `pifcap2fits -h` to get help for the command options. For instance to convert all `pfc` files in the current directory to FITS do
```commandline
pifcap2fits "*.pfc"
```
Different to linux commands the file name specifier must be quoted.



