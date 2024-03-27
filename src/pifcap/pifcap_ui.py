# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pifcap_ui.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1170, 746)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.widget_2 = QtWidgets.QWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(5)
        sizePolicy.setHeightForWidth(self.widget_2.sizePolicy().hasHeightForWidth())
        self.widget_2.setSizePolicy(sizePolicy)
        self.widget_2.setObjectName("widget_2")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.widget_2)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.splitter = QtWidgets.QSplitter(self.widget_2)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.widget_3 = QtWidgets.QWidget(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_3.sizePolicy().hasHeightForWidth())
        self.widget_3.setSizePolicy(sizePolicy)
        self.widget_3.setObjectName("widget_3")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget_3)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.splitter_2 = QtWidgets.QSplitter(self.widget_3)
        self.splitter_2.setOrientation(QtCore.Qt.Vertical)
        self.splitter_2.setObjectName("splitter_2")
        self.ImageView_Preview = ImageView(self.splitter_2)
        self.ImageView_Preview.setObjectName("ImageView_Preview")
        self.plainTextEdit_Log = QtWidgets.QPlainTextEdit(self.splitter_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plainTextEdit_Log.sizePolicy().hasHeightForWidth())
        self.plainTextEdit_Log.setSizePolicy(sizePolicy)
        self.plainTextEdit_Log.setObjectName("plainTextEdit_Log")
        self.verticalLayout_3.addWidget(self.splitter_2)
        self.widget = QtWidgets.QWidget(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setObjectName("widget")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.scrollArea = QtWidgets.QScrollArea(self.widget)
        self.scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents_3 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_3.setGeometry(QtCore.QRect(0, 0, 320, 705))
        self.scrollAreaWidgetContents_3.setObjectName("scrollAreaWidgetContents_3")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents_3)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.groupBox_3 = QtWidgets.QGroupBox(self.scrollAreaWidgetContents_3)
        self.groupBox_3.setObjectName("groupBox_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox_3)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.comboBox_Camera = QtWidgets.QComboBox(self.groupBox_3)
        self.comboBox_Camera.setObjectName("comboBox_Camera")
        self.horizontalLayout.addWidget(self.comboBox_Camera)
        self.pushButton_ConnectDisconnect = QtWidgets.QPushButton(self.groupBox_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_ConnectDisconnect.sizePolicy().hasHeightForWidth())
        self.pushButton_ConnectDisconnect.setSizePolicy(sizePolicy)
        self.pushButton_ConnectDisconnect.setObjectName("pushButton_ConnectDisconnect")
        self.horizontalLayout.addWidget(self.pushButton_ConnectDisconnect)
        self.verticalLayout_6.addWidget(self.groupBox_3)
        self.groupBox_CameraSettings = QtWidgets.QGroupBox(self.scrollAreaWidgetContents_3)
        self.groupBox_CameraSettings.setObjectName("groupBox_CameraSettings")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox_CameraSettings)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_5 = QtWidgets.QLabel(self.groupBox_CameraSettings)
        self.label_5.setObjectName("label_5")
        self.gridLayout_2.addWidget(self.label_5, 1, 0, 1, 1)
        self.doubleSpinBox_Gain = QtWidgets.QDoubleSpinBox(self.groupBox_CameraSettings)
        self.doubleSpinBox_Gain.setObjectName("doubleSpinBox_Gain")
        self.gridLayout_2.addWidget(self.doubleSpinBox_Gain, 1, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.groupBox_CameraSettings)
        self.label_6.setObjectName("label_6")
        self.gridLayout_2.addWidget(self.label_6, 2, 0, 1, 1)
        self.doubleSpinBox_ExposureTime = QtWidgets.QDoubleSpinBox(self.groupBox_CameraSettings)
        self.doubleSpinBox_ExposureTime.setObjectName("doubleSpinBox_ExposureTime")
        self.gridLayout_2.addWidget(self.doubleSpinBox_ExposureTime, 2, 1, 1, 1)
        self.pushButton_OptimizeExposure = QtWidgets.QPushButton(self.groupBox_CameraSettings)
        self.pushButton_OptimizeExposure.setObjectName("pushButton_OptimizeExposure")
        self.gridLayout_2.addWidget(self.pushButton_OptimizeExposure, 2, 2, 1, 1)
        self.comboBox_RawMode = QtWidgets.QComboBox(self.groupBox_CameraSettings)
        self.comboBox_RawMode.setObjectName("comboBox_RawMode")
        self.gridLayout_2.addWidget(self.comboBox_RawMode, 0, 0, 1, 3)
        self.verticalLayout_6.addWidget(self.groupBox_CameraSettings)
        self.groupBox_4 = QtWidgets.QGroupBox(self.scrollAreaWidgetContents_3)
        self.groupBox_4.setObjectName("groupBox_4")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox_4)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.checkBox_PreviewFlipH = QtWidgets.QCheckBox(self.groupBox_4)
        self.checkBox_PreviewFlipH.setObjectName("checkBox_PreviewFlipH")
        self.gridLayout_3.addWidget(self.checkBox_PreviewFlipH, 0, 1, 1, 1)
        self.checkBox_PreviewFlipV = QtWidgets.QCheckBox(self.groupBox_4)
        self.checkBox_PreviewFlipV.setObjectName("checkBox_PreviewFlipV")
        self.gridLayout_3.addWidget(self.checkBox_PreviewFlipV, 0, 2, 1, 1)
        self.comboBox_PreviewRot = QtWidgets.QComboBox(self.groupBox_4)
        self.comboBox_PreviewRot.setObjectName("comboBox_PreviewRot")
        self.comboBox_PreviewRot.addItem("")
        self.comboBox_PreviewRot.addItem("")
        self.comboBox_PreviewRot.addItem("")
        self.comboBox_PreviewRot.addItem("")
        self.gridLayout_3.addWidget(self.comboBox_PreviewRot, 0, 0, 1, 1)
        self.checkBox_Saturation = QtWidgets.QCheckBox(self.groupBox_4)
        self.checkBox_Saturation.setEnabled(False)
        self.checkBox_Saturation.setChecked(True)
        self.checkBox_Saturation.setObjectName("checkBox_Saturation")
        self.gridLayout_3.addWidget(self.checkBox_Saturation, 1, 2, 1, 1)
        self.comboBox_RawPreviewMode = QtWidgets.QComboBox(self.groupBox_4)
        self.comboBox_RawPreviewMode.setEnabled(False)
        self.comboBox_RawPreviewMode.setObjectName("comboBox_RawPreviewMode")
        self.comboBox_RawPreviewMode.addItem("")
        self.comboBox_RawPreviewMode.addItem("")
        self.comboBox_RawPreviewMode.addItem("")
        self.comboBox_RawPreviewMode.addItem("")
        self.comboBox_RawPreviewMode.addItem("")
        self.gridLayout_3.addWidget(self.comboBox_RawPreviewMode, 1, 0, 1, 1)
        self.verticalLayout_6.addWidget(self.groupBox_4)
        self.groupBox = QtWidgets.QGroupBox(self.scrollAreaWidgetContents_3)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton_Folder = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_Folder.setObjectName("pushButton_Folder")
        self.gridLayout.addWidget(self.pushButton_Folder, 0, 0, 1, 2)
        self.spinBox_nImagesToRecord = QtWidgets.QSpinBox(self.groupBox)
        self.spinBox_nImagesToRecord.setMaximumSize(QtCore.QSize(70, 16777215))
        self.spinBox_nImagesToRecord.setMinimum(1)
        self.spinBox_nImagesToRecord.setMaximum(999999)
        self.spinBox_nImagesToRecord.setObjectName("spinBox_nImagesToRecord")
        self.gridLayout.addWidget(self.spinBox_nImagesToRecord, 2, 1, 1, 3)
        self.lineEdit_ImageComment = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_ImageComment.setObjectName("lineEdit_ImageComment")
        self.gridLayout.addWidget(self.lineEdit_ImageComment, 1, 1, 1, 6)
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.doubleSpinBox_TimeLapse = QtWidgets.QDoubleSpinBox(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.doubleSpinBox_TimeLapse.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox_TimeLapse.setSizePolicy(sizePolicy)
        self.doubleSpinBox_TimeLapse.setMaximumSize(QtCore.QSize(70, 16777215))
        self.doubleSpinBox_TimeLapse.setPrefix("")
        self.doubleSpinBox_TimeLapse.setDecimals(1)
        self.doubleSpinBox_TimeLapse.setMaximum(1000000.0)
        self.doubleSpinBox_TimeLapse.setObjectName("doubleSpinBox_TimeLapse")
        self.gridLayout.addWidget(self.doubleSpinBox_TimeLapse, 2, 5, 1, 1)
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 2, 4, 1, 1)
        self.pushButton_StartRec = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_StartRec.setObjectName("pushButton_StartRec")
        self.gridLayout.addWidget(self.pushButton_StartRec, 4, 0, 1, 2)
        self.label_RecordingInfos = QtWidgets.QLabel(self.groupBox)
        self.label_RecordingInfos.setObjectName("label_RecordingInfos")
        self.gridLayout.addWidget(self.label_RecordingInfos, 3, 0, 1, 7)
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 2, 1, 1)
        self.lineEdit_FileNamePrefix = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_FileNamePrefix.setObjectName("lineEdit_FileNamePrefix")
        self.gridLayout.addWidget(self.lineEdit_FileNamePrefix, 0, 3, 1, 4)
        self.pushButton_StopRec = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_StopRec.setEnabled(False)
        self.pushButton_StopRec.setObjectName("pushButton_StopRec")
        self.gridLayout.addWidget(self.pushButton_StopRec, 4, 5, 1, 2)
        self.label_RecordedImageCounter = QtWidgets.QLabel(self.groupBox)
        self.label_RecordedImageCounter.setObjectName("label_RecordedImageCounter")
        self.gridLayout.addWidget(self.label_RecordedImageCounter, 4, 2, 1, 3)
        self.verticalLayout_6.addWidget(self.groupBox)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_6.addItem(spacerItem)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents_3)
        self.verticalLayout_5.addWidget(self.scrollArea)
        self.verticalLayout_4.addWidget(self.splitter)
        self.verticalLayout_2.addWidget(self.widget_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1170, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.action_DarkNoiseMeasurement = QtWidgets.QAction(MainWindow)
        self.action_DarkNoiseMeasurement.setObjectName("action_DarkNoiseMeasurement")

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.groupBox_3.setTitle(_translate("MainWindow", "Camera"))
        self.pushButton_ConnectDisconnect.setText(_translate("MainWindow", "connect"))
        self.groupBox_CameraSettings.setTitle(_translate("MainWindow", "Camera Settings"))
        self.label_5.setText(_translate("MainWindow", "gain:"))
        self.label_6.setText(_translate("MainWindow", "exposure time:"))
        self.pushButton_OptimizeExposure.setText(_translate("MainWindow", "optimize"))
        self.groupBox_4.setTitle(_translate("MainWindow", "Display"))
        self.checkBox_PreviewFlipH.setText(_translate("MainWindow", "flip H"))
        self.checkBox_PreviewFlipV.setText(_translate("MainWindow", "flip V"))
        self.comboBox_PreviewRot.setItemText(0, _translate("MainWindow", "0deg"))
        self.comboBox_PreviewRot.setItemText(1, _translate("MainWindow", "90deg"))
        self.comboBox_PreviewRot.setItemText(2, _translate("MainWindow", "180deg"))
        self.comboBox_PreviewRot.setItemText(3, _translate("MainWindow", "270deg"))
        self.checkBox_Saturation.setText(_translate("MainWindow", "saturation"))
        self.comboBox_RawPreviewMode.setItemText(0, _translate("MainWindow", "luminance"))
        self.comboBox_RawPreviewMode.setItemText(1, _translate("MainWindow", "red"))
        self.comboBox_RawPreviewMode.setItemText(2, _translate("MainWindow", "green 1"))
        self.comboBox_RawPreviewMode.setItemText(3, _translate("MainWindow", "green 2"))
        self.comboBox_RawPreviewMode.setItemText(4, _translate("MainWindow", "blue"))
        self.groupBox.setTitle(_translate("MainWindow", "Recording"))
        self.pushButton_Folder.setText(_translate("MainWindow", "Folder"))
        self.label_4.setText(_translate("MainWindow", "# Images:"))
        self.label_2.setText(_translate("MainWindow", "Comment:"))
        self.doubleSpinBox_TimeLapse.setSuffix(_translate("MainWindow", " sec"))
        self.label.setText(_translate("MainWindow", "every"))
        self.pushButton_StartRec.setText(_translate("MainWindow", "Rec"))
        self.label_RecordingInfos.setText(_translate("MainWindow", " "))
        self.label_3.setText(_translate("MainWindow", "Prefix:"))
        self.pushButton_StopRec.setText(_translate("MainWindow", "Stop"))
        self.label_RecordedImageCounter.setText(_translate("MainWindow", "0 images saved"))
        self.action_DarkNoiseMeasurement.setText(_translate("MainWindow", "Dark Noise Measurement"))
from pyqtgraph import ImageView


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
