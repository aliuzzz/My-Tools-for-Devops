import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QComboBox, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()

        # 创建控件
        self.label_a = QLabel("a:")
        self.label_b = QLabel("b:")
        self.label_formula = QLabel("选择公式:")
        self.combo_box = QComboBox()
        self.combo_box.addItem("公式1")
        self.combo_box.addItem("公式2")
        self.line_edit_a = QLineEdit()
        self.line_edit_b = QLineEdit()
        self.result_label = QLabel("结果:")
        self.result = QLabel()

        self.button = QPushButton("计算")
        self.button.clicked.connect(self.calculate)

        # 创建布局
        vbox1 = QVBoxLayout()
        vbox1.addWidget(self.label_a)
        vbox1.addWidget(self.line_edit_a)

        vbox2 = QVBoxLayout()
        vbox2.addWidget(self.label_b)
        vbox2.addWidget(self.line_edit_b)

        hbox1 = QHBoxLayout()
        hbox1.addLayout(vbox1)
        hbox1.addLayout(vbox2)

        vbox3 = QVBoxLayout()
        vbox3.addWidget(self.label_formula)
        vbox3.addWidget(self.combo_box)

        hbox2 = QHBoxLayout()
        hbox2.addLayout(hbox1)
        hbox2.addLayout(vbox3)

        vbox4 = QVBoxLayout()
        vbox4.addLayout(hbox2)
        vbox4.addWidget(self.button)

        vbox5 = QVBoxLayout()
        vbox5.addWidget(self.result_label)
        vbox5.addWidget(self.result)

        hbox3 = QHBoxLayout()
        hbox3.addLayout(vbox4)
        hbox3.addLayout(vbox5)

        self.setLayout(hbox3)

    def calculate(self):
        a = int(self.line_edit_a.text())
        b = int(self.line_edit_b.text())

        if self.combo_box.currentText() == "公式1":
            result = a + b
        else:
            result = a - b

        self.result.setText(str(result))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
