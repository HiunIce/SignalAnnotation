# -*- mode: python ; coding: utf-8 -*-
import os

import cv2
import numpy as np
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QListView
from PyQt5.QtCore import QRect, pyqtSignal
from PyQt5.QtGui import QPaintEvent, QIcon, QStandardItemModel, QStandardItem
import scipy.io as scio
#####
from matplotQt import PltCanvas
from rangeSlider import RangeSlider
#####


'''
a widget like this
============  
  Mat Plot
===========
+- [[[[[double slider]]]]]
listview[name][name][name][name][name]
'''


class SignalAnnotateWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.__pltcanvas = PltCanvas(self)
        self.plt = self.__pltcanvas.axes
        self.lineset = self.plt.lines
        self.collections = self.plt.collections
        self.target_name = []
        self.target_data = None
        self.readFunction = None
        self.grabTools = OneDimLabelSlider(self)
        self.grabTools.rangeChanged.connect(self.setAnnotation)
        self.grabTools.currentDataChanged.connect(self.setAnnotation)

    def setReadFunction(self, fun):
        '''
        try to make it as a clear widget
        '''
        self.readFunction = fun

    def setFile(self, path):
        if not os.path.isfile(path):
            print("you shall input a file")
            return
        if self.readFunction is None:
            def mat2nparray(path):
                data = scio.loadmat(path)
                return data[list(data.keys())[-1]]
            self.readFunction = mat2nparray
        data = self.readFunction(path)
        self.setData(os.path.splitext(path)[0], data)

    def setData(self, name, data):
        self.target_name = name
        self.target_data = data
        for i in range(self.target_data.shape[0]):
            self.plot(self.target_data[i], lw=0.3)

        self.collections.clear()
        self.vlines(0, 0, 300, linestyle='dotted', linewidth=5, color='b')
        self.vlines(0, 0, 300, linestyle='dotted', linewidth=5, color='c')

        self.grabTools.blockSignals(True)
        self.grabTools.slider.setValueRange(0, self.target_data.shape[1])
        self.grabTools.blockSignals(False)
        self.setVlineVisibility(-1, False)

    def plot(self, *args, **kwargs):
        self.plt.plot(*args, **kwargs)

    def vlines(self, *args, **kwargs):
        line = self.plt.vlines(*args, **kwargs)
        line.set_segments([[[300, 0], [300, 200]]])

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
                obj[i].set_visible(v)

    def paintEvent(self, a0: QPaintEvent) -> None:
        pass

    def resizeEvent(self, a0) -> None:
        grabtoolHeiht = 80
        self.__pltcanvas.setGeometry(0, 0, self.width(), self.height()-grabtoolHeiht)
        self.grabTools.setGeometry(0, self.__pltcanvas.height(), self.width(), grabtoolHeiht)

    def getAnnotation(self):
        return self.target_name

    def setAnnotation(self, low, high):
        for v in self.collections:
            v.set_visible(True)
        self.collections[0].set_segments([[[low, 0], [low, 300]]])
        self.collections[1].set_segments([[[high, 0], [high, 300]]])
        self.__pltcanvas.draw()


class OneDimLabelSlider(QWidget):
    rangeChanged = pyqtSignal(float, float)
    currentDataChanged = pyqtSignal(float, float)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        root = os.path.dirname(__file__) + "/"

        self.btn_add = QPushButton(self)
        self.btn_add.setIcon(QIcon(root+'/icons/icon_addtag.png'))
        self.btn_add.setFlat(True)
        self.btn_add.clicked.connect(lambda : self.addData("data{}".format(self.listmodel.rowCount())))

        self.btn_rmv = QPushButton(self)
        self.btn_rmv.setIcon(QIcon(root+'/icons/icon_delete.png'))
        self.btn_rmv.setFlat(True)
        self.btn_rmv.clicked.connect(self.removeCurrentData)

        self.dataset = dict()
        self.listmodel = QStandardItemModel(self)
        self.listmodel.dataChanged.connect(self.dataChangedSlot)
        self.listview = QListView(self)
        self.listview.setFlow(QListView.LeftToRight)
        #self.listview.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listview.doubleClicked.connect(self._doubleClickItem)
        self.listview.setModel(self.listmodel)
        self.listview.selectionModel().currentChanged.connect(self.currentIndexChanged)

        self.slider = RangeSlider(self)
        self.slider.valueChanged.connect(self.rangeChangedSlot)
        self.slider.middlePressOn = False

        self.addDataCallBack = None

    def currentIndexChanged(self, now, before):
        self.currentDataChanged.emit(*self.dataset[now.data()])

    def dataChangedSlot(self, a, b):
        self.dataset[a.data()] = self.dataset.pop(self.dataBeforeModify)

    def rangeChangedSlot(self, low, high):
        self.rangeChanged.emit(low, high)
        self.dataset[self.listview.currentIndex().data()] = [low, high]

    def addData(self, name):
        if name in self.dataset.keys():
            return
        self.dataset[name] = [self.slider._firstValue, self.slider._secondValue]
        self.listmodel.appendRow(QStandardItem(name))
        self.currentDataChanged.emit(*self.dataset[name])

    def removeCurrentData(self):
        data = self.listview.currentIndex().data()
        self.dataset[data] = []
        self.listmodel.removeRow(self.listview.currentIndex().row())

    def resizeEvent(self, a0) -> None:
        ih, iw = 40, 40
        self.btn_add.setGeometry(0, 0, iw, ih)
        self.btn_rmv.setGeometry(self.btn_add.x()+self.btn_add.width(),
                                 0, iw, ih)
        self.slider.setGeometry(self.btn_rmv.x()+self.btn_rmv.width(),
                                0, self.width()-iw*2, ih)
        self.listview.setGeometry(0,self.slider.y()+self.slider.height(),
                                  self.width(), self.height()-ih)


    def paintEvent(self, a0) -> None:
        pass

    def _doubleClickItem(self):
        self.dataBeforeModify = self.listview.currentIndex().data()


def testMain():
    import sys
    app = QApplication(sys.argv)
    win = SignalAnnotateWidget()
    path = "testdata.mat"
    win.setFile(path)
    win.setSingalVisiblity(-1, True)
    win.show()
    sys.exit(app.exec_())


def testHeader():
    import sys
    app = QApplication(sys.argv)
    win = OneDimLabelSlider()
    win.resize(400,80)
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    testMain()