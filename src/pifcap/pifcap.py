"""
Fast Raspberry Pi image capturing software for Lucky Imaging.
"""

from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import os
import os.path
import numpy as np
import pyqtgraph as pg

from . import pifcap_ui
from . import camera
from . import settings
from . import autoexposure

__author__ = "Ronald Schreiber"
__copyright__ = "Copyright 2024"
__version__ = "v1.0.0"
__license__ = "MIT"
__title__ = f'pifcap {__version__}'

theme_selection = "Dark"  # "Dark", "Light"

# Interpret image data as row-major instead of col-major
pg.setConfigOptions(imageAxisOrder='row-major')


class MainWin(QtWidgets.QMainWindow):
    """
    pifcap main window.
    """

    def __init__(self, showDebugMessages=False):
        super(MainWin, self).__init__()
        # settings
        DefaultSettings = [
            {'name': 'saturation limit', 'type': 'int', 'value': 95, 'limits': [0, 100], 'suffix': ' %',
             'tip': 'mark saturated pixel when above % of full-scale',
            },
            autoexposure.settings,
            camera.settings,
            {'name': 'recording', 'type': 'group', 'children': [
                {
                    'name': 'default folder', 'type': 'str', 'value': os.path.join(os.path.expanduser("~"), "Pictures"),
                    'tip': 'default folder to store images',
                },
            ]},
        ]
        self.Settings = settings.SettingsDialog(parent=self, settings=DefaultSettings)
        self.Settings.load_QSettings()
        # GUI
        pg.setConfigOption('background', pg.mkColor(100, 0, 0))
        self.showDebugMessages = showDebugMessages
        self.ui = pifcap_ui.Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle(__title__)
        self.ui.plainTextEdit_Log.setMaximumBlockCount(100)
        self.ui.pushButton_Settings.clicked.connect(self.on_Settings_clicked)
        self.ui.groupBox_CameraSettings.setEnabled(False)
        self.ui.pushButton_StartRec.setEnabled(False)
        self.ui.comboBox_Camera.setEnabled(True)
        #
        self.ui.ImageView_Preview.setLevels(0, 2**16 - 1)
        self.ui.ImageView_Preview.ui.roiBtn.hide()
        self.ui.ImageView_Preview.ui.menuBtn.hide()
        # saturated pixel highlight
        self.SaturatedPixelImage = pg.ImageItem()
        self.SaturatedPixelImage.setZValue(65000)
        self.ui.ImageView_Preview.addItem(self.SaturatedPixelImage)
        #
        self.ImageFolder = self.Settings.get('recording', 'default folder')
        # camera
        self.Cam = camera.CameraControl(parent=self)
        self.Cam.sigImage.connect(self.on_Image)
        self.Cam.sigRecordingFinished.connect(self.on_pushButton_StopRec_clicked)
        self.Cam.Sig_GiveImage.set()
        self.ui.comboBox_Camera.addItems(self.Cam.get_Cameras())
        # recording settings
        self.ui.lineEdit_ImageComment.textChanged.connect(self.on_RecordingSettingsChanged)
        self.ui.lineEdit_FileNamePrefix.textChanged.connect(self.on_RecordingSettingsChanged)
        self.ui.spinBox_nImagesToRecord.valueChanged.connect(self.on_RecordingSettingsChanged)
        self.ui.doubleSpinBox_TimeLapse.valueChanged.connect(self.on_RecordingSettingsChanged)
        self.ui.comboBox_FrameType.currentIndexChanged.connect(self.on_RecordingSettingsChanged)
        # preview image
        self.Img = None
        # exposure time optimization
        self.AutoExposure = autoexposure.AutoExposure(Settings=self.Settings)

    def add_LogMessage(self, Msg, Severity="INFO"):
        if Severity=="ERROR":
            Html = '<font color="red">ERROR: %s</font>' % Msg
        elif Severity=="WARN":
            Html = '<font color="orange">WARN: %s</font>' % Msg
        elif (Severity=="DEBUG"):
            if self.showDebugMessages:
                Html = '<font color="yellow">DBG: %s</font>' % Msg
            else:
                return
        else: # INFO
            #Html = '<font color="black">%s</font>' % Msg
            Html = Msg
        self.ui.plainTextEdit_Log.appendHtml(Html)
        self.ui.statusbar.showMessage(Msg)
        self.ui.plainTextEdit_Log.ensureCursorVisible()

    def log_Error(self, Msg):
        self.add_LogMessage(Msg, "ERROR")

    def log_Warn(self, Msg):
        self.add_LogMessage(Msg, "WARN")

    def log_Debug(self, Msg):
        self.add_LogMessage(Msg, "DEBUG")

    def log_Info(self, Msg):
        self.add_LogMessage(Msg, "INFO")

    @QtCore.pyqtSlot()
    def closeEvent(self, event):
        self.add_LogMessage("entering closeEvent", Severity="DEBUG")
        self.Cam.closeCamera()
        #self.Settings.save_QSettings()  # FIXME: activate this!
        # proceed with close
        event.accept()

    def on_Settings_clicked(self):
        self.Settings.show()

    @QtCore.pyqtSlot()
    def on_pushButton_ConnectDisconnect_clicked(self):
        if self.Cam.is_Open():
            self.Cam.closeCamera()
            self.ui.pushButton_ConnectDisconnect.setText("connect")
            #self.ui.comboBox_RawMode.clear()
            self.ui.groupBox_CameraSettings.setEnabled(False)
            self.ui.pushButton_StartRec.setEnabled(False)
            self.ui.comboBox_Camera.setEnabled(True)
        else:
            self.Cam.openCamera(self.ui.comboBox_Camera.currentIndex())
            self.ui.comboBox_Camera.setEnabled(False)
            self.ui.comboBox_RawMode.clear()
            self.ui.comboBox_RawMode.addItems([rm["label"] for rm in self.Cam.CameraSettings.available_RawModes])
            self.ui.comboBox_RawMode.setCurrentIndex(0)
            self.ui.pushButton_ConnectDisconnect.setText("disconnect")
            self.ui.groupBox_CameraSettings.setEnabled(True)
            self.ui.pushButton_StartRec.setEnabled(True)


    @QtCore.pyqtSlot(int)
    def on_comboBox_RawMode_currentIndexChanged(self, idx):
        if idx >= 0:
            self.Cam.CameraSettings.set_RawModeFromIdx(idx)
            self.ui.doubleSpinBox_Gain.setMaximum(self.Cam.CameraSettings.MaxGain)
            self.ui.doubleSpinBox_Gain.setMinimum(self.Cam.CameraSettings.MinGain)
            self.ui.doubleSpinBox_Gain.setValue(self.Cam.CameraSettings.Gain)
            self.ui.doubleSpinBox_ExposureTime.setMaximum(self.Cam.CameraSettings.MaxExposureTime)
            self.ui.doubleSpinBox_ExposureTime.setMinimum(self.Cam.CameraSettings.MinExposureTime)
            self.ui.doubleSpinBox_ExposureTime.setValue(self.Cam.CameraSettings.ExposureTime)


    @QtCore.pyqtSlot(float)
    def on_doubleSpinBox_ExposureTime_valueChanged(self, t):
        self.Cam.CameraSettings.ExposureTime = t

    @QtCore.pyqtSlot(float)
    def on_doubleSpinBox_Gain_valueChanged(self, g):
        self.Cam.CameraSettings.Gain = g

    @QtCore.pyqtSlot()
    def on_pushButton_Folder_clicked(self):
        ImageFolder = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Folder to store images..",
            self.ImageFolder
        )
        if ImageFolder != '':
            self.ImageFolder = ImageFolder
        self.on_RecordingSettingsChanged()

    def on_RecordingSettingsChanged(self):
        self.Cam.set_RecordingSettings(
            Folder=self.ImageFolder,
            Prefix=self.ui.lineEdit_FileNamePrefix.text(),
            Comment=self.ui.lineEdit_ImageComment.text(),
            ImagesToRecord=self.ui.spinBox_nImagesToRecord.value(),
            FrameType=self.ui.comboBox_FrameType.currentText(),
        )

    @QtCore.pyqtSlot(int)
    def on_checkBox_OptimizeExposure_stateChanged(self, state):
        if state:
            self.AutoExposure.init_optimize()

    @QtCore.pyqtSlot(dict)
    def on_Image(self, Img):
        self.ui.label_RecordingInfos.setText(
            f'{Img["RecordingInfos"]["disc_free"]/1024/1024:.0f} MiB (~{Img["RecordingInfos"]["disc_free_images"]} images) free'
        )
        self.ui.label_RecordedImageCounter.setText(f'{Img["RecordingInfos"]["ImagesRecorded"]} images saved')
        self.log_Debug(f'received image: {Img["format"]}, {Img["array"].shape}, {Img["array"].dtype}')
        self.log_Debug(f'received metadata: {Img["metadata"]}')
        self.Img = Img
        self.process_Image()
        # TODO: wie wird Aufnahme automatisch gestoppt?
        QtCore.QTimer.singleShot(100, self.request_NewImage)

    def request_NewImage(self):
        self.Cam.Sig_GiveImage.set()

    def process_Image(self):
        format = self.Img["format"]
        array = self.Img["array"]
        # we expect uncompressed format here
        if format.count("_") > 0:
            raise NotImplementedError(f'got unsupported raw image format {format}')
        if format[0] not in ["S", "R"]:
            raise NotImplementedError(f'got unsupported raw image format {format}')
        # Bayer or mono format
        if format[0] == "S":
            # Bayer pattern format
            BayerPattern = format[1:5]
            # FIXME: BayerPattern = self.parent.config.get("driver", "force_BayerOrder", fallback=BayerPattern)
            bit_depth = int(format[5:])
        else:
            # mono format
            BayerPattern = None
            bit_depth = int(format[1:])
        # left adjust if needed
        if bit_depth > 8:
            array = array.view(np.uint16)
        else:
            array = array.view(np.uint8)
        #
        # remove 0- or garbage-filled columns # TODO implement this?
        #true_size = self.present_CameraSettings.RawMode["true_size"]
        #array = array[0:true_size[1], 0:true_size[0]]
        # exposure time optimization
        if self.ui.checkBox_OptimizeExposure.isChecked():
            finished, newExposureTime = self.AutoExposure.do_optimize(
                array=array,
                ExposureTime=self.Img["metadata"]["ExposureTime"]/1e6,
                n_bits=bit_depth,
                MinExposureTime=self.ui.doubleSpinBox_ExposureTime.minimum(),
                MaxExposureTime=self.ui.doubleSpinBox_ExposureTime.maximum()
            )
            if finished:
                self.ui.checkBox_OptimizeExposure.setChecked(False)
            else:
                self.ui.doubleSpinBox_ExposureTime.setValue(newExposureTime)
        # color channels
        imgR = None
        imgG1 = None
        imgG2 = None
        imgB = None
        if BayerPattern is None:
            # mono format
            img = array
        else:
            BayerChannels = {
                "GBRG": {"G1": (0, 0), "B": (0, 1), "R": (1, 0), "G2": (1, 1)},
                "BGGR": {"B": (0, 0), "G1": (0, 1), "G2": (1, 0), "R": (1, 1)},
            }[BayerPattern]
            imgR = array[BayerChannels["R"][0]::2, BayerChannels["R"][1]::2]
            imgG1 = array[BayerChannels["G1"][0]::2, BayerChannels["G1"][1]::2]
            imgG2 = array[BayerChannels["G2"][0]::2, BayerChannels["G2"][1]::2]
            imgB = array[BayerChannels["B"][0]::2, BayerChannels["B"][1]::2]
            RawPreviewMode = self.ui.comboBox_RawPreviewMode.currentText()
            if RawPreviewMode == "luminance":
                img = (0.2126 * imgR + 0.7152 / 2 * imgG1 + 0.7152 / 2 * imgG2 + 0.0722 * imgB).astype(int)
            elif RawPreviewMode == "red":
                img = imgR
            elif RawPreviewMode == "green 1":
                img = imgG1
            elif RawPreviewMode == "green 2":
                img = imgG2
            elif RawPreviewMode == "blue":
                img = imgB
            else:
                raise NotImplementedError
        # preview rotation and flip
        Rot = self.ui.comboBox_PreviewRot.currentText()
        FlipH = self.ui.checkBox_PreviewFlipH.isChecked()
        FlipV = self.ui.checkBox_PreviewFlipV.isChecked()
        img = self.flipRotate_Image(img, Rot, FlipH, FlipV)
        # show preview image
        self.ui.ImageView_Preview.setImage(img, autoLevels=False,
                                            autoHistogramRange=False,
                                            #levelMode="rgb",
                                            autoRange=False,
                                            )
        # highlight saturated pixel
        if self.ui.checkBox_Saturation.isChecked():
            sat = np.zeros((img.shape[0], img.shape[1], 4), dtype=int)
            sat[:, :, 0] = 1  # pure red, full transparent
            satLim = (2**bit_depth) * self.Settings.get('saturation limit') / 100
            if BayerPattern is None:
                # mono image
                is_sat = img > satLim
            else:
                is_sat = (imgR > satLim) | (imgG1 > satLim) | (imgG2 > satLim) | (imgB > satLim)
            is_sat = self.flipRotate_Image(is_sat, Rot, FlipH, FlipV)
            sat[:, :, 3] = is_sat * 1  # saturated pixel get intransparent red
            self.SaturatedPixelImage.setImage(sat, levels=[[0, 1], [0, 1], [0, 1], [0, 1]])
        else:
            self.SaturatedPixelImage.clear()

    def flipRotate_Image(self, img, Rot, FlipH, FlipV):
        if Rot != "0deg":
            k = {"90deg": 3, "180deg": 2, "270deg": 1}[Rot]
            img = np.rot90(img, k=k)
        if FlipH:
            img = np.fliplr(img)
        if FlipV:
            img = np.flipud(img)
        return img

    @QtCore.pyqtSlot()
    def on_pushButton_StartRec_clicked(self):
        self.ui.pushButton_StopRec.setEnabled(True)
        self.ui.pushButton_StartRec.setEnabled(False)
        self.Cam.Recording(True)

    @QtCore.pyqtSlot()
    def on_pushButton_StopRec_clicked(self):
        self.Cam.Recording(False)
        self.ui.pushButton_StartRec.setEnabled(True)
        self.ui.pushButton_StopRec.setEnabled(False)




