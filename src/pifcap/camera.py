"""
CameraControl class
"""
import os.path
import shutil
import pickle
import numpy as np
import io
import re
import threading
import time
import datetime
from PyQt5 import QtCore


from picamera2 import Picamera2
from libcamera import controls, Rectangle
from . import pifcap_image

settings = {'name': 'camera hardware', 'type': 'group', 'children': [
    {
        'name': 'do hardware specific adjustments', 'type': 'bool', 'value': True,
        'tip': 'do adjustments for specific camera hardware',
    },
    {
        'name': 'force pixel size', 'type': 'bool', 'value': False, 'children': [
        {
            'name': 'X size', 'type': 'float', 'value': 1.0, 'suffix': ' µm', 'limits': [0.0, 10000.0],
        },
        {
            'name': 'Y size', 'type': 'float', 'value': 1.0, 'suffix': ' µm', 'limits': [0.0, 10000.0],
        },
    ]
    },
    {
        'name': 'force camera restarts', 'type': 'list', 'values': ['auto', 'yes', 'no'], 'value': 'auto',
        'tip': 'force camera restart after each exposure',
    },
]}


class CameraSettings:
    """exposure settings
    """

    def __init__(self):
        self._RawModes = list()
        self._selected_RawMode_idx = None
        self._is_newMode = True
        self._camera_controls = {
            "ExposureTime": 0.01,
            "AnalogueGain": 1.0,
            # disable all automatic regulations
            "AeEnable": False,
            "NoiseReductionMode": controls.draft.NoiseReductionModeEnum.Off,
            "AwbEnable": False,
            "ColourGains": (2.0, 2.0),  # to compensate the 2 G pixel in Bayer pattern
        }
        self._is_newControls = True
        # make thread safe
        self._AccessLock = QtCore.QMutex()


    @property
    def available_RawModes(self):
        self._AccessLock.lock()
        ret = self._RawModes
        self._AccessLock.unlock()
        return ret

    @available_RawModes.setter
    def available_RawModes(self, rms):
        self._AccessLock.lock()
        self._RawModes = rms
        self._AccessLock.unlock()
        self.set_RawModeFromIdx(0)

    @property
    def RawMode(self):
        self._AccessLock.lock()
        rm = self._RawModes[self._selected_RawMode_idx]
        self._AccessLock.unlock()
        return rm

    def set_RawModeFromIdx(self, idx):
        assert idx >= 0
        assert idx < len(self._RawModes)
        self._AccessLock.lock()
        if idx != self._selected_RawMode_idx:
            self._selected_RawMode_idx = idx
            self._is_newMode = True
            self._camera_controls["ExposureTime"] = min(
                self._camera_controls["ExposureTime"],
                self._RawModes[self._selected_RawMode_idx]["max_ExposureTime"]
            )
            self._camera_controls["ExposureTime"] = max(
                self._camera_controls["ExposureTime"],
                self._RawModes[self._selected_RawMode_idx]["min_ExposureTime"]
            )
            self._camera_controls["AnalogueGain"] = min(
                self._camera_controls["AnalogueGain"],
                self._RawModes[self._selected_RawMode_idx]["max_AnalogueGain"]
            )
            self._camera_controls["AnalogueGain"] = max(
                self._camera_controls["AnalogueGain"],
                self._RawModes[self._selected_RawMode_idx]["min_AnalogueGain"]
            )
            self._is_newControls = True
        self._AccessLock.unlock()

    @property
    def MaxExposureTime(self):
        self._AccessLock.lock()
        t = self._RawModes[self._selected_RawMode_idx]["max_ExposureTime"]
        self._AccessLock.unlock()
        return t / 1e6

    @property
    def MinExposureTime(self):
        self._AccessLock.lock()
        t = self._RawModes[self._selected_RawMode_idx]["min_ExposureTime"]
        self._AccessLock.unlock()
        return t / 1e6

    @property
    def MaxGain(self):
        self._AccessLock.lock()
        g = self._RawModes[self._selected_RawMode_idx]["max_AnalogueGain"]
        self._AccessLock.unlock()
        return g

    @property
    def MinGain(self):
        self._AccessLock.lock()
        g = self._RawModes[self._selected_RawMode_idx]["min_AnalogueGain"]
        self._AccessLock.unlock()
        return g

    @property
    def Binning(self):
        self._AccessLock.lock()
        b = self._RawModes[self._selected_RawMode_idx]["binning"]
        self._AccessLock.unlock()
        return b

    @property
    def ExposureTime(self):
        self._AccessLock.lock()
        t = self._camera_controls["ExposureTime"] / 1e6
        self._AccessLock.unlock()
        return t

    @ExposureTime.setter
    def ExposureTime(self, t):
        t_usec = int(round(1e6 * t))
        self._AccessLock.lock()
        t_usec = min(
            t_usec,
            self._RawModes[self._selected_RawMode_idx]["max_ExposureTime"]
        )
        t_usec = max(
            t_usec,
            self._RawModes[self._selected_RawMode_idx]["min_ExposureTime"]
        )
        if t_usec != self._camera_controls["ExposureTime"]:
            self._camera_controls["ExposureTime"] = t_usec
            self._is_newControls = True
        self._AccessLock.unlock()

    @property
    def Gain(self):
        self._AccessLock.lock()
        g = self._camera_controls["AnalogueGain"]
        self._AccessLock.unlock()
        return g

    @Gain.setter
    def Gain(self, g):
        self._AccessLock.lock()
        g = min(
            g,
            self._RawModes[self._selected_RawMode_idx]["max_AnalogueGain"]
        )
        g = max(
            g,
            self._RawModes[self._selected_RawMode_idx]["min_AnalogueGain"]
        )
        if g != self._camera_controls["AnalogueGain"]:
            self._camera_controls["AnalogueGain"] = g
            self._is_newControls = True
        self._AccessLock.unlock()

    @property
    def is_newControls(self):
        self._AccessLock.lock()
        ret = self._is_newControls
        self._AccessLock.unlock()
        return ret

    def reset_newControls(self):
        self._AccessLock.lock()
        self._is_newControls = False
        self._AccessLock.unlock()

    @property
    def is_newMode(self):
        self._AccessLock.lock()
        ret = self._is_newMode
        self._AccessLock.unlock()
        return ret

    def reset_newMode(self):
        self._AccessLock.lock()
        self._is_newMode = False
        self._AccessLock.unlock()

    @property
    def camera_controls(self):
        self._AccessLock.lock()
        ret = self._camera_controls
        self._AccessLock.unlock()
        return ret

    def __str__(self):
        return f'CameraSettings: RawMode={self.RawMode}, CameraControls={self.camera_controls}'

    def __repr__(self):
        return str(self)


