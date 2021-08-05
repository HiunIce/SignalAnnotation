# -*- coding: utf-8 -*-
from PyQt5.QtCore import Qt, pyqtSignal, QRectF, QRect
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QMouseEvent, QColor, QPen, QBrush, QFont


# code from github, origin version is cpp#
class RangeSlider(QWidget):
    lowValueChanged = pyqtSignal(float)
    highValueChanged = pyqtSignal(float)
    _handleWidth = 8
    _handleHeight = 20

    _minimum = 0
    _maximum = 100

    _firstValue = 10
    _secondValue = 90

    _flag_firstHandlePressed = False
    _flag_secondHandlePressed = False
    _flag_rangeHandlePressed = False

    _flag_firstHandleHovered = False
    _flag_secondHandleHovered = False
    _flag_breakThroughOk = False
    _firstHandleColor = QColor("#FAFAFA")
    _secondHandleColor = QColor("#FAFAFA")
    _flag_horizontal = True

    def __init__(self, *args):
        super(QWidget, self).__init__(*args)
        self.setMouseTracking(True)

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        if (a0.buttons() == Qt.LeftButton):
            self._flag_secondHandlePressed = self._handleRect(self._secondValue).contains(a0.pos())
            self._flag_firstHandlePressed = not self._flag_secondHandlePressed and self._handleRect(
                self._firstValue).contains(a0.pos())
            self._flag_rangeHandlePressed = not (
                        self._flag_firstHandlePressed or self._flag_secondHandlePressed) and self._rangeHandleRect().contains(
                a0.pos())

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton):
            interval = abs(self._maximum - self._minimum)

            if (self._flag_secondHandlePressed):

                if (self._flag_horizontal):
                    self.setSecondValue(event.pos().x() * interval / (self.width() - self._handleWidth) + self._minimum)
                else:
                    self.setSecondValue(
                        event.pos().y() * interval / (self.height() - self._handleWidth) + self._minimum)

            elif (self._flag_firstHandlePressed):
                if (self._flag_horizontal):
                    self.setFirstValue(event.pos().x() * interval / (self.width() - self._handleWidth) + self._minimum)
                else:
                    self.setFirstValue(event.pos().y() * interval / (self.height() - self._handleWidth) + self._minimum)
            elif (self._flag_rangeHandlePressed):
                centerValue = (self._secondValue + self._firstValue) / 2
                if (self._flag_horizontal):
                    centerValue -= (event.pos().x() * interval / (self.width() - self._handleWidth) + self._minimum)
                else:
                    centerValue -= (event.pos().y() * interval / (self.height() - self._handleWidth) + self._minimum)

                self.setFirstValue(self._firstValue - centerValue)
                self.setSecondValue(self._secondValue - centerValue)

        rv2 = self._handleRect(self._secondValue)
        rv1 = self._handleRect(self._secondValue)
        self._secondHandleHovered = self._flag_secondHandlePressed or (
                    not self._flag_firstHandlePressed and rv2.contains(event.pos()))
        self._firstHandleHovered = self._flag_firstHandlePressed or (
                    not self._flag_secondHandleHovered and rv1.contains(event.pos()))
        self.update(rv2.toRect())
        self.update(rv1.toRect())

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setPen(QPen(Qt.gray, 0.8))
        painter.setRenderHint(QPainter.Qt4CompatiblePainting)
        painter.setBrush(QBrush(QColor("#D0D0D0")))
        rv1 = self._handleRect(self._firstValue)
        rv2 = self._handleRect(self._secondValue)

        if (self._flag_horizontal):
            r = QRectF(0, (self.height() - self._handleWidth) / 2, self.width() - 1, self._handleWidth)
        else:
            r = QRectF((self.width() - self._handleWidth) / 2, 0, self._handleWidth, self.height() - 1)
        painter.drawRoundedRect(r, 1, 1)

        painter.fillRect(self._rangeHandleRect(), QColor(Qt.green).darker(150))

        painter.setPen(QPen(Qt.darkGray, 0.5))
        painter.setRenderHint(QPainter.Antialiasing)

        handlecolor = self._firstHandleColor.lighter() if self._flag_firstHandleHovered else self._firstHandleColor
        painter.setBrush(QBrush(handlecolor))
        painter.drawRoundedRect(rv1, 2, 2)
        handlecolor = self._secondHandleColor.lighter() if self._flag_secondHandleHovered else self._secondHandleColor
        painter.setBrush(QBrush(handlecolor))
        painter.drawRoundedRect(rv2, 2, 2)

        if (self._flag_firstHandlePressed or self._flag_secondHandlePressed or self._flag_rangeHandlePressed):
            font = QFont()
            w = int(100)
            h = int(25)
            font.setFamily("Microsoft YaHei")
            font.setPixelSize(int(h * 0.7))
            painter.setFont(font)
            painter.drawText(QRectF(rv1.x() - w // 2, rv1.y(), w, h),
                             Qt.AlignCenter, "{:.1f}".format(self._firstValue))
            painter.drawText(QRectF(rv2.x() - w // 2, rv2.y(), w, h),
                             Qt.AlignCenter, "{:.1f}".format(self._secondValue))

    def _span(self):
        interval = abs(self._maximum - self._minimum)

        if (self._flag_horizontal):
            return (self.width() - self._handleWidth) / (interval)
        else:
            return (self.height() - self._handleWidth) / (interval)

    def _rangeHandleRect(self):
        s = self._span()
        if (self._flag_horizontal):
            r = QRectF(s * (self._firstValue - self._minimum), (self.height() - self._handleWidth) / 2,
                       s * (self._secondValue - self._firstValue), self._handleWidth)
        else:
            r = QRectF((self.width() - self._handleWidth) / 2, s * (self._firstValue - self._minimum),
                       self._handleWidth, s * (self._secondValue - self._firstValue))

        return r

    def _handleRect(self, value):
        s = self._span()
        if (self._flag_horizontal):
            r = QRectF(0, (self.height() - self._handleHeight) / 2, self._handleWidth, self._handleHeight)
            r.moveLeft(s * (value - self._minimum))
        else:
            r = QRectF((self.width() - self._handleHeight) / 2, 0, self._handleHeight, self._handleWidth)
            r.moveTop(s * (value - self._minimum))
        return r

    def setValueRange(self, min, max):
        self.setMinimum(min)
        self.setMaximum(max)
        r = max - min
        self.setFirstValue(min + 0.1 * r)
        self.setSecondValue(min + 0.9 * r)

    def setMaximum(self, max):
        if (max >= self._minimum):
            self._maximum = max;
        else:
            self._maximum = self._minimum
            self._minimum = max
        self.update();
        if (self._firstValue > self._maximum):
            self.setFirstValue(self._maximum);

        if (self._secondValue > self._maximum):
            self.setSecondValue(self._maximum)

    def setMinimum(self, min):
        if (min <= self._maximum):
            self._minimum = min
        else:
            self._minimum = self._maximum
            self._maximum = min
        self.update();
        if (self._firstValue < self._minimum):
            self.setFirstValue(self._minimum);

        if (self._secondValue < self._minimum):
            self.setSecondValue(self._minimum)

    def setFirstValue(self, low):
        if low == self._firstValue:
            return
        if low < self._minimum:
            low = self._minimum
            if (self._flag_breakThroughOk and self._flag_rangeHandlePressed):
                self.setMaximum(self._maximum + 100)
        low = self._secondValue if low >= self._secondValue else low
        self._firstValue = low

        self.lowValueChanged.emit(self._firstValue)
        self.update()

    def setSecondValue(self, high):
        if high == self._secondValue:
            return
        if high > self._maximum:
            high = self._maximum
            if (self._flag_breakThroughOk and self._flag_rangeHandlePressed):
                self.setMaximum(self._minimum - 100)
        high = self._firstValue if high <= self._firstValue else high
        self._secondValue = high

        self.highValueChanged.emit(self._secondValue)
        self.update()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    slider = RangeSlider()  # QtWidgets.QSlider()


    # TODO: fix handles' positioning while appearance is inverted
    # slider.setInvertedAppearance( True )

    def echo(value):
        print
        value


    # QtCore.QObject.connect(slider, QtCore.SIGNAL('sliderMoved(int)'), echo)
    # QtCore.QObject.connect(slider, QtCore.SIGNAL('lowValueChanged(int)'), echo)
    # QtCore.QObject.connect(slider, QtCore.SIGNAL('highValueChanged(int)'), echo)

    slider.show()
    sys.exit(app.exec_())
