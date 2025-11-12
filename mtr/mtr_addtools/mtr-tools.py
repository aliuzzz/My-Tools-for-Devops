import sys
import os
import pymysql
import configparser
from PyQt6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QComboBox, QListWidget
)
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator, QIcon


class DBHelper:
    """数据库操作封装类"""
    def __init__(self, config_path):
        config = configparser.ConfigParser()
        config.read(config_path, encoding='utf-8')

        self.conn = pymysql.connect(
            host=config['database']['host'],
            port=3306,
            user=config['database']['user'],
            password=config['database']['password'],
            database=config['database']['db'],
            connect_timeout=300
        )
        self.cursor = self.conn.cursor()

    def get_distinct(self, field, table='mtr_company'):
        self.cursor.execute(f"SELECT DISTINCT {field} FROM {table}")
        return [row[0] for row in self.cursor.fetchall() if row[0]]

    def get_by_condition(self, field, cond_field, cond_value, table='mtr_company'):
        sql = f"SELECT DISTINCT {field} FROM {table} WHERE {cond_field} = %s"
        self.cursor.execute(sql, (cond_value,))
        return [row[0] for row in self.cursor.fetchall() if row[0]]

    def get_ips(self, region, room, custom):
        sql = """SELECT ip FROM mtr_company
                 WHERE region=%s AND room=%s AND custom=%s"""
        self.cursor.execute(sql, (region, room, custom))
        return [row[0] for row in self.cursor.fetchall() if row[0]]

    def ip_exists(self, ip):
        self.cursor.execute("SELECT COUNT(*) FROM mtr_company WHERE ip = %s", (ip,))
        return self.cursor.fetchone()[0] > 0

    def region_exists(self, region_prefix):
        sql = "SELECT region FROM mtr_company WHERE region LIKE %s GROUP BY region"
        self.cursor.execute(sql, (f"%{region_prefix}%",))
        return [row[0] for row in self.cursor.fetchall()]

    def insert_record(self, ip, region, room, custom, operator, description):
        sql = """
            INSERT INTO mtr_company (ip, region, room, custom, operator, description)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(sql, (ip, region, room, custom, operator, description))
        self.conn.commit()

    def delete_ip(self, ip):
        """删除指定 IP 的记录"""
        sql = "DELETE FROM mtr_company WHERE ip = %s"
        self.cursor.execute(sql, (ip,))
        self.conn.commit()


class Main(QWidget):
    def __init__(self):
        super().__init__()

        config_path = os.path.join(os.getcwd(), 'mtr', 'mtr_addtools', 'mtr.conf')
        self.db = DBHelper(config_path)

        # 初始化界面
        self.initUI()

    def initUI(self):
        # 样式统一
        combo_style = """
        QComboBox {
            border: 1px solid gray;
            border-radius: 4px;
            padding: 3px 18px 3px 6px;
            min-width: 6em;
        }
        """
        line_edit_style = "QLineEdit { border: 1px solid gray; border-radius: 4px; padding: 3px; }"
        button_style = """
        QPushButton {
            border: 1px solid gray;
            border-radius: 4px;
            padding: 4px 12px;
            background-color: #0A81F3;
            color: white;
        }
        QPushButton:hover { background-color: #0A6Fd3; }
        """

        self.setWindowTitle('MTR更新')
        icon_path = os.path.join(os.getcwd(), 'icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.resize(450, 400)
        self.setStyleSheet("background-color: #F5F5F5; color: #333333; font-family: 'Microsoft YaHei'; font-size: 14px;")

        # 控件创建
        region_label = QLabel('地区')
        self.region_edit = QComboBox()
        self.region_edit.setEditable(True)
        self.region_edit.addItems(self.db.get_distinct('region'))
        self.region_edit.setStyleSheet(combo_style)
        self.region_edit.currentIndexChanged.connect(self.update_room)

        room_label = QLabel('机房')
        self.room_edit = QComboBox()
        self.room_edit.setEditable(True)
        self.room_edit.setStyleSheet(combo_style)
        self.room_edit.currentIndexChanged.connect(self.update_custom)

        custom_label = QLabel('客户')
        self.custom_edit = QComboBox()
        self.custom_edit.setEditable(True)
        self.custom_edit.setStyleSheet(combo_style)
        self.custom_edit.currentIndexChanged.connect(self.update_ip_list)  # 当客户变化时更新 IP 列表

        ip_label = QLabel('IP')
        self.ip_edit = QLineEdit()
        ip_reg = QRegularExpression("^([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\."
                                    "([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\."
                                    "([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\."
                                    "([01]?\\d\\d?|2[0-4]\\d|25[0-5])$")
        self.ip_edit.setValidator(QRegularExpressionValidator(ip_reg, self.ip_edit))
        self.ip_edit.setStyleSheet(line_edit_style)

        operator_label = QLabel('运营商')
        self.operator_edit = QComboBox()
        self.operator_edit.setEditable(True)
        self.operator_edit.addItems(self.db.get_distinct('operator'))
        self.operator_edit.setStyleSheet(combo_style)

        submit_button = QPushButton('提交')
        submit_button.setStyleSheet(button_style)
        submit_button.clicked.connect(self.submit)

        # 🌟 新增部分：显示 IP 列表 + 删除按钮
        ip_list_label = QLabel('该客户的 IP 列表')
        self.ip_list = QListWidget()
        self.delete_button = QPushButton('删除选中 IP')
        self.delete_button.setStyleSheet(button_style)
        self.delete_button.clicked.connect(self.delete_selected_ip)

        # 布局
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(region_label, 0, 0)
        grid.addWidget(self.region_edit, 0, 1)
        grid.addWidget(room_label, 1, 0)
        grid.addWidget(self.room_edit, 1, 1)
        grid.addWidget(custom_label, 2, 0)
        grid.addWidget(self.custom_edit, 2, 1)
        grid.addWidget(ip_label, 3, 0)
        grid.addWidget(self.ip_edit, 3, 1)
        grid.addWidget(operator_label, 4, 0)
        grid.addWidget(self.operator_edit, 4, 1)
        grid.addWidget(submit_button, 5, 1)

        # 新区域（IP显示 & 删除）
        grid.addWidget(ip_list_label, 6, 0)
        grid.addWidget(self.ip_list, 6, 1)
        grid.addWidget(self.delete_button, 7, 1)

        self.setLayout(grid)

    def update_room(self):
        region = self.region_edit.currentText().strip()
        self.room_edit.clear()
        self.room_edit.addItems([''])
        if region:
            self.room_edit.addItems(self.db.get_by_condition('room', 'region', region))
        self.custom_edit.clear()
        self.ip_list.clear()

    def update_custom(self):
        room = self.room_edit.currentText().strip()
        self.custom_edit.clear()
        self.custom_edit.addItems([''])
        if room:
            self.custom_edit.addItems(self.db.get_by_condition('custom', 'room', room))
        self.ip_list.clear()

    def update_ip_list(self):
        """当地区、机房、客户都确定后更新对应 IP 列表"""
        region = self.region_edit.currentText().strip()
        room = self.room_edit.currentText().strip()
        custom = self.custom_edit.currentText().strip()

        self.ip_list.clear()
        if region and room and custom:
            ips = self.db.get_ips(region, room, custom)
            self.ip_list.addItems(ips)

    def delete_selected_ip(self):
        """删除选中的 IP"""
        selected_item = self.ip_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, '警告', '请先选择一个 IP')
            return

        ip = selected_item.text()
        reply = QMessageBox.question(
            self, '确认删除',
            f'确定删除 IP {ip} 吗？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.delete_ip(ip)
                QMessageBox.information(self, '提示', f'{ip} 删除成功')
                self.update_ip_list()  # 刷新IP列表
            except Exception as e:
                print(e)
                QMessageBox.warning(self, '错误', f'删除失败：{e}')

    def submit(self):
        region = self.region_edit.currentText().strip()
        room = self.room_edit.currentText().strip()
        custom = self.custom_edit.currentText().strip()
        ip = self.ip_edit.text().strip()
        operator = self.operator_edit.currentText().strip()

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

        # 相似地区提示
        if not self.db.region_exists(region):
            similar_regions = self.db.region_exists(region[:2])
            if similar_regions:
                reply = QMessageBox.question(
                    self,
                    "疑似相似地区",
                    f"数据库中已存在类似地区 {similar_regions}，是否继续添加 {region}？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return

        if self.db.ip_exists(ip):
            QMessageBox.warning(self, '警告', '该 IP 地址已存在')
            return

        description = f"{room}-{custom}-{ip}-{operator}"
        try:
            self.db.insert_record(ip, region, room, custom, operator, description)
            QMessageBox.information(self, '提示', '更新成功')
            self.update_ip_list()  # 插入后刷新列表
        except Exception as e:
            print(e)
            QMessageBox.warning(self, '警告', f'更新失败：{e}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Main()
    main.show()
    QMessageBox.information(main, '提示', '自用节点请选择地区 “自用地区”')
    sys.exit(app.exec())