# Start Qt event loop unless running in interactive mode.
def main():
    import argparse
    parser = argparse.ArgumentParser(description=f'{__title__}, a fast Raspberry Pi image capturing software for Lucky Imaging.')
    parser.add_argument("-d", "--debug", action="store_true",
                        help="enable debug messages")
    args = parser.parse_args()
    # build application
    App = QtWidgets.QApplication(sys.argv)
    App.setOrganizationName("GeierSoft")
    App.setOrganizationDomain("Astro")
    App.setApplicationName("pifcap")
    #
    # copied from https://stackoverflow.com/questions/48256772/dark-theme-for-qt-widgets
    if theme_selection == 'Dark':
        App.setStyle("Fusion")
        #
        # # Now use a palette to switch to dark colors:
        dark_palette = QtGui.QPalette()
        dark_palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
        dark_palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
        dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(35, 35, 35))
        dark_palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
        dark_palette.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(25, 25, 25))
        dark_palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
        dark_palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
        dark_palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
        dark_palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
        dark_palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
        dark_palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
        dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
        dark_palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(35, 35, 35))
        dark_palette.setColor(QtGui.QPalette.Active, QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
        dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, QtCore.Qt.darkGray)
        dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, QtCore.Qt.darkGray)
        dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, QtCore.Qt.darkGray)
        dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Light, QtGui.QColor(53, 53, 53))
        App.setPalette(dark_palette)
    elif theme_selection == 'Light':
        App.setStyle("")
        pass
    else:
        pass
    #
    MainWindow = MainWin(showDebugMessages=args.debug)
    # MainWindow.resize(1400, 900)
    MainWindow.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        sys.exit(App.exec_())


if __name__ == '__main__':
    main()
