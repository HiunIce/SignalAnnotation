# -*- mode: python ; coding: utf-8 -*-
import os

import numpy as np
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication
from PyQt5.QtCore import QRect, pyqtSignal
from PyQt5.QtGui import QPaintEvent

#####
from matplotQt import PltCanvas
#####

class signalAnnotateWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.__pltcanvas = PltCanvas(self)
        self.plt = self.__pltcanvas.axes
        self.lineset = self.plt.lines
        self.collections = self.plt.collections
        self.target_name = []
        self.target_data = None
        self.readFunction = None

    def setReadFunction(self, fun):
        '''
        try to make it as a clear widget, but not a reader
        '''
        self.readFunction = fun

    def setFile(self, path):
        if not os.path.isfile(path):
            print("you shall input a file")
            return
        if self.readFunction is None:
            from utils.medicalFileIO import mat2nparray
            self.readFunction = mat2nparray
        print(path)
        data = self.readFunction(path)
        self.setData(os.path.splitext(path)[0], data)

    def setData(self, name, data):
        self.target_name = name
        self.target_data = data
        for i in range(self.target_data.shape[0]):
            self.plot(self.target_data[i], lw=0.3)

    def plot(self, *args, **kwargs):
        self.plt.plot(*args, **kwargs)

    def vlines(self, *args, **kwargs):
        self.plt.vlines(*args, **kwargs)

    def setLineWidth(self, lw):
        for l in self.lineset:
            l.set_lw(lw)

    def setSingalVisiblity(self, idx, v):
        self.setObjVisiblity(self.lineset, idx, v)

    def setVlineVisibility(self, idx, v):
        self.setObjVisiblity(self.collections, idx, v)

    def setObjVisiblity(self, obj, idx, v):
        if isinstance(idx, int):
            if idx < 0:
                for l in obj:
                    l.set_visible(v)
            else:
                obj.set_visible(v)
        else:
            for i in idx:
                obj.set_visible(v)

    def paintEvent(self, a0: QPaintEvent) -> None:
        pass

    def resizeEvent(self, a0) -> None:
        self.__pltcanvas.setGeometry(self.rect())

    def getAnnotation(self):
        return self.target_name

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = signalAnnotateWidget()
    import utils.medicalFileIO as mio
    path = "C:/dataset/paiSignal/Cancellous bone/Cancellous bone_1.mat"
    win.setFile(path)
    line = win.vlines(200, 0, 200, colors="c", linestyles="dashed")
    win.setSingalVisiblity(-1, True)
    # seg = line.get_segments()
    # line.set_segments([[[300, 0], [300,200]]])
    win.show()
    sys.exit(app.exec_())