import sys
import os
import json
import configparser
import yaml

try:
    import requests
except ImportError:
    requests = None

import pymysql
from PyQt6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QComboBox, QListWidget, QTabWidget, QVBoxLayout,
    QFileDialog, QTextEdit, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QCheckBox, QHeaderView, QGroupBox
)
from PyQt6.QtCore import QRegularExpression, Qt
from PyQt6.QtGui import QRegularExpressionValidator, QIcon


__version__ = "1.0.0"


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

    def get_distinct(self, field, table='mtr_company_copy1'):
        self.cursor.execute(f"SELECT DISTINCT {field} FROM {table}")
        return [row[0] for row in self.cursor.fetchall() if row[0]]

    def get_operators(self):
        """从 operator 表获取所有运营商，返回 {id: name} 字典"""
        self.cursor.execute("SELECT id, o_name FROM mtr_operator ORDER BY id")
        return {row[0]: row[1] for row in self.cursor.fetchall()}

    def get_ip_types(self):
        """从 mtr_type 表获取所有类型 {id: display_name}"""
        self.cursor.execute("SELECT id, type FROM mtr_type ORDER BY id")
        result = {}
        for row in self.cursor.fetchall():
            if row[1] == "idc":
                result[row[0]] = "IDC"
            elif row[1] == "high_security":
                result[row[0]] = "高防"
            else:
                result[row[0]] = row[1]
        return result

    def get_by_condition(self, field, cond_field, cond_value, table='mtr_company_copy1'):
        sql = f"SELECT DISTINCT {field} FROM {table} WHERE {cond_field} = %s"
        self.cursor.execute(sql, (cond_value,))
        return [row[0] for row in self.cursor.fetchall() if row[0]]

    def get_ips(self, region, room, custom):
        sql = """SELECT ip FROM mtr_company_copy1
                 WHERE region=%s AND room=%s AND custom=%s"""
        self.cursor.execute(sql, (region, room, custom))
        return [row[0] for row in self.cursor.fetchall() if row[0]]

    def ip_exists(self, ip):
        self.cursor.execute("SELECT COUNT(*) FROM mtr_company_copy1 WHERE ip = %s", (ip,))
        return self.cursor.fetchone()[0] > 0

    def region_exists(self, region_prefix):
        sql = "SELECT region FROM mtr_company_copy1 WHERE region LIKE %s GROUP BY region"
        self.cursor.execute(sql, (f"%{region_prefix}%",))
        return [row[0] for row in self.cursor.fetchall()]

    def insert_record(self, ip, region, room, custom, operator_id, ip_type_id, description):
        sql = """
            INSERT INTO mtr_company_copy1 
            (ip, region, room, custom, operator_id, type_id, description, d_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        """
        self.cursor.execute(sql, (ip, region, room, custom, operator_id, ip_type_id, description))
        self.conn.commit()

    def delete_ip(self, ip):
        """删除指定 IP 的记录"""
        sql = "DELETE FROM mtr_company_copy1 WHERE ip = %s"
        self.cursor.execute(sql, (ip,))
        self.conn.commit()

    def get_nodes(self):
        """获取mtr_node表的所有节点信息"""
        self.cursor.execute("SELECT name, host, if_gaofang FROM mtr_node")
        return self.cursor.fetchall()

    def get_customs_and_ips(self):
        """获取mtr_company_copy1表的custom和ip信息"""
        self.cursor.execute("SELECT custom, ip, type_id FROM mtr_company_copy1")
        return self.cursor.fetchall()


