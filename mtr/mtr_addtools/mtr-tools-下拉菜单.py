import sys
from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox
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
        self.resize(400, 300)

        # 创建控件
        region_label = QLabel('地区')
        self.region_edit = QComboBox()
        self.region_edit.setEditable(True)
        self.region_edit.addItems(self.get_data('region'))
        self.region_edit.currentIndexChanged.connect(self.update_room_custom)

        room_label = QLabel('机房')
        self.room_edit = QComboBox()
        self.room_edit.setEditable(True)
       # self.room_edit.addItems(self.get_data('room'))

        custom_label = QLabel('客户')
        self.custom_edit = QComboBox()
        self.custom_edit.setEditable(True)
        #self.custom_edit.addItems(self.get_data('custom'))

        ip_label = QLabel('IP')
        self.ip_edit = QLineEdit()

        operator_label = QLabel('运营商')
        self.operator_edit = QComboBox()
        self.operator_edit.setEditable(True)
        self.operator_edit.addItems(self.get_data('operator'))

        submit_button = QPushButton('提交')
        submit_button.clicked.connect(self.submit)

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
        description = room + '-' + custom + '-' + ip + '-' + operator
        sql = "INSERT INTO  mtr_company (ip, region, room, custom, operator, description) VALUES (%s, %s, %s, %s, %s, %s)"
        # 更新数据库
        try:
            #self.cursor.execute(f"UPDATE mtr_company SET region='{region}', room='{room}', custom='{custom}', operator='{operator}' WHERE ip='{ip}'")
            self.cursor.execute(sql, (ip, region, room, custom, operator, description))
            self.conn.commit()
            QMessageBox.information(self, '提示', '更新成功')
        except Exception as e:
            print(e)
            QMessageBox.warning(self, '警告', '更新失败')

if __name__ == '__main__':
    app = QApplication([])
    main = Main()
    main.show()
    sys.exit(app.exec())
