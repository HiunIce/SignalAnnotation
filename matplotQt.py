from PyQt5.QtWidgets import QSizePolicy, QApplication
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class PltCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(1,1,1)

        self.compute_initial_figure()
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass

    def mousePressEvent(self, event):
        print("!")

def test_PltCanvas():
    import sys
    app = QApplication(sys.argv)
    win = PltCanvas()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    test_PltCanvas()