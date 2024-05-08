# pifcap - A GUI for fast RAW image capture on Raspberry Pi
This software allows you to capture RAW images on Raspberry Pi in a fast way. Typical application is Lucky Imaging in astro photography.

***This software is still in development. It may not be functional. Please wait for the released version before you send issue reports.***

## Installation
The software is made for raspberry Pi with a recent OS (Bullseye or Bookworm). 

Some packages need to be installed with `sudo apt`:
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
- Some Python packages require matching versions of system libraries. They must be installed with `sudo apt`:
```commandline
sudo apt install python3-pip libcamera-apps python3-picamera2 python3-pyqt5 python3-pyqtgraph python3-astropy python3-numpy python3-venv
```

The Raspberry Pi OS "Bullseye" still allowed to install system wide with `sudo pip install pifcap`.
Since "Bookworm" a virtual environment is required to install non-system Python packages. Trying to install
`pifcap` without a virtual environment will fail with `error: externally-managed-environment`.

Run the following on a command line to install `pifcap`in a virtual environment called `venv_pifcap`:
```commandline
python3 -m venv --system-site-packages ~/venv_pifcap
source ~/venv_pifcap/bin/activate
pip install --upgrade pip
pip install pifcap
```


## Some hints when you get trouble
The Python packages `picamera2`, `numpy`, and ` astropy` MUST be installed with `sudo apt install`.
You MUST NOT update them with `pip`. When you get errors related to these packages you can:
  1. Check directory `~/.local/lib/python3.9/site-packages` if it contains one of these packages. If yes delete them!
  2. Check if `pip list` shows different version numbers than `apt list` for these packages:
     ```commandline
     pip list | grep numpy
     apt list | grep numpy

     pip list | grep astropy
     apt list | grep astropy

     pip list | grep picamera2
     apt list | grep picamera2
     ```
     If you see different versions for a package remove it with `pip uninstall` and reinstall it with
     `sudo apt reinstall`.
  3. Remove and recreate the virtual environment.


## Uninstall
To remove `pifcap` from your Pi just delete the virtual environment:
```commandline
rm -rf ~/venv_pifcap
```

## Running

Before using `pifcap` you need to activate the virtual environment in the command window:
```commandline
source ~/venv_pifcap/bin/activate
```

You can start graphical user interface of the capture program with:
```commandline
pifcap
```


Images are stored in a proprietary format to minimize CPU load during capture. Conversion of the collected images to FITS format can be done with the command line program `pifcap2fits`. Run `pifcap2fits -h` to get help for the command options. For instance to convert all `pfc` files in the current directory to FITS do
```commandline
pifcap2fits "*.pfc"
```
Different to linux commands the file name specifier must be quoted!



