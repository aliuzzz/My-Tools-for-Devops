import sys
from PyQt6.QtWidgets import QApplication, QWidget, QListWidget, QListWidgetItem, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from qfluentwidgets import ListWidget

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("可选择文本的 ListWidget 示例")
        self.resize(300, 400)

        # 创建 QListWidget 和布局
        self.list_widget = QListWidget()
        layout = QVBoxLayout(self)
        layout.addWidget(self.list_widget)

        # 添加多个条目
        for i in range(1, 21):
            # 创建一个空的 QListWidgetItem
            item = QListWidgetItem()
            # 将 item 添加到 list_widget 中
            self.list_widget.addItem(item)
            # 创建标签并设置文本
            label = QLabel(f"Item {i}")
            # 设置标签只允许用鼠标选择文本
            label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            # 将该标签作为 item 的视图组件放入 list_widget
            self.list_widget.setItemWidget(item, label)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())