from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout
from PyQt6.QtCore import Qt

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        # 创建一个QLabel控件作为文本框的背景
        self.label = QLabel("Label", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 创建一个QLineEdit控件
        self.line_edit = QLineEdit(self)
        self.line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.line_edit.setHidden(True)

        # 将QLabel和QLineEdit添加到垂直布局中
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.line_edit)

        # 连接QLabel的单击事件，以便在单击时将QLineEdit设置为可编辑状态
        self.label.mousePressEvent = self.edit_text

    def edit_text(self, event):
        # 将QLineEdit设置为可编辑状态，并将其内容设置为QLabel的文本
        self.line_edit.setHidden(False)
        self.line_edit.setText(self.label.text())
        self.line_edit.setFocus()

        # 将QLabel设置为不可见状态
        self.label.setHidden(True)

        # 连接QLineEdit的完成编辑事件，以便在完成编辑时将QLineEdit设置为不可编辑状态，并将其内容设置为QLabel的文本
        self.line_edit.editingFinished.connect(self.update_label)

    def update_label(self):
        # 将QLineEdit设置为不可编辑状态，并将其内容设置为QLabel的文本
        self.line_edit.setHidden(True)
        self.label.setHidden(False)
        self.label.setText(self.line_edit.text())

if __name__ == '__main__':
    app = QApplication([])
    widget = MyWidget()
    widget.show()
    app.exec()
