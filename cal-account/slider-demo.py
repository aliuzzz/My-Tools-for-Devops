import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QSlider, QLineEdit, QVBoxLayout

class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        # 创建滑块组件
        self.slider = QSlider()
        self.slider.setRange(0, 10000)
        self.slider.setOrientation(Qt.Orientation.Horizontal)  # 设置滑块为垂直方向
        self.slider.setSingleStep(5)
        self.slider.valueChanged.connect(self.sliderMoved)

        # 创建文本框组件
        self.textbox = QLineEdit()
        self.textbox.textChanged.connect(self.textboxChanged)

        # 创建垂直布局
        vbox = QVBoxLayout()
        vbox.addWidget(self.slider)
        vbox.addWidget(self.textbox)

        self.setLayout(vbox)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('滑块和文本框')
        self.show()

    def sliderMoved(self, value):
        self.textbox.setText(str(value))

    def textboxChanged(self, text):
        value = int(text)
        self.slider.setValue(value)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec())