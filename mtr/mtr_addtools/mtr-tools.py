import sys
from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox
from PyQt6.QtCore import QRegularExpression,QTimer
from PyQt6.QtGui import QRegularExpressionValidator,QIcon
import configparser
import pymysql



class Main(QWidget):
    def __init__(self):
        super().__init__()
        
        #读配置文件
        config = configparser.ConfigParser()
        config.read('mtr\mtr_addtools\mtr.conf')

        host = config['database']['host']
        user = config['database']['user']
        password = config['database']['password']  
        db = config['database']['db']
        # 连接数据库
        self.conn = pymysql.connect(host=host, port=3306, user=user, password=password, database=db, connect_timeout=300)
        self.cursor = self.conn.cursor()
        
        # 初始化界面
        self.initUI()

    def initUI(self):
        self.combo_box_style = """
        QComboBox {
            border: 1px solid gray;
            border-radius: 4px;
            padding: 1px 18px 1px 3px;
            min-width: 6em;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 15px;
            border-left-width: 1px;
            border-left-color: darkgray;
            border-left-style: solid;
            border-top-right-radius: 3px;
            border-bottom-right-radius: 3px;
        }
        QComboBox::down-arrow {
            image: url(./down_arrow.png);
            width: 10px;
            height: 10px;
        }"""
        

        # 设置窗口标题和大小
        self.setWindowTitle('MTR更新')
        self.setWindowIcon(QIcon('./icon.png'))
        self.resize(400, 300)

        # 设置窗口背景色和字体颜色
        self.setStyleSheet("background-color: #F5F5F5; color: #333333; font-family: Microsoft YaHei; font-size: 15px;")

        # 创建控件
        region_label = QLabel('地区')
        self.region_edit = QComboBox()
        self.region_edit.setEditable(True)
        self.region_edit.addItems(self.get_data('region'))
        self.region_edit.currentIndexChanged.connect(self.update_room_custom)
        self.region_edit.setStyleSheet(self.combo_box_style)
        
        room_label = QLabel('机房')
        self.room_edit = QComboBox()
        self.room_edit.setEditable(True)
        self.room_edit.setStyleSheet(self.combo_box_style)
        
        custom_label = QLabel('客户')
        self.custom_edit = QComboBox()
        self.custom_edit.setEditable(True)
        self.custom_edit.setStyleSheet(self.combo_box_style)
        
        ip_label = QLabel('IP')
        self.ip_edit = QLineEdit()
        ip_reg = QRegularExpression("^([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\."
                        "([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\."
                        "([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\."
                        "([01]?\\d\\d?|2[0-4]\\d|25[0-5])$")
        ip_validator = QRegularExpressionValidator(ip_reg, self.ip_edit)
        self.ip_edit.setValidator(ip_validator)
        self.ip_edit.setStyleSheet("QLineEdit { border: 1px solid gray; border-radius: 4px; padding: 1px 18px 1px 3px; min-width: 6em; }")

        

        operator_label = QLabel('运营商')
        self.operator_edit = QComboBox()
        self.operator_edit.setEditable(True)
        self.operator_edit.addItems(self.get_data('operator'))
        self.operator_edit.setStyleSheet(self.combo_box_style)
        
        submit_button = QPushButton('提交')
        submit_button.clicked.connect(self.submit)
        submit_button.setStyleSheet("QPushButton { border: 1px solid gray; border-radius: 4px; padding: 1px 5px; min-width: 8em; background-color: #0A81F3; color: #FFFFFF; } QPushButton:hover { background-color: #0A81F3; }")

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
        
        # 检查输入的信息
        if not region:
            QMessageBox.warning(self, '警告', '地区不能为空')
            return
        query_region = self.cursor.execute(f"SELECT region FROM mtr_company WHERE region LIKE '%{region}%' GROUP BY region")
        self.cursor.execute(f"SELECT region FROM mtr_company WHERE region LIKE '%{region[:2]}%' GROUP BY region")
        similar_region = self.cursor.fetchall()
        similar_region_result =[ str(result)[2:7] for result in similar_region ]
        print(similar_region_result)
        if not query_region:
            reply = QMessageBox.question(self, "Question", f"数据库里已有类似地区{similar_region_result}, 继续添加 {region}吗？", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
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
        query_ip = self.cursor.execute(f"SELECT * FROM mtr_company WHERE ip='{ip}'")
        if query_ip:
            QMessageBox.warning(self, '警告', '该IP地址已存在')
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
    QMessageBox.warning(main, '提示', '自用节点选择地区“自用地区”')
    sys.exit(app.exec())
