# -*- mode: python ; coding: utf-8 -*-
import datetime
import json
import os

import cv2
import numpy as np
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QListView, QFileDialog
from PyQt5.QtCore import QRect, pyqtSignal, Qt
from PyQt5.QtGui import QPaintEvent, QIcon, QStandardItemModel, QStandardItem
import scipy.io as scio
#####
from matplotQt import PltCanvas
from rangeSlider import RangeSlider
from selectDrawer import SelectDrawer
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
        self.__pltcanvas.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.plt = self.__pltcanvas.axes
        self.lineset = self.plt.lines
        self.collections = self.plt.collections
        self.target_root = ''
        self.target_name = 'data'
        self.target_data = None
        self.readFunction = None
        self.grabTools = OneDimLabelSlider(self)
        self.grabTools.rangeChanged.connect(self.setAnnotation)
        self.grabTools.currentDataChanged.connect(self.setAnnotation)
        self.selector = SelectDrawer(self)
        self.selector.dataSelected.connect(lambda file: self.setFile(self.target_root+"/"+file))

    def setReadFunction(self, fun):
        '''
        try to make it as a clear widget
        '''
        self.readFunction = fun

    def mouseDoubleClickEvent(self, a0) -> None:
        dir_path = QFileDialog.getExistingDirectory(self, "choose directory", os.path.dirname(__file__))
        if dir_path == "":
            return
        self.target_root = dir_path
        dataname = []
        for file in next(os.walk(dir_path))[2]:
            if '.mat' in file:
                dataname.append(file)
        if len(dataname) == 0:
            self.clearLine()
        self.selector.setData(dataname)

    def clearLine(self):
        for l in self.lineset:
            self.plt.remove(l)
        self.plt.lines = []
        self.__pltcanvas.draw()

    def setFile(self, path):
        if not os.path.isfile(path):
            print("you shall input a file")
            self.clearLine()
            return
        if len(self.grabTools.dataset) != 0:
            self.grabTools.saveData()
        if self.readFunction is None:
            def mat2nparray(path):
                data = scio.loadmat(path)
                return data[list(data.keys())[-1]]
            self.readFunction = mat2nparray
        data = self.readFunction(path)
        self.setData(os.path.splitext(path)[0], data)
        if os.path.isfile(path.replace(".mat", ".json")):
            f = open(path.replace(".mat", ".json"))
            data = f.read()
            f.close()
            data = json.loads(data)
            self.grabTools.setDataset(data)


    def setData(self, name, data):
        self.target_name = name
        self.target_data = data
        #print('set data', self.target_name, self.target_data.shape)
        self.grabTools.savePath = name+".json"
        self.clearLine()
        self.grabTools.listmodel.clear()
        self.grabTools.dataset = dict()
        for i in range(self.target_data.shape[0]):
            self.plot(self.target_data[i], lw=0.3)
        min, max =  np.min(self.target_data), np.max(self.target_data)
        diff = max - min
        self.plt.axis([-20, self.target_data[i].shape[0]+20, min-diff*0.1, max+diff*0.1])
        self.collections.clear()
        self.vlines(0, 0, 300, linestyle='dotted', linewidth=5, color='b')
        self.vlines(0, 0, 300, linestyle='dotted', linewidth=5, color='c')

        self.grabTools.slider.blockSignals(True)
        self.grabTools.slider.setValueRange(0, self.target_data.shape[1])
        self.grabTools.slider.blockSignals(False)
        self.setVlineVisibility(-1, False)
        self.__pltcanvas.draw()

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
        self.selector.setGeometry(self.__pltcanvas.geometry())
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
        self.__initBtns()
        self.__initListView()
        self.slider = RangeSlider(self)
        self.slider.valueChanged.connect(self.rangeChangedSlot)
        self.slider.middlePressOn = False

        self.dataset = dict()

        self.addDataCallBack = None
        self.savePath = "save_{}.json".format(datetime.datetime.now().strftime('%m%d_%M%S'))

    def __initBtns(self):
        root = os.path.dirname(__file__) + "/"

        def makeBtn(icon, slot):
            btn = QPushButton(self)
            btn.setIcon(QIcon(root + '/icons/{}.png'.format(icon)))
            btn.setFlat(True)
            btn.clicked.connect(slot)
            return btn
        self.btn_add = makeBtn('icon_addtag', lambda : self.addData("data{}".format(self.listmodel.rowCount())))
        self.btn_rmv = makeBtn('icon_delete', self.removeCurrentData)
        self.btn_sav = makeBtn('icon_save', self.saveData)

    def __initListView(self):
        self.listmodel = QStandardItemModel(self)
        self.listmodel.dataChanged.connect(self.dataChangedSlot)
        self.listview = QListView(self)
        self.listview.setFlow(QListView.LeftToRight)
        #self.listview.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listview.doubleClicked.connect(self._doubleClickItem)
        self.listview.setModel(self.listmodel)
        self.listview.selectionModel().currentChanged.connect(self.currentIndexChanged)

    def currentIndexChanged(self, now, before):
        self.currentDataChanged.emit(*self.dataset[now.data()])

    def dataChangedSlot(self, a, b):
        self.dataset[a.data()] = self.dataset.pop(self.dataBeforeModify)

    def rangeChangedSlot(self, low, high):
        self.rangeChanged.emit(low, high)
        if self.listview.currentIndex().data() in self.dataset:
            self.dataset[self.listview.currentIndex().data()] = [low, high]

    def addData(self, name):
        if name in self.dataset.keys():
            return
        self.dataset[name] = [self.slider._firstValue, self.slider._secondValue]
        self.listmodel.appendRow(QStandardItem(name))
        self.currentDataChanged.emit(*self.dataset[name])

    def removeCurrentData(self):
        data = self.listview.currentIndex().data()
        del self.dataset[data]
        self.listmodel.removeRow(self.listview.currentIndex().row())

    def saveData(self):
        jd = json.dumps(self.dataset, indent=4, ensure_ascii=False)
        f = open(self.savePath, "w")
        f.write(jd)
        f.close()
        print(self.dataset)
        print("save data")


    def resizeEvent(self, a0) -> None:
        ih, iw = 40, 40
        self.btn_add.setGeometry(0, 0, iw, ih)
        self.btn_rmv.setGeometry(self.btn_add.x()+self.btn_add.width(),
                                 0, iw, ih)
        self.btn_sav.setGeometry(self.btn_rmv.x()+self.btn_rmv.width(),
                                 0, iw, ih)
        self.slider.setGeometry(self.btn_sav.x()+self.btn_sav.width(),
                                0, self.width()-iw*3, ih)
        self.listview.setGeometry(0,self.slider.y()+self.slider.height(),
                                  self.width(), self.height()-ih)

    def setDataset(self, data):
        self.dataset = data
        for k in self.dataset.keys():
            self.listmodel.appendRow(QStandardItem(k))
        self.listview.setCurrentIndex(self.listmodel.index(0, 0))

    def paintEvent(self, a0) -> None:
        pass

    def _doubleClickItem(self):
        self.dataBeforeModify = self.listview.currentIndex().data()


def testMain():
    import sys
    app = QApplication(sys.argv)
    win = SignalAnnotateWidget()
    path = "testdata/testdata.mat"
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