class Main(QWidget):
    def __init__(self):
        super().__init__()

        config_path = os.path.join(os.getcwd(), 'mtr', 'mtr_addtools', 'mtr.conf')
        self.db = DBHelper(config_path)

        # 检查版本一致性，失败则退出
        if not self.check_version_consistency():
            sys.exit(0)

        self.operators = self.db.get_operators()
        self.ip_types = self.db.get_ip_types()

        self.initUI()

    def check_version_consistency(self):
        """
        检查本地版本与数据库 mtr_version 表中的 version 是否一致。
        返回 True 表示一致，False 表示不一致（需退出）。
        """
        try:
            self.db.cursor.execute("SELECT version FROM mtr_add_version LIMIT 1")
            result = self.db.cursor.fetchone()

            if not result:
                QMessageBox.critical(
                    self,
                    "数据库错误",
                    "数据库中未找到版本信息（mtr_version 表为空）！\n请检查数据库结构。"
                )
                return False

            db_version = str(result[0]).strip()

            if db_version != __version__:
                QMessageBox.warning(
                    self,
                    "版本不匹配",
                    f"当前本地版本：{__version__}\n"
                    f"数据库要求版本：{db_version}\n\n"
                    "请更新应用程序后再使用！"
                )
                return False

            return True

        except Exception as e:
            QMessageBox.critical(
                self,
                "版本检查失败",
                f"无法读取数据库版本信息：\n{str(e)}"
            )
            return False

    def initUI(self):
        self.setWindowTitle(f'MTR更新 v{__version__}')

        icon_path = os.path.join(os.getcwd(), 'icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.resize(900, 700)
        self.setStyleSheet("background-color: #F5F5F5; color: #333333; font-family: 'Microsoft YaHei'; font-size: 14px;")

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabs.setDocumentMode(True)

        self.add_tab = QWidget()
        self.grafana_tab = QWidget()

        self.tabs.addTab(self.add_tab, "添加 MTR")
        self.tabs.addTab(self.grafana_tab, "配置生成")

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

        self.setup_add_tab()
        self.setup_grafana_tab()

    def setup_add_tab(self):
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

        # 地区
        region_label = QLabel('地区')
        self.region_edit = QComboBox()
        self.region_edit.setEditable(True)
        self.region_edit.addItems(self.db.get_distinct('region'))
        self.region_edit.setStyleSheet(combo_style)
        self.region_edit.currentIndexChanged.connect(self.update_room)

        # 机房
        room_label = QLabel('机房')
        self.room_edit = QComboBox()
        self.room_edit.setEditable(True)
        self.room_edit.setStyleSheet(combo_style)
        self.room_edit.currentIndexChanged.connect(self.update_custom)

        # 客户
        custom_label = QLabel('客户')
        self.custom_edit = QComboBox()
        self.custom_edit.setEditable(True)
        self.custom_edit.setStyleSheet(combo_style)
        self.custom_edit.currentIndexChanged.connect(self.update_ip_list)

        # IP
        ip_label = QLabel('IP')
        self.ip_edit = QLineEdit()
        ip_reg = QRegularExpression("^([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\."
                                    "([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\."
                                    "([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\."
                                    "([01]?\\d\\d?|2[0-4]\\d|25[0-5])$")
        self.ip_edit.setValidator(QRegularExpressionValidator(ip_reg, self.ip_edit))
        self.ip_edit.setStyleSheet(line_edit_style)

        # 运营商
        operator_label = QLabel('运营商')
        self.operator_edit = QComboBox()
        for op_id, op_name in self.operators.items():
            self.operator_edit.addItem(op_name, op_id)
        self.operator_edit.setStyleSheet(combo_style)

        # IP 类型
        iptype_label = QLabel("IP类型")
        self.iptype_edit = QComboBox()
        for type_id, display_name in self.ip_types.items():
            self.iptype_edit.addItem(display_name, type_id)
        self.iptype_edit.setStyleSheet(combo_style)

        # 提交
        submit_button = QPushButton('提交')
        submit_button.setStyleSheet(button_style)
        submit_button.clicked.connect(self.submit)

        # IP 列表
        ip_list_label = QLabel('该客户的 IP 列表')
        self.ip_list = QListWidget()

        self.delete_button = QPushButton('删除选中 IP')
        self.delete_button.setStyleSheet(button_style)
        self.delete_button.clicked.connect(self.delete_selected_ip)

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

        grid.addWidget(iptype_label, 5, 0)
        grid.addWidget(self.iptype_edit, 5, 1)

        grid.addWidget(submit_button, 6, 1)

        grid.addWidget(ip_list_label, 7, 0)
        grid.addWidget(self.ip_list, 7, 1)
        grid.addWidget(self.delete_button, 8, 1)

        self.add_tab.setLayout(grid)

    def setup_grafana_tab(self):
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

        layout = QVBoxLayout()
        layout.setSpacing(10)

        # 节点表格
        nodes_group = QGroupBox("节点列表")
        nodes_layout = QVBoxLayout()
        
        self.nodes_table = QTableWidget()
        self.nodes_table.setColumnCount(4)
        self.nodes_table.setHorizontalHeaderLabels(["选择", "节点名", "IP地址", "是否高防"])
        header = self.nodes_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        nodes_layout.addWidget(self.nodes_table)
        nodes_group.setLayout(nodes_layout)
        
        # 类型选择
        type_group = QGroupBox("监控类型")
        type_layout = QHBoxLayout()
        
        self.mtr_checkbox = QCheckBox("MTR")
        self.mtr_checkbox.setChecked(True)
        self.icmp_checkbox = QCheckBox("ICMP")
        self.tcp_checkbox = QCheckBox("TCP")
        
        type_layout.addWidget(self.mtr_checkbox)
        type_layout.addWidget(self.icmp_checkbox)
        type_layout.addWidget(self.tcp_checkbox)
        
        # 高防监控类型选择
        high_defense_label = QLabel("高防监控类型:")
        self.high_defense_combo = QComboBox()
        self.high_defense_combo.addItems(["无", "MTR", "ICMP", "TCP"])
        self.high_defense_combo.setCurrentIndex(0)
        
        high_defense_layout = QHBoxLayout()
        high_defense_layout.addWidget(high_defense_label)
        high_defense_layout.addWidget(self.high_defense_combo)
        
        # 端口号输入
        port_label = QLabel("端口号:")
        self.port_edit = QLineEdit()
        self.port_edit.setPlaceholderText("例如: 443")
        self.port_edit.setValidator(QRegularExpressionValidator(QRegularExpression(r"^\d{1,5}$"), self.port_edit))
        
        port_layout = QHBoxLayout()
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.port_edit)
        
        type_layout.addLayout(high_defense_layout)
        type_layout.addLayout(port_layout)
        type_group.setLayout(type_layout)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.load_nodes_button = QPushButton("加载节点")
        self.load_nodes_button.setStyleSheet(button_style)
        self.load_nodes_button.clicked.connect(self.load_nodes)
        
        self.generate_yaml_button = QPushButton("生成YAML配置")
        self.generate_yaml_button.setStyleSheet(button_style)
        self.generate_yaml_button.clicked.connect(self.generate_yaml)
        
        self.save_yaml_button = QPushButton("保存YAML文件")
        self.save_yaml_button.setStyleSheet(button_style)
        self.save_yaml_button.clicked.connect(self.save_yaml)
        
        button_layout.addWidget(self.load_nodes_button)
        button_layout.addWidget(self.generate_yaml_button)
        button_layout.addWidget(self.save_yaml_button)
        
        # YAML显示区域
        yaml_label = QLabel("生成的YAML配置:")
        self.yaml_display = QTextEdit()
        self.yaml_display.setReadOnly(True)
        
        layout.addWidget(nodes_group)
        layout.addWidget(type_group)
        layout.addLayout(button_layout)
        layout.addWidget(yaml_label)
        layout.addWidget(self.yaml_display)
        
        self.grafana_tab.setLayout(layout)

    def load_nodes(self):
        try:
            nodes = self.db.get_nodes()
            self.nodes_table.setRowCount(len(nodes))
            
            for i, (name, host, if_gaofang) in enumerate(nodes):
                # 选择框
                checkbox = QCheckBox()
                self.nodes_table.setCellWidget(i, 0, checkbox)
                
                # 节点名
                name_item = QTableWidgetItem(name)
                self.nodes_table.setItem(i, 1, name_item)
                
                # IP地址
                host_item = QTableWidgetItem(host)
                self.nodes_table.setItem(i, 2, host_item)
                
                # 是否高防
                gaofang_text = "是" if if_gaofang == 1 else "否"
                gaofang_item = QTableWidgetItem(gaofang_text)
                self.nodes_table.setItem(i, 3, gaofang_item)
                
        except Exception as e:
            QMessageBox.warning(self, "加载失败", f"无法加载节点信息：{e}")

    def generate_yaml(self):
        try:
            # 读取配置文件
            config_path = os.path.join(os.getcwd(), 'mtr', 'mtr_addtools', 'mtr.conf')
            config = configparser.ConfigParser()
            config.read(config_path, encoding='utf-8')
            
            # 构建YAML配置 - 使用有序字典确保顺序
            yaml_config = {}
            
            # conf部分
            if config.has_section('default'):
                yaml_config['conf'] = {
                    'refresh': config.get('default', 'refresh', fallback='15m'),
                    'nameserver_timeout': config.get('default', 'nameserver_timeout', fallback='250ms')
                }
            
            # icmp部分
            if config.has_section('icmp'):
                yaml_config['icmp'] = {
                    'interval': config.get('icmp', 'interval', fallback='30s'),
                    'timeout': config.get('icmp', 'timeout', fallback='0.5s'),
                    'count': config.getint('icmp', 'count', fallback=10)
                }
            
            # mtr部分
            if config.has_section('mtr'):
                yaml_config['mtr'] = {
                    'interval': config.get('mtr', 'interval', fallback='60s'),
                    'timeout': config.get('mtr', 'timeout', fallback='500ms'),
                    'max-hops': config.getint('mtr', 'max-hops', fallback=30),
                    'count': config.getint('mtr', 'count', fallback=10)
                }
            
            # tcp部分
            if config.has_section('tcp'):
                yaml_config['tcp'] = {
                    'interval': config.get('tcp', 'interval', fallback='3s'),
                    'timeout': config.get('tcp', 'timeout', fallback='1s')
                }
            
            # http_get部分
            if config.has_section('http_get'):
                yaml_config['http_get'] = {
                    'interval': config.get('http_get', 'interval', fallback='15m'),
                    'timeout': config.get('http_get', 'timeout', fallback='5s')
                }
            
            # targets部分
            targets = []
            
            # 获取选中的节点
            selected_nodes = []
            for i in range(self.nodes_table.rowCount()):
                checkbox = self.nodes_table.cellWidget(i, 0)
                if checkbox.isChecked():
                    name = self.nodes_table.item(i, 1).text()
                    host = self.nodes_table.item(i, 2).text()
                    is_high_defense = self.nodes_table.item(i, 3).text() == "是"
                    selected_nodes.append((name, host, is_high_defense))
            
            # 获取所有客户和IP信息
            customs_ips = self.db.get_customs_and_ips()
            
            # 构建targets
            for node_name, node_host, is_high_defense in selected_nodes:
                for custom, ip, type_id in customs_ips:
                    target_name = f"{node_name}->{custom}-{ip}"
                    
                    # 确定监控类型
                    types = []
                    if self.mtr_checkbox.isChecked():
                        types.append('MTR')
                    if self.icmp_checkbox.isChecked():
                        types.append('ICMP')
                    if self.tcp_checkbox.isChecked():
                        types.append('TCP')
                    
                    # 如果没有勾选任何类型，则跳过
                    if types:
                        # 拼接类型
                        type_str = '+'.join(types)
                        
                        target = {
                            'name': target_name,
                            'host': ip,
                            'type': type_str
                        }
                        
                        targets.append(target)
                    
                    # 如果是高防节点且type_id为3，且选择了高防监控类型
                    high_defense_type = self.high_defense_combo.currentText()
                    port = self.port_edit.text().strip()
                    
                    if is_high_defense and type_id == 3 and high_defense_type != "无" and port:
                        high_defense_name = f"{node_name}-->{custom}-高防-{ip}"
                        high_defense_target = {
                            'name': high_defense_name,
                            'host': f"{ip}:{port}",
                            'type': high_defense_type
                        }
                        
                        targets.append(high_defense_target)
            
            yaml_config['targets'] = targets
            
            # 手动构建YAML字符串以确保正确的顺序
            yaml_str = ""
            
            # conf部分
            if 'conf' in yaml_config:
                yaml_str += "conf:\n"
                for key, value in yaml_config['conf'].items():
                    yaml_str += f"  {key}: {value}\n"
            
            # icmp部分
            if 'icmp' in yaml_config:
                yaml_str += "icmp:\n"
                for key, value in yaml_config['icmp'].items():
                    if isinstance(value, int):
                        yaml_str += f"  {key}: {value}\n"
                    else:
                        yaml_str += f"  {key}: {value}\n"
            
            # mtr部分
            if 'mtr' in yaml_config:
                yaml_str += "mtr:\n"
                for key, value in yaml_config['mtr'].items():
                    if isinstance(value, int):
                        yaml_str += f"  {key}: {value}\n"
                    else:
                        yaml_str += f"  {key}: {value}\n"
            
            # tcp部分
            if 'tcp' in yaml_config:
                yaml_str += "tcp:\n"
                for key, value in yaml_config['tcp'].items():
                    if isinstance(value, int):
                        yaml_str += f"  {key}: {value}\n"
                    else:
                        yaml_str += f"  {key}: {value}\n"
            
            # http_get部分
            if 'http_get' in yaml_config:
                yaml_str += "http_get:\n"
                for key, value in yaml_config['http_get'].items():
                    if isinstance(value, int):
                        yaml_str += f"  {key}: {value}\n"
                    else:
                        yaml_str += f"  {key}: {value}\n"
            
            # targets部分
            if 'targets' in yaml_config:
                yaml_str += "targets:\n"
                for target in yaml_config['targets']:
                    yaml_str += f"- host: {target['host']}\n"
                    yaml_str += f"  name: {target['name']}\n"
                    yaml_str += f"  type: {target['type']}\n"
            
            self.yaml_display.setText(yaml_str)
            
        except Exception as e:
            QMessageBox.warning(self, "生成失败", f"无法生成YAML配置：{e}")

    def save_yaml(self):
        if not self.yaml_display.toPlainText().strip():
            QMessageBox.warning(self, "提示", "请先生成YAML配置")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, "保存YAML文件", "", "YAML文件 (*.yml *.yaml);;所有文件 (*)")
        if not file_path:
            return
            
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.yaml_display.toPlainText())
            QMessageBox.information(self, "成功", f"YAML配置已保存到 {file_path}")
        except Exception as e:
            QMessageBox.warning(self, "保存失败", f"无法保存文件：{e}")

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
        region = self.region_edit.currentText().strip()
        room = self.room_edit.currentText().strip()
        custom = self.custom_edit.currentText().strip()

        self.ip_list.clear()
        if region and room and custom:
            ips = self.db.get_ips(region, room, custom)
            self.ip_list.addItems(ips)

    def delete_selected_ip(self):
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
                self.update_ip_list()
            except Exception as e:
                QMessageBox.warning(self, '错误', f'删除失败：{e}')

    def submit(self):
        region = self.region_edit.currentText().strip()
        room = self.room_edit.currentText().strip()
        custom = self.custom_edit.currentText().strip()
        ip = self.ip_edit.text().strip()
        operator_id = self.operator_edit.currentData()
        operator_name = self.operator_edit.currentText()

        ip_type_id = self.iptype_edit.currentData()
        ip_type_name = self.iptype_edit.currentText()

        if not region or not room or not custom or not ip:
            QMessageBox.warning(self, '警告', '请填写完整信息')
            return

        if not self.db.region_exists(region):
            similar = self.db.region_exists(region[:2])
            if similar:
                reply = QMessageBox.question(
                    self,
                    "疑似相似地区",
                    f"数据库中已存在类似地区 {similar}，是否继续添加 {region}？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return

        if self.db.ip_exists(ip):
            QMessageBox.warning(self, '警告', '该 IP 地址已存在')
            return

        description = f"{room}-{custom}-{ip}-{operator_name}-{ip_type_name}"
        try:
            self.db.insert_record(ip, region, room, custom, operator_id, ip_type_id, description)
            QMessageBox.information(self, '提示', '更新成功')
            self.update_ip_list()
        except Exception as e:
            QMessageBox.warning(self, '警告', f'更新失败：{e}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Main()
    main.show()
    QMessageBox.information(main, '提示', '自用节点请选择地区 "自用地区"')
    sys.exit(app.exec())