"""
managing application settings, including a QtDialog to change them
"""

from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import pyqtgraph.parametertree

from . import settings_ui


def name2key(name):
    """convert string to a valid QSettings key"""
    n = name
    for replacement in [(" ", "_")]:  # prepared for more replacements
        n = n.replace(*replacement)
    return n


class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, settings, *args, **kwargs):
        super(SettingsDialog, self).__init__(*args, **kwargs)
        self.ui = settings_ui.Ui_Dialog()
        self.ui.setupUi(self)
        self.Settings = settings
        self.Params = pyqtgraph.parametertree.Parameter.create(name='params', type='group', children=settings)
        self.ui.ParamTree.setParameters(self.Params, showTop=False)

    def get(self, *names):
        return self.Params.child(*names).value()

    def store_QSettings(self):
        """stores all settings in QSettings"""
        # recursive function to traverse the tree
        def _traverseTree(QSettings, Params):
            for p in Params:
                if p.type() == "group":
                    QSettings.beginGroup(name2key(p.name()))
                    _traverseTree(QSettings, p)
                    QSettings.endGroup()
                else:
                    QSettings.setValue(name2key(p.name()), p.value())
        #
        QSettings = QtCore.QSettings()
        _traverseTree(QSettings, self.Params)

    def load_QSettings(self):
        """loads all settings from QSettings"""
        # recursive function to traverse the tree
        def _traverseTree(QSettings, Params):
            for p in Params:
                if p.type() == "group":
                    QSettings.beginGroup(name2key(p.name()))
                    _traverseTree(QSettings, p)
                    QSettings.endGroup()
                else:
                    # older pyqtgraph does not know p.defaultValue()
                    #p.setValue(QSettings.value(name2key(p.name()), p.defaultValue()))
                    p.setValue(QSettings.value(name2key(p.name()), p.value()))
        #
        QSettings = QtCore.QSettings()
        _traverseTree(QSettings, self.Params)



if __name__ == '__main__':
    ExampleSettings = [
        {'name': 'group 1', 'type': 'group', 'children': [
            {'name': 'an integer', 'type': 'int', 'value': 500, 'limits': [100, 10000],
             'tip': 'this is an integer'},
            {'name': 'a string', 'type': 'str', 'value': "test string", 'tip': 'this is a string'},
            {'name': 'a float', 'type': 'float', 'value': 3.0, 'limits': [2.0, 3600], 'step': 0.5, 'suffix': ' sec',
             'tip': 'this is a float'},
            {'name': 'a 2nd float', 'type': 'float', 'value': 6.0, 'tip': 'this is a 2nd float'},
            {'name': 'a bool', 'type': 'bool', 'value': True, 'tip': "this is a checkbox"},
        ]},
        {'name': 'group 2', 'type': 'group', 'children': [
            {'name': 'a bool with nested float', 'type': 'bool', 'value': False, 'children': [
                {'name': u'nested float', 'type': 'float', 'value': 23.0, 'limits': [-400.0, 80.0],
                 'step': 1.0, 'visible': True},
            ]},
        ]},
        {'name': 'a hidden float', 'type': 'float', 'value': 10.0, 'limits': [2.0, 3600], 'step': 0.5, 'suffix': ' m',
         'tip': 'this is a hidden float', 'visible': False},
    ]
    #
    App = QtWidgets.QApplication(sys.argv)
    App.setOrganizationName("GeierSoft")
    App.setOrganizationDomain("Astro")
    App.setApplicationName("settings")
    #
    #
    MainWindow = SettingsDialog(settings=ExampleSettings)
    # MainWindow.resize(1400, 900)
    MainWindow.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        sys.exit(App.exec_())
