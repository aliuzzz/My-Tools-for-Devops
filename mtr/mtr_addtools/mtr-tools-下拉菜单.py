import sys
from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator,QIcon
import pymysql

class Main(QWidget):
    def __init__(self):
        super().__init__()
        
        # 连接数据库
        self.conn = pymysql.connect(host="47.94.86.144", port=3306, user="root", password="qingdao@123", database="mtr")
        self.cursor = self.conn.cursor()
        
        # 初始化界面
        self.initUI()

    def initUI(self):
        # 设置窗口标题和大小
        self.setWindowTitle('MTR信息更新')
        self.setWindowIcon(QIcon('./icon.png'))
        self.resize(400, 300)

        # 设置窗口背景色和字体颜色
        self.setStyleSheet("background-color: #F5F5F5; color: #333333;")

        # 创建控件
        region_label = QLabel('地区')
        self.region_edit = QComboBox()
        self.region_edit.setEditable(True)
        self.region_edit.addItems(self.get_data('region'))
        self.region_edit.currentIndexChanged.connect(self.update_room_custom)
        self.region_edit.setStyleSheet("QComboBox { border: 1px solid gray; border-radius: 3px; padding: 1px 18px 1px 3px; min-width: 6em; } QComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: top right; width: 15px; border-left-width: 1px; border-left-color: darkgray; border-left-style: solid; border-top-right-radius: 3px; border-bottom-right-radius: 3px; } QComboBox::down-arrow { image: url(./down_arrow.png); width: 10px; height: 10px; }")

        room_label = QLabel('机房')
        self.room_edit = QComboBox()
        self.room_edit.setEditable(True)
        # self.room_edit.addItems(self.get_data('room'))
        self.room_edit.setStyleSheet("QComboBox { border: 1px solid gray; border-radius: 3px; padding: 1px 18px 1px 3px; min-width: 6em; } QComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: top right; width: 15px; border-left-width: 1px; border-left-color: darkgray; border-left-style: solid; border-top-right-radius: 3px; border-bottom-right-radius: 3px; } QComboBox::down-arrow { image: url(./down_arrow.png); width: 10px; height: 10px; }")

        custom_label = QLabel('客户')
        self.custom_edit = QComboBox()
        self.custom_edit.setEditable(True)
        #self.custom_edit.addItems(self.get_data('custom'))
        self.custom_edit.setStyleSheet("QComboBox { border: 1px solid gray; border-radius: 3px; padding: 1px 18px 1px 3px; min-width: 6em; } QComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: top right; width: 15px; border-left-width: 1px; border-left-color: darkgray; border-left-style: solid; border-top-right-radius: 3px; border-bottom-right-radius: 3px; } QComboBox::down-arrow { image: url(./down_arrow.png); width: 10px; height: 10px; }")

        ip_label = QLabel('IP')
        self.ip_edit = QLineEdit()
        ip_reg = QRegularExpression("^([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\."
                        "([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\."
                        "([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\."
                        "([01]?\\d\\d?|2[0-4]\\d|25[0-5])$")
        ip_validator = QRegularExpressionValidator(ip_reg, self.ip_edit)
        self.ip_edit.setValidator(ip_validator)

        operator_label = QLabel('运营商')
        self.operator_edit = QComboBox()
        self.operator_edit.setEditable(True)
        self.operator_edit.addItems(self.get_data('operator'))
        self.operator_edit.setStyleSheet("QComboBox { border: 1px solid gray; border-radius: 3px; padding: 1px 18px 1px 3px; min-width: 6em; } QComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: top right; width: 15px; border-left-width: 1px; border-left-color: darkgray; border-left-style: solid; border-top-right-radius: 3px; border-bottom-right-radius: 3px; } QComboBox::down-arrow { image: url(./down_arrow.png); width: 10px; height: 10px; }")

        submit_button = QPushButton('提交')
        submit_button.clicked.connect(self.submit)
        submit_button.setStyleSheet("QPushButton { border: 1px solid gray; border-radius: 3px; padding: 1px 5px; min-width: 6em; background-color: #0A81F3; color: #FFFFFF; } QPushButton:hover { background-color: #0A81F3; }")

        # 创建网格布局
        grid = QGridLayout()
        grid.setSpacing(10)

        # 将控件添加到布局中
        grid.addWidget(region_label, 1, 0)
        grid.addWidget(self.region_edit, 1, 1)

        grid.addWidget(room_label, 2, 0)
        grid.addWidget(self.room_edit, 2, 1)

        grid.addWidget(custom_label, 3, 0)
        grid.addWidget(self.custom_edit, 3, 1)

        grid.addWidget(ip_label, 4, 0)
        grid.addWidget(self.ip_edit, 4, 1)

        grid.addWidget(operator_label, 5, 0)
        grid.addWidget(self.operator_edit, 5, 1)

        grid.addWidget(submit_button, 6, 1)

        # 设置布局
        self.setLayout(grid)

    def get_data(self, field):
        # 查询数据
        self.cursor.execute(f"SELECT DISTINCT {field} FROM mtr_company")
        result = self.cursor.fetchall()
        data = [str(i[0]) for i in result]
        return data
    
    def update_room_custom(self):
        # 根据地区更新机房和客户下拉框
        region = self.region_edit.currentText()
        self.room_edit.clear()
        self.room_edit.addItems([''])
        self.room_edit.addItems(self.get_data_by_condition('room', 'region', region))
        self.custom_edit.clear()
        self.custom_edit.addItems([''])
        self.custom_edit.addItems(self.get_data_by_condition('custom', 'region', region))

    def get_data_by_condition(self, field, condition_field, condition_value):
        # 根据条件查询数据
        self.cursor.execute(f"SELECT DISTINCT {field} FROM mtr_company WHERE {condition_field}='{condition_value}'")
        result = self.cursor.fetchall()
        data = [str(i[0]) for i in result]
        return data
    
    def submit(self):
        # 获取输入的信息
        region = self.region_edit.currentText()
        room = self.room_edit.currentText()
        custom = self.custom_edit.currentText()
        ip = self.ip_edit.text()
        operator = self.operator_edit.currentText()
        # 检查空值
        if not region:
            QMessageBox.warning(self, '警告', '地区不能为空')
            return
        if not room:
            QMessageBox.warning(self, '警告', '机房不能为空')
            return
        if not custom:
            QMessageBox.warning(self, '警告', '客户不能为空')
            return
        if not ip:
            QMessageBox.warning(self, '警告', 'IP不能为空')
            return
        if not operator:
            QMessageBox.warning(self, '警告', '运营商不能为空')
            return

        description = room + '-' + custom + '-' + ip + '-' + operator
        sql = "INSERT INTO  mtr_company (ip, region, room, custom, operator, description) VALUES (%s, %s, %s, %s, %s, %s)"
        # 更新数据库
        try:
            self.cursor.execute(sql, (ip, region, room, custom, operator, description))
            self.conn.commit()
            # 查询数据库中是否有刚刚添加上的ip地址，
            self.cursor.execute(f"SELECT IF(COUNT(*) > 0, 0, 1) AS result FROM mtr_company WHERE ip ='{ip}'")
            data = int(self.cursor.fetchone()[0])
            if data == 0:
                QMessageBox.information(self, '提示', '更新成功')
            else:
                QMessageBox.warning(self, '警告', '更新失败')
        except Exception as e:
            print(e)
            QMessageBox.warning(self, '警告', '更新失败')

if __name__ == '__main__':
    app = QApplication([])
    main = Main()
    main.show()
    sys.exit(app.exec())