class CameraControl(QtCore.QThread):
    """camera control and exposure thread
    """

    sigImage = QtCore.pyqtSignal(dict)
    sigRecordingFinished = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.parent = parent
        # reset states
        self.picam2 = None
        self.CameraSettings = CameraSettings()
        self.CamProps = dict()
        self.needs_Restarts = False
        # exposure loop control
        self.Sig_ActionExit = threading.Event()  # abort and exit exposure loop
        self.Sig_CaptureDone = threading.Event()
        # exposure loop in separate thread
        self.Sig_ActionExit.clear()
        self.Sig_CaptureDone.clear()
        # handshake with GUI
        self.Sig_GiveImage = threading.Event()
        self.Sig_GiveImage.clear()
        # image recorder
        self._Folder = parent.Settings.get('recording', 'default folder')
        self._Comment = ""
        self._Prefix = ""
        self._FrameType = "Light"
        self._ImagesToRecord = 0
        self._ImagesRecorded = 0
        self._Record = False
        self._SettingsLock = QtCore.QMutex()
        self._Ext = ".pfc"

    def get_Cameras(self):
        """return list of available cameras"""
        cameras = Picamera2.global_camera_info()
        # use Id as unique camera identifier
        return [c["Model"] for c in cameras]

    def openCamera(self, idx: int):
        """open camera with given index idx
        """
        self.parent.log_Info("Opening camera.")
        self.picam2 = Picamera2(idx)
        # read camera properties
        self.CamProps = self.picam2.camera_properties
        self.parent.log_Info(f'Camera properties: {self.CamProps}')
        # force properties with values from config file
        if self.parent.Settings.get('camera hardware', 'force pixel size') or ("UnitCellSize" not in self.CamProps):
            self.parent.log_Info("Forcing UnitCellSize from program settings.")
            self.CamProps["UnitCellSize"] = (
                self.parent.Settings.get('camera hardware', 'force pixel size', 'X size'),
                self.parent.Settings.get('camera hardware', 'force pixel size', 'Y size'),
            )
        # some libcamera versions return a libcamera.Rectangle here!
        if type(self.CamProps["PixelArrayActiveAreas"][0]) is Rectangle:
            Rect = self.CamProps["PixelArrayActiveAreas"][0]
            self.CamProps["PixelArrayActiveAreas"] = (Rect.x, Rect.y, Rect.width, Rect.height)
        # raw modes
        self.CameraSettings.available_RawModes = self.getRawCameraModes()
        # some cameras need a restart after each exposure
        force_Restart = self.parent.Settings.get('camera hardware', 'force camera restarts')
        if force_Restart == "yes":
            self.parent.log_Info("Application setting forces camera restarts.")
            self.needs_Restarts = True
        elif force_Restart == "no":
            self.parent.log_Info("Application setting enabled camera restarts as needed.")
            self.needs_Restarts = False
        else:
            # "auto":
            self.needs_Restarts = self.CamProps["Model"] in ["imx290", "imx519"]
        # start exposure loop
        self.Sig_ActionExit.clear()
        self.start()

    def is_Open(self):
        """return camera state
        """
        return (self.picam2 is not None) and self.isRunning()

    def closeCamera(self):
        """close camera
        """
        self.parent.log_Info('Closing camera.')
        # stop exposure loop
        if self.isRunning():
            self.Sig_ActionExit.set()
            self.wait()  # wait until exposure loop exits
        # close picam2
        if self.picam2 is not None:
            if self.picam2.started:
                self.picam2.stop_()
            self.picam2.close()
        self.picam2 = None
        # reset states
        self.CamProps = dict()
        self.CameraSettings = CameraSettings()


    def reconfigure_Camera(self, RawMode, DoFastExposure=True):
        self.parent.log_Info(f'reconfiguring camera')
        config = self.picam2.create_still_configuration(
            queue=DoFastExposure,
            buffer_count=2 if DoFastExposure else 1  # need at least 2 buffer for queueing
        )
        # we do not need the main stream and configure it to smaller size to save memory
        config["main"]["size"] = (240, 190)
        # configure raw stream
        config["raw"] = {
            "size": RawMode["size"],
            "format": RawMode["camera_format"]
        }
        # optimize (align) configuration: small changes to some main stream configurations
        # (for instance: size) will fit better to hardware
        self.picam2.align_configuration(config)
        # set still configuration
        self.picam2.configure(config)

    def getRawCameraModes(self):
        """get list of usable raw camera modes
        """
        sensor_modes = self.picam2.sensor_modes
        raw_modes = []
        for sensor_mode in sensor_modes:
            # sensor_mode is dict
            # it must have key "format" (usually a packed data format) and can have
            # "unpacked" (unpacked data format)
            if "unpacked" not in sensor_mode.keys():
                sensor_format = sensor_mode["format"]
            else:
                sensor_format = sensor_mode["unpacked"]
            # packed data formats are not supported
            if sensor_format.endswith("_CSI2P"):
                self.parent.log_Warn(f'Raw mode not supported: {sensor_mode}!')
                continue
            # only monochrome and Bayer pattern formats are supported
            is_monochrome = re.match("R[0-9]+", sensor_format)
            is_bayer = re.match("S[RGB]{4}[0-9]+", sensor_format)
            if not (is_monochrome or is_bayer):
                self.parent.log_Warn(f'Raw mode not supported: {sensor_mode}!')
                continue
            #
            size = sensor_mode["size"]
            # adjustments for cameras:
            #   * zero- or garbage-filled columns
            #   * raw modes with binning or subsampling
            true_size = size
            binning = (1, 1)
            if self.parent.Settings.get('camera hardware', 'do hardware specific adjustments'):
                if self.CamProps["Model"] == 'imx477':
                    if size == (1332, 990):
                        true_size = (1332, 990)
                        binning = (2, 2)
                    elif size == (2028, 1080):
                        true_size = (2024, 1080)
                        binning = (2, 2)
                    elif size == (2028, 1520):
                        true_size = (2024, 1520)
                        binning = (2, 2)
                    elif size == (4056, 3040):
                        true_size = (4056, 3040)
                    else:
                        self.parent.log_Warn(f'Unsupported frame size {size} for imx477!')
                elif self.CamProps["Model"] == 'ov5647':
                    if size == (640, 480):
                        binning = (4, 4)
                    elif size == (1296, 972):
                        binning = (2, 2)
                    elif size == (1920, 1080):
                        pass
                    elif size == (2592, 1944):
                        pass
                    else:
                        self.parent.log_Warn(f'Unsupported frame size {size} for ov5647!')
                elif self.CamProps["Model"].startswith("imx708"):
                    if size == (1536, 864):
                        binning = (2, 2)
                    elif size == (2304, 1296):
                        binning = (2, 2)
                    elif size == (4608, 2592):
                        pass
                    else:
                        self.parent.log_Warn(f'Unsupported frame size {size} for imx708!')
            # add to list of raw formats
            raw_mode = {
                "label": f'{size[0]}x{size[1]} {sensor_format[1:5] if is_bayer else "mono"} {sensor_mode["bit_depth"]}bit',
                "size": size,
                "true_size": true_size,
                "camera_format": sensor_format,
                "bit_depth": sensor_mode["bit_depth"],
                "binning": binning,
            }
            self.reconfigure_Camera(raw_mode)
            ExposureTimeLimits = self.picam2.camera_controls['ExposureTime']
            AnalogueGainLimits = self.picam2.camera_controls['AnalogueGain']
            self.parent.log_Debug(f'Raw mode "{raw_mode["label"]}": ExposureTimeLimits={ExposureTimeLimits}, AnalogueGainLimits={AnalogueGainLimits}')
            raw_mode["min_ExposureTime"] = 0.0 if ExposureTimeLimits[0] is None else ExposureTimeLimits[0]
            raw_mode["max_ExposureTime"] = \
                1e6 if (ExposureTimeLimits[1] is None) or (ExposureTimeLimits[1] < ExposureTimeLimits[0]) \
                    else ExposureTimeLimits[1]
            raw_mode["min_AnalogueGain"] = 0.0 if AnalogueGainLimits[0] is None else AnalogueGainLimits[0]
            raw_mode["max_AnalogueGain"] = \
                250 if (AnalogueGainLimits[1] is None) or (AnalogueGainLimits[1] < AnalogueGainLimits[0]) \
                    else AnalogueGainLimits[1]
            raw_modes.append(raw_mode)
        # sort list of raw formats by size and bit depth in descending order
        raw_modes.sort(key=lambda k: k["size"][0] * k["size"][1] * 100 + k["bit_depth"], reverse=True)
        return raw_modes

    def getProp(self, name):
        """return camera properties
        """
        return self.CamProps[name]

    def log_FrameInformation(self, array, metadata, format):
        """write frame information to log

        Args:
            array: raw frame data
            metadata: frame metadata
            format: format string
        """
        if self.parent.config.getboolean("driver", "log_FrameInformation", fallback=False):
            if array.ndim == 2:
                arr = array.view(np.uint16)
                BitUsages = list()
                for b in range(15, -1, -1):
                    BitSlice = (arr & (1 << b)) != 0
                    BitUsage = BitSlice.sum() / arr.size
                    BitUsages.append(BitUsage)
                BitUsages = [f'{bu:.1e}' for bu in BitUsages]
                self.parent.log_Info(f'Frame format: {format}, shape: {array.shape} {array.dtype}, bit usages: (MSB) {" ".join(BitUsages)} (LSB)')
            else:
                self.parent.log_Info(f'Frame format: {format}, shape: {array.shape} {array.dtype}')
            self.parent.log_Info(f'Frame metadata: {metadata}')

    def set_RecordingSettings(self, Folder, Prefix, Comment, ImagesToRecord, FrameType):
        self._SettingsLock.lock()
        self._Folder = Folder
        self._Prefix = Prefix
        self._Comment = Comment
        self._ImagesToRecord = ImagesToRecord
        self._FrameType = FrameType
        self._SettingsLock.unlock()

    def Recording(self, Record):
        self._SettingsLock.lock()
        self._Record = Record
        if Record:
            self._ImagesRecorded = 0
        self._SettingsLock.unlock()

    def run(self):
        """exposure loop

        Made to run in a separate thread.
        """
        DoFastExposure = True
        while True:
            if self.Sig_ActionExit.is_set():
                # exit exposure loop
                self.picam2.stop_()
                return
            # picam2 needs to be open!
            if self.picam2 is None:
                raise RuntimeError("trying to make an exposure without camera opened")
            # need a camera stop/start when something has changed on camera configuration
            if self.CameraSettings.is_newMode or self.needs_Restarts:
                if self.picam2.started:
                    #self.parent.log_Info(f'Stopping camera for deeper reconfiguration.')
                    self.picam2.stop_()
                # change of DoFastExposure needs a configuration change
                self.CameraSettings.reset_newMode()
                self.reconfigure_Camera(RawMode=self.CameraSettings.RawMode, DoFastExposure=DoFastExposure)
            # changing exposure time or analogue gain can be done with camera running
            if self.CameraSettings.is_newControls:
                # change camera controls
                self.CameraSettings.reset_newControls()
                self.picam2.set_controls(self.CameraSettings.camera_controls)
            # start camera if not already running
            if not self.picam2.started:
                self.picam2.start()
                #self.parent.log_Info(f'Camera started.')
            # last chance to exit or abort before doing exposure
            if self.Sig_ActionExit.is_set():
                # exit exposure loop
                self.picam2.stop_()
                return
            # get (non-blocking!) frame and meta data
            self.Sig_CaptureDone.clear()  # set by on_CaptureFinished callback
            ExpectedEndOfExposure = time.time() + self.CameraSettings.ExposureTime
            job = self.picam2.capture_arrays(["raw"], wait=False, signal_function=self.on_CaptureFinished)
            PollingPeriod_s = 0.2
            while ExpectedEndOfExposure - time.time() > PollingPeriod_s:
                # allow to close camera
                if self.Sig_ActionExit.is_set():
                    # exit exposure loop
                    self.picam2.stop_()
                    return
                # allow exposure to finish earlier than expected (for instance when in fast exposure mode)
                if self.Sig_CaptureDone.is_set():
                    break
                time.sleep(PollingPeriod_s)
            # get frame and its metadata
            (array, ), metadata = self.picam2.wait(job)
            DateEnd = datetime.datetime.now(datetime.timezone.utc)
            #self.parent.log_Info('got exposed frame')
            # last chance to exit or abort before sending frame
            if self.Sig_ActionExit.is_set():
                # exit exposure loop
                self.picam2.stop_()
                return
            if not DoFastExposure:
                # in normal exposure mode the camera needs to be started with exposure command
                self.picam2.stop()
            # save image
            metadata = {
                k: metadata.get(k, None) 
                for k in [
                    'SensorBlackLevels', 'Lux', 'FrameDuration', 'DigitalGain',
                    'AnalogueGain', 'ScalerCrop', 'ExposureTime'
                ]
            }
            metadata["DateEnd"] = DateEnd
            metadata["FrameType"] = self._FrameType
            metadata["CameraModel"] = self.CamProps["Model"]
            metadata["UnitCellSize"] = self.CamProps["UnitCellSize"]
            metadata["Binning"] = self.CameraSettings.Binning
            self.on_Image(
                array=array, metadata=metadata, 
                format=self.picam2.camera_configuration()["raw"]["format"]
            )


    def on_CaptureFinished(self, Job):
        """callback function for capture done
        """
        self.Sig_CaptureDone.set()

    def on_Image(self, array, metadata, format):
        self._SettingsLock.lock()
        Img = pifcap_image.Image(array=array, metadata=metadata, format=format, comment=self._Comment)
        Record = self._Record
        ImagesRemain = self._ImagesToRecord - self._ImagesRecorded
        Folder = self._Folder
        self._SettingsLock.unlock()
        if Record and (ImagesRemain > 0):
            TimeStamp = datetime.datetime.now().strftime("%y%m%dT%H%M%S%f")[:16]
            self._SettingsLock.lock()
            FileName = os.path.join(Folder, f'{self._Prefix}-{TimeStamp}{self._Ext}')
            self._ImagesRecorded += 1
            if self._ImagesRecorded >= self._ImagesToRecord:
                self.sigRecordingFinished.emit()
                self._Record = False
            self._SettingsLock.unlock()
            Img.save(filename=FileName)
        disc_total, disc_used, disc_free = shutil.disk_usage(Folder)
        disc_free_images = disc_free // Img.estimate_FileSize()
        # send preview image to GUI
        if self.Sig_GiveImage.is_set():
            self.sigImage.emit({
                "array": array,
                "format": self.picam2.camera_configuration()["raw"]["format"],
                "metadata": metadata,
                "RecordingInfos": {
                    "ImagesRecorded": self._ImagesRecorded,
                    "disc_free": disc_free,
                    "disc_free_images": disc_free_images,
                },
            })
            self.Sig_GiveImage.clear()
