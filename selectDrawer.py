import time

from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QListView, QAbstractItemView, QGraphicsDropShadowEffect
from PyQt5.QtCore import QRect, pyqtSignal, Qt
from PyQt5.QtGui import QPaintEvent, QIcon, QStandardItemModel, QStandardItem, QPainter, QColor


class SelectDrawer(QWidget):
    dataSelected = pyqtSignal(str)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)
        def makeBtn(txt, fun, xoffset=5):
            btn = QPushButton(txt, self)
            btn.hide()
            btn.clicked.connect(fun)
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(5)
            shadow.setYOffset(0)
            shadow.setXOffset(xoffset)
            btn.setGraphicsEffect(shadow)
            return btn

        self.btnLeft = makeBtn("<", self.preItem, 5)
        self.btnRight = makeBtn(">", self.nextItem, -5)

        self.listmodel = QStandardItemModel(self)
        self.listview = QListView(self)
        self.listview.setFlow(QListView.LeftToRight)
        self.listview.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listview.setModel(self.listmodel)
        self.listview.hide()
        self.listview.setStyleSheet("QListWidget{color:gray;font-size:12px;background:#FAFAFD;}\
                        QScrollBar{width:0;height:0}")
        self.listview.selectionModel().currentChanged.connect(self.currentIndexChanged)

    def setData(self, data):
        self.listmodel.clear()
        for d in data:
            self.listmodel.appendRow(QStandardItem(d))
        self.listview.setCurrentIndex(self.listmodel.index(0,0))
        #self.dataSelected.emit(self.listview.currentIndex().data())

    def nextItem(self):
        idx = self.listview.currentIndex().row()+1
        if idx >= self.listmodel.rowCount():
            return
        self.listview.setCurrentIndex(self.listmodel.index(idx, 0))

    def preItem(self):
        idx = self.listview.currentIndex().row()-1
        if idx < 0:
            return
        self.listview.setCurrentIndex(self.listmodel.index(idx, 0))

    def currentIndexChanged(self, now, before):

        self.dataSelected.emit(self.listview.currentIndex().data())

    def leaveEvent(self, a0) -> None:
        self.btnLeft.hide()
        self.btnRight.hide()
        self.listview.hide()

    def __judgeVisible(self, w, pos):
        if w.geometry().contains(pos):
            w.show()
        else:
            w.hide()

    def mouseMoveEvent(self, a0) -> None:
        pos = a0.pos()
        self.__judgeVisible(self.btnLeft, pos)
        self.__judgeVisible(self.btnRight, pos)
        self.__judgeVisible(self.listview, pos)

    def resizeEvent(self, a0) -> None:
        btnw = int(self.width()*0.15)
        btnh = btnw//2
        self.btnLeft.setGeometry(0, 0, btnw, self.height())
        self.btnRight.setGeometry(self.width() - btnw, 0, btnw, self.height())
        self.listview.setGeometry(btnw, self.height()-btnh, self.width()-2*btnw, btnh)

    def paintEvent(self, a0) -> None:
        pass


def testDrawer():
    import sys
    app = QApplication(sys.argv)
    warpper = QWidget()
    win = SelectDrawer(warpper)
    win.setGeometry(0,0,400,400)
    win.resize(400, 400)
    warpper.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    testDrawer()