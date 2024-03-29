##新增把current改为可更改的，新增实时显示公式
##待整理，还没调通
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QSlider, QMessageBox
from PyQt6.QtGui import QColor, QPalette, QRegularExpressionValidator, QFont
from PyQt6.QtCore import Qt, QRegularExpression

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        self.setGeometry(300, 300, 300, 200)

        self.price_label = QLabel('出售单价(元/GB/月)')
        self.price_edit = QLineEdit()
        self.price_edit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]+([.]\\d+)?")))

        self.cost_label = QLabel('成本价(元/GB/月)')
        self.cost_edit = QLineEdit()
        self.cost_edit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]+([.]\\d+)?")))
        
        self.minimum_label = QLabel('保底流量(G)')
        self.minimum_edit = QLineEdit()
        self.minimum_edit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]+([.]\\d+)?")))

        self.subsidy_label = QLabel('补贴流量(G)')
        self.subsidy_edit = QLineEdit()
        self.subsidy_edit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]+([.]\\d+)?")))

        self.custom_label = QLabel('客户侧保底流量(G)')
        self.custom_edit = QLineEdit()
        self.custom_edit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]+([.]\\d+)?")))

        self.current_label = QLabel('当前实际流量(G)')
        self.current_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.current_slider.setRange(0,1500)
        self.current_slider.setSingleStep(1)
        self.current_slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.current_slider.valueChanged.connect(self.update_label)
        
        self.current_value_label = QLabel('0')
        self.current_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.line_edit = QLineEdit(self)
        self.line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.line_edit.setHidden(True)    

        self.result_label = QLabel('0')
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 添加“公式”标签  
        self.formula_label = QLabel('当前公式：')
        self.formula_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        #这里公式可以调整成可选项，QComboBox(),让QComBox的值传到下面的result中，不同的公式出不同的result
        #self.combo_box = QComboBox()
        #self.combo_box.addItem("公式1")
        #self.combo_box.addItem("公式2")
        
        # 设置字体和字号
        font = QFont()
        font.setPointSize(15)
        self.price_label.setFont(font)
        self.price_edit.setFont(font)
        self.cost_label.setFont(font)
        self.cost_edit.setFont(font)
        self.minimum_label.setFont(font)
        self.minimum_edit.setFont(font)
        self.subsidy_label.setFont(font)
        self.subsidy_edit.setFont(font)
        self.custom_label.setFont(font)
        self.custom_edit.setFont(font)
        self.formula_label.setFont(font)
        self.current_label.setFont(font)
        self.current_value_label.setFont(font)
        self.result_label.setFont(font)
        self.result_label.setFont(font)
        self.result_label.setStyleSheet("font-weight: bold;")

        #美化进度条，groove是进度条参数，handle是滑块的参数
        slider_style = """
        QSlider::groove:horizontal {
            border: 1px solid #bbb;
            background: white;
            height: 10px;
            border-radius: 3px;  
        }

        QSlider::handle:horizontal {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #eee, stop:1 #ccc);
            border: 1px solid #777;
            width: 20px;
            margin: -5px 0;
            border-radius: 2px;
        }
        """
        self.current_slider.setStyleSheet(slider_style)
    # 连接QLabel的单击事件，以便在单击时将QLineEdit设置为可编辑状态
        self.current_value_label.mousePressEvent = self.edit_text 

        vbox = QVBoxLayout()
        vbox.addWidget(self.price_label)
        vbox.addWidget(self.price_edit)
        vbox.addWidget(self.cost_label)
        vbox.addWidget(self.cost_edit)
        vbox.addWidget(self.minimum_label)
        vbox.addWidget(self.minimum_edit)
        vbox.addWidget(self.subsidy_label)
        vbox.addWidget(self.subsidy_edit)
        vbox.addWidget(self.custom_label)
        vbox.addWidget(self.custom_edit)
        vbox.addWidget(self.formula_label)

        current_hbox = QHBoxLayout()
        current_hbox.addWidget(self.current_label)
        current_hbox.addWidget(self.current_value_label)
        current_hbox.addWidget(self.line_edit)
        vbox.addLayout(current_hbox)

        vbox.addWidget(self.current_slider)
        vbox.addWidget(self.result_label)


        self.setLayout(vbox)
        self.setWindowTitle('流量计算器')

    def edit_text(self, event):
        # 将QLineEdit设置为可编辑状态，并将其内容设置为QLabel的文本
        self.line_edit.setHidden(False)
        self.line_edit.setText(self.current_value_label.text())
        self.line_edit.setFocus()

        # 将QLabel设置为不可见状态
        self.current_value_label.setHidden(True)

        # 连接QLineEdit的完成编辑事件，以便在完成编辑时将QLineEdit设置为不可编辑状态，并将其内容设置为QLabel的文本
        self.line_edit.editingFinished.connect(self.update_label)

    def update_label(self):
        # 将QLineEdit设置为不可编辑状态，并将其内容设置为QLabel的文本
        self.line_edit.setHidden(True)
        self.current_value_label.setHidden(False)
        self.current_value_label.setText(self.line_edit.text())

        value = float(self.line_edit.text())
        self.current_slider.setValue(int(value))

    def update_label(self, value):
    # 获取输入框中的值
        price_text = self.price_edit.text()
        cost_text = self.cost_edit.text()
        minimum_text = self.minimum_edit.text()
        subsidy_text = self.subsidy_edit.text()
        custom_text = self.custom_edit.text()
        #current_text = self.current_value_label.text()

        # 检查输入框中的值是否为空
        if not price_text or not cost_text or not minimum_text or not subsidy_text or not custom_text :
            QMessageBox.warning(self, '警告', '请确保所有输入框都已填写！')
            self.current_slider.setValue(0)
            return

        # 将输入框中的值转换为浮点数
        price = float(price_text)
        cost = float(cost_text)
        minimum = float(minimum_text)
        subsidy = float(subsidy_text)
        custom = float(custom_text)
        #current = float(current_text)
       # current = float(self.current_slider.value())
        current = float(value)
        result = 0
        #result公式,这里如果很多条件可以用match..case方法来写
        if current >= custom and (current - subsidy) >= minimum:
            result = price * current - cost * (current - subsidy)
        elif current >= custom and (current - subsidy) < minimum:
            result = price * current - cost * minimum
        elif current < custom and (current - subsidy) >= minimum:
            result = price * custom - cost * (current - subsidy)
        elif current < custom and (current - subsidy) < minimum:
            result = price * custom - cost * minimum

        self.current_value_label.setText(str(value))
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.WindowText, QColor('blue'))
        self.current_value_label.setPalette(palette)
        
        if result > 0:
            color = 'red'
        elif result < 0:
            color = 'green'
        else:
            color = 'black'
        palette.setColor(QPalette.ColorRole.WindowText, QColor(color))
        self.result_label.setPalette(palette)
        self.result_label.setText(f'结果：{result:.2f}元')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MyWidget()
    w.show()
    sys.exit(app.exec())
