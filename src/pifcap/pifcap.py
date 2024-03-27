"""
Fast Raspberry Pi image capturing software for Lucky Imaging.
"""

from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import pyqtgraph as pg

import pifcap_ui
import camera
import settings

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
            {'name': 'automatic exposure', 'type': 'group', 'children': [
                {
                    'name': 'target exposure', 'type': 'int', 'value': 80, 'limits': [1, 100], 'suffix': ' %',
                    'tip': 'exposure target in % of full-scale',
                },
                {
                    'name': 'allowed overexposed pixel', 'type': 'float', 'value': 1.0, 'limits': [0, 100], 'suffix': ' %',
                    'tip': '% of pixels allowed to be overexposed (for instance defective pixel)',
                },
            ]},
            {'name': 'camera hardware', 'type': 'group', 'childern': [
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
            ]},
            {'name': 'recording', 'type': 'group', 'childern': [
                {
                    'name': 'default folder', 'type': 'str', 'value': "~/Pictures",
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
        #
        self.ui.ImageView_Preview.setLevels(0, 255)
        self.ui.ImageView_Preview.ui.roiBtn.hide()
        self.ui.ImageView_Preview.ui.menuBtn.hide()
        # saturated pixel highlight
        self.SaturatedPixelImage = pg.ImageItem()
        self.SaturatedPixelImage.setZValue(65000)  # TODO: make this dependent on setting
        self.ui.ImageView_Preview.addItem(self.SaturatedPixelImage)
        #
        self.ImageFolder = self.Settings.get('recording', 'default folder')
        # camera
        self.Cam = camera.CameraControl(parent=self)
        self.Cam.sigImage.connect(self.on_Image)
        self.ui.comboBox_Camera.addItems(self.Cam.get_Cameras())
        # recording settings
        self.ui.lineEdit_ImageComment.textChanged.connect(self.on_RecordingSettingsChanged)
        self.ui.lineEdit_FileNamePrefix.textChanged.connect(self.on_RecordingSettingsChanged)
        self.ui.spinBox_nImagesToRecord.valueChanged.connect(self.on_RecordingSettingsChanged)
        self.ui.doubleSpinBox_TimeLapse.valueChanged.connect(self.on_RecordingSettingsChanged)

    def add_LogMessage(self, Msg, Severity="INFO"):
        if Severity=="ERROR":
            Html = '<font color="red">ERROR: %s</font>' % Msg
        elif Severity=="WARN":
            Html = '<font color="orange">WARN: %s</font>' % Msg
        elif (Severity=="DEBUG") and self.showDebugMessages:
            Html = '<font color="yellow">DBG: %s</font>' % Msg
        else:
            #Html = '<font color="black">%s</font>' % Msg
            Html = Msg
        self.ui.plainTextEdit_Log.appendHtml(Html)
        self.ui.statusbar.showMessage(Msg)

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
        self.Cam.close()
        #self.Settings.save_QSettings()  # FIXME: activate this!
        # proceed with close
        event.accept()

    @QtCore.pyqtSlot()
    def on_pushButton_ConnectDisconnect_clicked(self):
        if self.Cam.is_Open():
            self.Cam.closeCamera()
            self.ui.pushButton_ConnectDisconnect.setText("connect")
            self.ui.comboBox_RawMode.clear()
            self.ui.groupBox_CameraSettings.setEnabled(False)
            self.ui.pushButton_StartRec.setEnabled(False)
        else:
            self.Cam.openCamera(self.ui.comboBox_Camera.currentIndex())
            self.ui.doubleSpinBox_ExposureTime.setMaximum(self.Cam.CameraSettings.max_ExposureTime)
            self.ui.doubleSpinBox_ExposureTime.setMinimum(self.Cam.CameraSettings.min_ExposureTime)
            self.ui.doubleSpinBox_ExposureTime.setValue(self.Cam.CameraSettings.ExposureTime)
            self.ui.doubleSpinBox_Gain.setMaximum(self.Cam.CameraSettings.max_AnalogueGain)
            self.ui.doubleSpinBox_Gain.setMinimum(self.Cam.CameraSettings.min_AnalogueGain)
            self.ui.doubleSpinBox_Gain.setValue(self.Cam.CameraSettings.AnalogueGain)
            self.ui.comboBox_RawMode.addItems([rm["label"] for rm in self.Cam.CameraSettings.available_RawModes])
            self.ui.comboBox_RawMode.setCurrentIndex(0)
            self.ui.pushButton_ConnectDisconnect.setText("disconnect")
            self.ui.groupBox_CameraSettings.setEnabled(True)
            self.ui.pushButton_StartRec.setEnabled(True)

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
        )

    @QtCore.pyqtSlot(dict)
    def on_Image(self, Img):
        self.ui.label_RecordingInfos.setText(
            f'{Img["RecordingInfos"]["disc_free"]/1024/1024} MiB (~{Img["RecordingInfos"]["disc_free_images"]} images) free'
        )
        self.ui.label_RecordedImageCounter.setText(f'{Img["RecordingInfos"]["ImagesRecorded"]} images saved')
        self.log_Debug(f'received image: {Img["array"].shape}, {Img["array"].dtype}')
        self.log_Debug(f'received metadata: {Img["metadata"]}')
        #Img["array"]
        #Img["metadata"]
        # TODO: wie wird Aufnahme automatisch gestoppt?

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
