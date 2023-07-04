import sys
from PIL import Image, ImageDraw, ImageFont
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QMessageBox, QVBoxLayout, QWidget
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QPixmap, QRegularExpressionValidator, QIcon
from PyQt6.QtCore import QRegularExpression
from pathlib import Path

class ImageValidator(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("流量订正")
        self.setWindowIcon(QIcon('./ps.png'))
        self.setGeometry(100, 100, 400, 200)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.image_path_label = QLabel("图片路径（将图片直接拖到下面的对话框里）:", self.central_widget)
        self.layout.addWidget(self.image_path_label)

        self.image_path_textbox = QLineEdit(self.central_widget)
        self.layout.addWidget(self.image_path_textbox)
        self.image_path_textbox.setReadOnly(True)

        self.number_label = QLabel("要修改的流量值（包含单位M，最大11个字符位）:", self.central_widget)
        self.layout.addWidget(self.number_label)

        self.number_textbox = QLineEdit(self.central_widget)
        self.layout.addWidget(self.number_textbox)
        #self.number_textbox.setValidator(QDoubleValidator(self.number_textbox))
        self.number_textbox.setValidator(QRegularExpressionValidator(QRegularExpression("^[0-9.]+[a-zA-Z]*$"), self.number_textbox))



        self.button = QPushButton("确认修改", self.central_widget)
        self.layout.addWidget(self.button)
        self.button.clicked.connect(self.validate_image)

        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            file_path = url.toLocalFile()
            self.image_path_textbox.setText(file_path)
            
    def change_num(self):
        image_path = self.image_path_textbox.text()
        number = self.number_textbox.text()
        canvas = Image.new('RGB', (100,17), '#F3F3F3')
        draw = ImageDraw.Draw(canvas)#创建画笔      
        font = ImageFont.truetype("./wqy-zenhei.ttc", 15)  #设置字体
        draw.text((2,0), number, font=font, fill='black')  #绘制数字 x,y,左上角是0，0
        image_b = Image.open(image_path) #打开图片b
        image_a_width, image_a_height = canvas.size   #获取图片a的尺寸
        image_b.paste(canvas, (115, 381)) #将canvas粘贴到图片b的左上角
        folder_path = './result/'         # 指定文件夹路径
        Path(folder_path).mkdir(parents=True, exist_ok=True) # 使用Path.mkdir()方法创建文件夹
        image_b.save("./result/result.png") #保存修改后的图片b


    def validate_image(self):
        image_path = self.image_path_textbox.text()
        number = self.number_textbox.text()

        if not image_path:
            QMessageBox.warning(self, "Error", "请添加图片路径")
            return
        if not number:
            QMessageBox.warning(self, "Error", "请添加要修改的流量值(包含单位M，最大11个字符位)")
            return

        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            QMessageBox.warning(self, "Error", "图片文件路径为空")
            return

        if pixmap.width() == 793 and pixmap.height() == 412:
            self.change_num()
            QMessageBox.information(self, "ok", "已生成结果result.png在当前目录下")
        else:
            reply = QMessageBox.question(self, "Confirmation", "图片尺寸不是793x412，替换的流量值位置会异常，是否继续？", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.change_num()
            else:
                return

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageValidator()
    window.show()
    sys.exit(app.exec())
